# Story Rpc Scanner- Simple Setup Guide

This project includes two main Python scripts: `prg.py` and `scan.py`. Here's a quick guide to what they do and how to set them up.

## What Does the Program Do?

- **prg.py**: This is the main user interface of the program. It shows results of RPC validators and vulnerable validators in a visually styled window using PyQt5.
- **scan.py**: This script scans for validators' RPCs, checks their status, and writes the results into CSV files (`valid_rpc.csv` and `vulnerable_validators.csv`).

## Requirements

Before running the program, ensure you have the following:

- **Python 3.9+** installed on your system.
- Required Python libraries: `PyQt5`, `requests`, `tabulate`, `vlc`.

## Quick Setup Instructions

### Step 1: Install Python

Download and install Python from [python.org](https://www.python.org/downloads/). Ensure you check the option to "Add Python to PATH" during installation.

### Step 2: Install Required Libraries

Open your terminal or command prompt and run the following command to install the necessary libraries:

```
pip install PyQt5 requests tabulate python-vlc
```
### Step 3: Update Python Executable Path
In the prg.py script, adjust the Python executable path if necessary. Replace the following line with the correct path to your Python installation:
```
python_path = "C:/Users/x1001/AppData/Local/Programs/Python/Python313/python.exe"

```
### Step 4: Run the Program
Run the main program (prg.py):

```
python prg.py
```

From the interface, you can:

**Show Valid RPC:** Displays the valid RPC results from the scan.
**Show Vulnerable** Validators: Displays the vulnerable validators.
**Start New Scan** Initiates a new scan by running scan.py to update the results.
That's it! You can now interact with the program and view the validator results.


### Note:
The RPC scanner process in the program may take 5-10 minutes to complete depending on the network and the number of nodes. If you are starting a new scan, please allow time for the process to finish before expecting the results.
