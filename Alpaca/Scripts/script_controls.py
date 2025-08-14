import os
import psutil
import subprocess
import platform
import sys

# Fixes import issue for db functions
current_dir = os.path.dirname(os.path.abspath(__file__))
alpaca_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, alpaca_dir)

from Database.db_functions import updateProcessId, getProcessId


def checkScriptRunning(target_pid):
    device_platform = get_platform()
    if device_platform == "Windows":
        try:
            process = psutil.Process(int(target_pid))
            if process.name() == "pythonw.exe" or process.name() == "python.exe":
                print("Script running at " + target_pid)
                return True
            else:
                print("no script found.")
                return False
        except:
            print('Script not running')
            updateProcessId("0")
            return False
    else:
        try:
            process = psutil.Process(int(target_pid))
            if process.name() == "python3":
                print("Script running at " + target_pid)
                return True
            else:
                print("no script found.")
                return False
        except:
            print('Script not running')
            updateProcessId("0")
            return False      
    
def stopScript(target_pid):
    target_pid = int(target_pid)
    try: 
        process = psutil.Process(target_pid)

        process.terminate()
        process.wait()
        print(f"Script {target_pid} successfully terminiated")
        return False

    except psutil.NoSuchProcess:
        print(f"No process found with PID {target_pid}")
    except psutil.AccessDenied:
        print(f"Access denied to terminate process {target_pid}")
    except psutil.ZombieProcess:
        print(f"Process with PID {target_pid} is a zombie process and cannot be terminated.")
    
    return True

def get_platform():
    if platform.system() == "Windows":
        return "Windows"
    elif platform.system() == "Linux":
        return "Linux"
    else:
        return "mac"

def runScript():
        old_pid = getProcessId()
        still_active = checkScriptRunning(old_pid)
        if still_active == True:
            stopScript(old_pid)
        # Run script for stocks
        platform = get_platform()

        current_working_dir = os.getcwd()

        bcknd_script =  r".\Alpaca\Scripts\alpaca_trading.py"



        if platform == "Windows":
            bcknd_script =  r".\Alpaca\Scripts\alpaca_trading.py"

            process = subprocess.Popen(["pythonw", bcknd_script])
            updateProcessId(process.pid)
            print(f"Run script at PID: {process.pid}")
            return process.pid
        else:
            bcknd_script = r"Alpaca/Scripts/alpaca_trading.py"
            process = subprocess.Popen(["python3", bcknd_script, "&"])
            updateProcessId(process.pid)
            print(process.pid)
            return process.pid

