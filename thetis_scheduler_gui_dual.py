import socket
import time
import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import schedule
import logging
from datetime import datetime
import traceback

# Configuration
CAT_SERVER_HOST = "127.0.0.1"
CAT_SERVER_PORT = 50001  # TS-2000 CAT port
SAMPLE_RATE = 44100
VAC_DEVICE = "Line 3 (Virtual Audio Cable)"

# Band plan for mode defaults
BAND_MODES = {
    "160m": "LSB",
    "80m": "LSB",
    "40m": "LSB",
    "30m": "USB",
    "20m": "USB",
    "17m": "USB",
    "15m": "USB",
    "12m": "USB",
    "10m": "USB"
}

# Setup logging
try:
    logging.basicConfig(
        filename="scheduler.log",
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logging.info("Logging initialized")
    print("Logging initialized to scheduler.log")
except Exception as e:
    print(f"Failed to initialize logging: {e}")
    logging.basicConfig(level=logging.DEBUG)  # Fallback to console logging

# Thread lock for CAT commands
cat_lock = threading.Lock()

def send_cat_command(command, retries=3, delay=0.5):
    """Send a CAT command to TS-2000 and return the response."""
    logging.debug(f"Sending CAT command: {command}")
    for attempt in range(retries):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3)
                s.connect((CAT_SERVER_HOST, CAT_SERVER_PORT))
                s.sendall(command.encode())
                time.sleep(0.2)
                response = s.recv(1024).decode().strip()
                logging.debug(f"Received response: {response}")
                return response
        except Exception as e:
            logging.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
            continue
    logging.error(f"Failed to send CAT command after {retries} attempts: {command}")
    return None

def set_frequency_and_mode(freq_hz, mode):
    """Set the frequency and mode on TS-2000."""
    with cat_lock:
        try:
            freq_str = f"{int(freq_hz):011d}"
            freq_command = f"FA{freq_str};"
            mode_command = "MD2;" if mode.upper() == "USB" else "MD1;"
            
            logging.info(f"Setting frequency: {freq_hz} Hz")
            response = send_cat_command(freq_command)
            if response is None:
                logging.error("Frequency command failed")
                return False
            
            time.sleep(1.5)
            
            logging.info(f"Setting mode: {mode}")
            response = send_cat_command(mode_command)
            if response is None:
                logging.error("Mode command failed")
                return False
            
            return True
        except Exception as e:
            logging.error(f"Error in set_frequency_and_mode: {e}\n{traceback.format_exc()}")
            return False

def load_schedules():
    """Load schedules from schedules.json."""
    try:
        with open("schedules.json", "r") as f:
            schedules = json.load(f)
            logging.info("Loaded schedules from JSON")
            return schedules
    except FileNotFoundError:
        logging.warning("schedules.json not found, returning empty list")
        return []
    except Exception as e:
        logging.error(f"Error loading schedules: {e}\n{traceback.format_exc()}")
        return []

def save_schedules(schedules):
    """Save schedules to schedules.json."""
    try:
        with open("schedules.json", "w") as f:
            json.dump(schedules, f, indent=4)
        logging.info("Schedules saved to JSON")
    except Exception as e:
        logging.error(f"Error saving schedules: {e}\n{traceback.format_exc()}")

def run_schedule():
    """Run the scheduler in a separate thread."""
    try:
        logging.info("Scheduler thread started")
        while scheduler_running:
            schedule.run_pending()
            time.sleep(1)
        logging.info("Scheduler thread stopped")
    except Exception as e:
        logging.error(f"Error in run_schedule: {e}\n{traceback.format_exc()}")
        print(f"Error in scheduler thread: {e}")

def apply_schedule(freq_hz, mode, time_str, days, rx="RX1"):
    """Apply a schedule by setting frequency, mode, and RX."""
    logging.info(f"Applying schedule: {freq_hz} Hz, {mode}, {time_str}, {days}, {rx}")
    with cat_lock:
        try:
            freq_str = f"{int(freq_hz):011d}"
            if rx == "RX2":
                freq_command = f"FB{freq_str};"  # VFO B
                rx_switch = "FR1;"               # Select RX2
            else:
                freq_command = f"FA{freq_str};"  # VFO A
                rx_switch = "FR0;"               # Select RX1 (optional)

            mode_command = "MD2;" if mode.upper() == "USB" else "MD1;"

            # Set frequency
            response = send_cat_command(freq_command)
            if not response:
                logging.error("Frequency command failed")
                return False
            time.sleep(1.5)

            # Set mode
            response = send_cat_command(mode_command)
            if not response:
                logging.error("Mode command failed")
                return False
            time.sleep(0.5)

            # Switch RX
            response = send_cat_command(rx_switch)
            if not response:
                logging.error("RX switch failed")
                return False

            logging.info(f"Successfully set {rx}: {freq_hz/1e6} MHz, {mode}")
            return True
        except Exception as e:
            logging.error(f"Error in apply_schedule: {e}\n{traceback.format_exc()}")
            return False

def create_schedule(freq, mode, time_str, days, rx="RX1"):
    """Create a schedule for frequency, mode, and RX change."""
    try:
        freq_hz = int(float(freq) * 1_000_000)
        if not mode:
            f = float(freq)
            band = None
            if 1.8 <= f <= 2.0:
                band = "160m"
            elif 3.5 <= f <= 4.0:
                band = "80m"
            elif 7.0 <= f <= 7.3:
                band = "40m"
            elif 10.1 <= f <= 10.15:
                band = "30m"
            elif 14.0 <= f <= 14.35:
                band = "20m"
            elif 18.068 <= f <= 18.168:
                band = "17m"
            elif 21.0 <= f <= 21.45:
                band = "15m"
            elif 24.89 <= f <= 24.99:
                band = "12m"
            elif 28.0 <= f <= 29.7:
                band = "10m"
            mode = BAND_MODES.get(band, "USB")
        
        if days == "Daily":
            schedule.every().day.at(time_str).do(apply_schedule, freq_hz, mode, time_str, days, rx)
        elif days == "Monday thru Friday":
            for day in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
                getattr(schedule.every(), day).at(time_str).do(apply_schedule, freq_hz, mode, time_str, days, rx)
        else:
            day = days.lower()
            if day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
                getattr(schedule.every(), day).at(time_str).do(apply_schedule, freq_hz, mode, time_str, days, rx)
            else:
                raise ValueError(f"Invalid day: {days}")
        logging.info(f"Scheduled: {freq} MHz, {mode}, {time_str}, {days}, {rx}")
    except Exception as e:
        logging.error(f"Error creating schedule: {e}\n{traceback.format_exc()}")
        raise

# GUI setup
try:
    root = tk.Tk()
    root.title("Thetis Scheduler by K2COP")
    logging.info("GUI initialized")
    print("GUI initialized")
except Exception as e:
    logging.error(f"Error initializing GUI: {e}\n{traceback.format_exc()}")
    print(f"Error initializing GUI: {e}")
    raise

scheduler_running = False

# Add schedule form
freq_label = ttk.Label(root, text="Frequency (MHz): (e.g., 7.255)")
freq_label.pack()
freq_entry = ttk.Entry(root)
freq_entry.pack()

mode_label = ttk.Label(root, text="Mode:")
mode_label.pack()
mode_combo = ttk.Combobox(root, values=["", "USB", "LSB"])
mode_combo.pack()

time_label = ttk.Label(root, text="Time (HH:MM): (e.g., 14:00)")
time_label.pack()
time_entry = ttk.Entry(root)
time_entry.pack()

days_label = ttk.Label(root, text="Days:")
days_label.pack()
days_combo = ttk.Combobox(root, values=["Daily", "Monday thru Friday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
days_combo.pack()

# NEW: RX1 / RX2 Dropdown
rx_label = ttk.Label(root, text="Receiver:")
rx_label.pack()
rx_combo = ttk.Combobox(root, values=["RX1", "RX2"])
rx_combo.set("RX1")  # Default
rx_combo.pack()

def add_schedule():
    try:
        freq = freq_entry.get()
        mode_input = mode_combo.get()
        time_str = time_entry.get()
        days = days_combo.get()
        rx = rx_combo.get()  # NEW
        freq_float = float(freq)
        if freq_float < 1 or freq_float > 60:
            raise ValueError("Frequency must be between 1 and 60 MHz")
        if not time_str or not days:
            raise ValueError("Time and days must be specified")
        mode = mode_input
        if not mode:
            band = None
            if 1.8 <= freq_float <= 2.0:
                band = "160m"
            elif 3.5 <= freq_float <= 4.0:
                band = "80m"
            elif 7.0 <= freq_float <= 7.3:
                band = "40m"
            elif 10.1 <= freq_float <= 10.15:
                band = "30m"
            elif 14.0 <= freq_float <= 14.35:
                band = "20m"
            elif 18.068 <= freq_float <= 18.168:
                band = "17m"
            elif 21.0 <= freq_float <= 21.45:
                band = "15m"
            elif 24.89 <= freq_float <= 24.99:
                band = "12m"
            elif 28.0 <= freq_float <= 29.7:
                band = "10m"
            mode = BAND_MODES.get(band, "USB")
        
        # Save the new schedule to JSON
        schedules = load_schedules()
        schedules.append({"freq": freq, "mode": mode, "time": time_str, "days": days, "rx": rx})
        save_schedules(schedules)
        
        # Clear and reload all schedules
        schedule.clear()
        for s in schedules:
            create_schedule(s["freq"], s["mode"], s["time"], s["days"], s.get("rx", "RX1"))
        
        update_schedules_listbox()
        messagebox.showinfo("Success", "Schedule added")
    except ValueError as e:
        logging.error(f"Invalid input: {e}\n{traceback.format_exc()}")
        messagebox.showerror("Error", f"Invalid input: {e}")
    except Exception as e:
        logging.error(f"Error adding schedule: {e}\n{traceback.format_exc()}")
        messagebox.showerror("Error", f"Error adding schedule: {e}")

add_button = ttk.Button(root, text="Add Schedule", command=add_schedule)
add_button.pack()

# Scheduled Tasks List with Scrollbar
schedules_frame = tk.Frame(root)
schedules_frame.pack(side='top', fill='both', expand=True)

schedules_label = ttk.Label(schedules_frame, text="Scheduled Tasks:")
schedules_label.pack()

list_frame = tk.Frame(schedules_frame)
list_frame.pack(fill='both', expand=True)

schedules_listbox = tk.Listbox(list_frame, height=10)
schedules_listbox.pack(side='left', fill='both', expand=True)

scrollbar = tk.Scrollbar(list_frame, orient='vertical', command=schedules_listbox.yview)
scrollbar.pack(side='right', fill='y')

schedules_listbox.config(yscrollcommand=scrollbar.set)

def update_schedules_listbox():
    """Update the Listbox with current schedules."""
    try:
        schedules = load_schedules()
        schedules_listbox.delete(0, tk.END)
        for schedule in schedules:
            freq = schedule["freq"]
            mode = schedule["mode"]
            time_str = schedule["time"]
            days = schedule["days"]
            rx = schedule.get("rx", "RX1")  # NEW
            display_str = f"{freq} MHz, {mode}, {time_str}, {days}, {rx}"
            schedules_listbox.insert(tk.END, display_str)
        logging.info("Updated schedules listbox")
    except Exception as e:
        logging.error(f"Error updating listbox: {e}\n{traceback.format_exc()}")

# Control buttons
control_frame = tk.Frame(root)
control_frame.pack(side='bottom', fill='x', pady=10)

remove_disclaimer = ttk.Label(control_frame, text="Stop scheduler before removing a schedule", foreground="red")
remove_disclaimer.pack(side='left', padx=5)

def remove_schedule():
    try:
        if not scheduler_running:
            selected = schedules_listbox.curselection()
            if selected:
                index = selected[0]
                schedules = load_schedules()
                if 0 <= index < len(schedules):
                    del schedules[index]
                    save_schedules(schedules)
                    update_schedules_listbox()
                    schedule.clear()
                    for s in load_schedules():
                        create_schedule(s["freq"], s["mode"], s["time"], s["days"], s.get("rx", "RX1"))
                    messagebox.showinfo("Success", "Schedule removed")
                else:
                    messagebox.showerror("Error", "Invalid selection")
            else:
                messagebox.showerror("Error", "No schedule selected")
        else:
            messagebox.showerror("Error", "Stop the scheduler before removing a schedule")
    except Exception as e:
        logging.error(f"Error removing schedule: {e}\n{traceback.format_exc()}")
        messagebox.showerror("Error", f"Error removing schedule: {e}")

remove_button = ttk.Button(control_frame, text="Remove Selected Schedule", command=remove_schedule)
remove_button.pack(side='left', padx=5)

def start_scheduler():
    global scheduler_running
    try:
        if not scheduler_running:
            scheduler_running = True
            schedule.clear()
            for s in load_schedules():
                create_schedule(s["freq"], s["mode"], s["time"], s["days"], s.get("rx", "RX1"))
            threading.Thread(target=run_schedule, daemon=True).start()
            messagebox.showinfo("Info", "Scheduler started")
            update_button_states()
            logging.info("Scheduler started")
            print("Scheduler started")
        else:
            messagebox.showinfo("Info", "Scheduler is already running")
    except Exception as e:
        logging.error(f"Error starting scheduler: {e}\n{traceback.format_exc()}")
        messagebox.showerror("Error", f"Error starting scheduler: {e}")

start_button = ttk.Button(control_frame, text="Start Scheduler", command=start_scheduler)
start_button.pack(side='left', padx=5)

def stop_scheduler():
    global scheduler_running
    try:
        scheduler_running = False
        schedule.clear()
        messagebox.showinfo("Info", "Scheduler stopped")
        update_button_states()
        logging.info("Scheduler stopped")
        print("Scheduler stopped")
    except Exception as e:
        logging.error(f"Error stopping scheduler: {e}\n{traceback.format_exc()}")
        messagebox.showerror("Error", f"Error stopping scheduler: {e}")

stop_button = ttk.Button(control_frame, text="Stop Scheduler", command=stop_scheduler, state='disabled')
stop_button.pack(side='left', padx=5)

def update_button_states():
    try:
        if scheduler_running:
            start_button.config(state='disabled')
            stop_button.config(state='normal')
        else:
            start_button.config(state='normal')
            stop_button.config(state='disabled')
    except Exception as e:
        logging.error(f"Error updating button states: {e}\n{traceback.format_exc()}")

# Initial update of listbox
update_schedules_listbox()

# Run GUI in main thread
try:
    root.mainloop()
except Exception as e:
    logging.error(f"Error in GUI mainloop: {e}\n{traceback.format_exc()}")
    print(f"Error in GUI mainloop: {e}")
