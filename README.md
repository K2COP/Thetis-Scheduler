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
   git clone https://github.com/your-username/Thetis-Scheduler.git
   cd Thetis-Scheduler
type "python thetis_scheduler.py"  no quotes to start the script and if all went well the program window will open.
