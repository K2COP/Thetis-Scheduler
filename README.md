# Thetis Scheduler for Hermes Lite 2

Thetis Scheduler is a Python-based GUI application designed to automate frequency and mode changes for the Hermes Lite 2 running Thetis Software amateur radio via its CAT (Computer Aided Transceiver) interface. Built by K2COP, the application allows users to schedule radio frequencies at specific times and days, making it ideal for ham radio operators who need consistent, automated band and mode switching. The interface is built with Tkinter, and schedules are stored in a JSON file for persistence.

## Features
- **Automated Scheduling**: Set frequency (e.g., 3.777 MHz) and mode (e.g., LSB) changes for specific times and days (Daily, Monday through Friday, or individual days).
- **Band-Aware Mode Selection**: Automatically selects USB or LSB based on the frequency’s amateur radio band (e.g., LSB for 80m, USB for 20m) if no mode is specified.
- **Persistent Schedules**: Stores schedules in `schedules.json` for reuse across sessions.
- **Logging**: Detailed logging of operations and errors to `scheduler.log` for debugging and monitoring.
- **Thread-Safe CAT Commands**: Uses a thread lock to ensure reliable communication with the TS-2000 CAT server over a TCP socket (`127.0.0.1:50001`).
- **User-Friendly GUI**: Built with Tkinter, featuring input fields for frequency, mode, time, and days, plus a listbox to view and manage schedules.
- **Error Handling**: Robust validation and error reporting for invalid inputs (e.g., frequencies outside 1–60 MHz) and connection issues.

## Requirements
- **Hardware**:
  - Hermes Lite 2 with a configured CAT interface (Kenwood TS-2000 CAT commands) accessible at `127.0.0.1:50001`.
  - Windows operating system (tested on Windows 11 with Python 3.13.3).
- **Software**:
  - Python 3.13 or later. Download python from https://python.org/download
  - Python standard library modules: `tkinter`, `json`, `threading`, `socket`, `time`, `logging`, `traceback`.
  - External library: `schedule` (install via `pip install schedule`). <--  from cmd box type "pip install schedule" (no quotation marks)

## Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/K2COP/Thetis-Scheduler.git
   cd Thetis-Scheduler
type "python thetis_scheduler_GUI.py"  no quotes to start the script and if all went well the program window will open.
or type "py thetis_scheduler_gui_dual.py" no quotes to start the script and all went well the program will open.

11/10/25 Added option for second receiver (RX 2).  You just select whether the change will take place on RX 1 or RX 2 when creating a scheduled frequency change.

Added Comments:  A few things have changed.  python.org has moved to installing python through Windows App Store.  This change has virtually no effect on the script. You will however still need to install "schedule" library through pip. The command would be similar to "pip install schedule" NO QUOTES! Once this is done the script will start normally.  

One other note to mention.  The first time you start the script and add a scheduled frequency change you will have to end and restart the python script "thetis_scheduler_gui_dual.py"  This is because the schedule is saved in a file in the same directory as the script and has a suffix of .json  Once the schedule has been added and the script has been killed and restarted the .json file wil be read and everything will function as expected. For myself I open a cmd window (search box and type cmd youll see where to click to open the command prompt window) You can then "pin" the program to the task bar and click it after reboot. If you have typed the command to start the prompt previously just "up arror" on keyboard and you shoud see something like "py thetis_scheduler_gui_dual.py" at that point you can hit "enter" to run the script.
