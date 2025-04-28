# Thetis Scheduler

Thetis Scheduler is a Python-based GUI application designed to automate frequency and mode changes for the Kenwood TS-2000 amateur radio via its CAT (Computer Aided Transceiver) interface. Built by K2COP, the application allows users to schedule radio operations at specific times and days, making it ideal for ham radio operators who need consistent, automated band and mode switching. The interface is built with Tkinter, and schedules are stored in a JSON file for persistence.

## Features
- **Automated Scheduling**: Set frequency (e.g., 3.755 MHz) and mode (e.g., LSB) changes for specific times and days (Daily, Monday through Friday, or individual days).
- **Band-Aware Mode Selection**: Automatically selects USB or LSB based on the frequency’s amateur radio band (e.g., LSB for 80m, USB for 20m) if no mode is specified.
- **Persistent Schedules**: Stores schedules in `schedules.json` for reuse across sessions.
- **Logging**: Detailed logging of operations and errors to `scheduler.log` for debugging and monitoring.
- **Thread-Safe CAT Commands**: Uses a thread lock to ensure reliable communication with the TS-2000 over a TCP socket (`127.0.0.1:50001`).
- **User-Friendly GUI**: Built with Tkinter, featuring input fields for frequency, mode, time, and days, plus a listbox to view and manage schedules.
- **Error Handling**: Robust validation and error reporting for invalid inputs (e.g., frequencies outside 1–60 MHz) and connection issues.

## Requirements
- **Hardware**:
  - Kenwood TS-2000 radio with a configured CAT interface accessible at `127.0.0.1:50001`.
  - Windows operating system (tested on Windows with Python 3.13).
- **Software**:
  - Python 3.13 or later.
  - Python standard library modules: `tkinter`, `json`, `threading`, `socket`, `time`, `logging`, `traceback`.
  - External library: `schedule` (install via `pip install schedule`).
- **Optional**:
  - Virtual Audio Cable (VAC) for audio routing, configured as "Line 3 (Virtual Audio Cable)" with a 44.1 kHz sample rate (used in the script’s configuration but not directly implemented).

## Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/Thetis-Scheduler.git
   cd Thetis-Scheduler
