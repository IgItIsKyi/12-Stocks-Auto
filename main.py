# Modules
import customtkinter
import platform
import sqlite3
from tkinter import ttk
import tkinter.messagebox as messagebox
from cryptography.fernet import Fernet
import os
import subprocess
import psutil

# Global Variables


customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("dark-blue")

root = customtkinter.CTk()
root.title("12 Auto Stocks")
root.geometry("500x350")
root.resizable(False, False)

def checkFirstRun():
    try:
        conn = sqlite3.connect("12Auto.db")
        cursor = conn.cursor()
        cursor.execute("SELECT key FROM user WHERE id = 1")
        
    except:
        # Create popup to get initial SQL information
        buildTables()
        show_popup()

def buildTables():
    # SQL Connection
    conn = sqlite3.connect("12Auto.db")
    cursor = conn.cursor()

    # Create the user table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY,
        api_key BLOB,
        secret BLOB,
        key BLOB,
        pay_date TEXT,
        cur_stock TEXT, 
        process_pid TEXT
    )
    """)

    # Create "logs" Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (

            id INTEGER PRIMARY KEY,
            info TEXT,
            date                  
        )
    """)
    # Create "stocks" Table and add all 12 stocks

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS stocks (

                id INTEGER PRIMARY KEY,
                stock_sym TEXT 
                    
            )
                    
        """)

        # Add all stocks to the table (each stock gives a dividend at some point)
    stocks = ['CSCO', 'LNC', 'ABBV', 'CFG', 'KMI', 'DUK', 'MMM', 'WHR', 'KEY', 'CCI', 'MO', 'WPC']

    for stock in stocks: 
        cursor.execute("INSERT INTO stocks (stock_sym) VALUES (?)", (stock,))

    conn.commit()

    conn.close()


def initial_setup(api, secret, payday, popup):

    conn = sqlite3.connect("12Auto.db")
    cursor = conn.cursor()

    key = Fernet.generate_key()
    print(f"Key: {key}")
    cipher = Fernet(key)
    initial_stock = 1

    encrypted_api_key = cipher.encrypt(api.encode())
    encrypted_secret_key = cipher.encrypt(secret.encode())

    cursor.execute("INSERT INTO user (api_key, secret, key, pay_date, cur_stock) VALUES (?,?,?,?,?)", (encrypted_api_key, encrypted_secret_key, key, payday, initial_stock, ))

    conn.commit()
    conn.close()
    popup.destroy()

def show_popup():
        popup = customtkinter.CTkToplevel(root)
        popup.geometry("300x300")
        popup.title("First Run")
        popup.resizable(False, False)

        popup_label = customtkinter.CTkLabel(master=popup, text="First Time Setup")
        popup_label.pack(pady=10, padx=10)
        api_key = customtkinter.CTkEntry(master=popup, placeholder_text="Input Api Key Here")
        api_key.pack(pady=12, padx=10)

        secret_key = customtkinter.CTkEntry(master=popup, placeholder_text="Input Secret Key Here")
        secret_key.pack(pady=12, padx=10)

        next_payday = customtkinter.CTkEntry(master=popup, placeholder_text="Next Pay Day ( MM/DD/YYYY )")
        next_payday.pack(pady=12, padx=10)

        submit_button = customtkinter.CTkButton(master=popup, text= "Submit", command= lambda: initial_setup(api_key.get(), secret_key.get(), next_payday.get(), popup))
        submit_button.pack(pady=12, padx=10)           

def get_platform():
    if platform.system() == "Windows":
        return "Windows"
    elif platform.system() == "Linux":
        return "Linux"
    else:
        return "mac"

def runScript():
    Running = checkScriptRunning(bcknd_script_pid)

    if Running == True:
        stopScript(bcknd_script_pid)
        runScript()

    else:
        # Run script for stocks
        platform = get_platform()

        current_working_dir = os.getcwd()
        bcknd_script = os.path.join(current_working_dir, "script.py")

        if platform == "Windows":
            process = subprocess.Popen(["pythonw", bcknd_script])
            print(f"Process id is {process.pid}")
            updateProcessId(process.pid)
            return process.pid
        else:
            process = subprocess.Popen(["python3", bcknd_script, "&"])
            updateProcessId(process.pid)
            return process.pid

def stopScript(target_pid):
    try: 
        process = psutil.Process(target_pid)

        process.terminate()
        process.wait()

    except psutil.NoSuchProcess:
        print(f"No process found with PID {target_pid}")
    except psutil.AccessDenied:
        print(f"Access denied to terminate process {target_pid}")
    except psutil.ZombieProcess:
        print(f"Process with PID {target_pid} is a zombie process and cannot be terminated.")
    
def update_keys(api, secret, process_id):

    stopScript(process_id)

    try:
        conn = sqlite3.connect("12Auto.db")
        cursor = conn.cursor()
        if api == "" or secret == "":
            messagebox.showerror("Missing Info", "One or more boxes are empty")
        else:
            cursor.execute("SELECT key FROM user WHERE id = 1")
            key = cursor.fetchone()
            cipher = Fernet(key[0])
        
            encrypted_api_key = cipher.encrypt(api.encode())
            encrypted_secret_key = cipher.encrypt(secret.encode())
            cursor.execute("""
                UPDATE user
                SET api_key = ?, secret = ?
                Where id = 1
                """, (encrypted_api_key, encrypted_secret_key)
            )

            messagebox.showinfo("Success", "API and Secret key updated successfully")
            api_key.delete(0, "end") 
            secret_key.delete(0, "end") 


            conn.commit()
            conn.close()

        bcknd_script_pid = runScript()

    except:
        messagebox.showwarning("Error", "Unable to update")  

def getLogs():
    # SQL Connection
    conn = sqlite3.connect("12Auto.db")
    cursor = conn.cursor()

    # Get all log information from SQL Table
    cursor.execute("SELECT info, date FROM logs")
    logs = cursor.fetchall()

    conn.close()

    for log in logs:
        table.insert("", "end", values=log)

def getProcessId():
    # SQL Connection
    conn = sqlite3.connect("12Auto.db")
    cursor = conn.cursor()

    try: 
        cursor.execute("SELECT process_pid FROM user WHERE id = 1")
        pid = cursor.fetchone()
        return pid

    except:
        return 0


def checkScriptRunning(target_pid):
    # SQL Connection
    conn = sqlite3.connect("12Auto.db")
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT process_pid FROM user WHERE id = 1")
        bcknd_script_pid = cursor.fetchone()

        process = psutil.Process(target_pid)

        if process.name == "python":
            return True

    except:
        return False

def updateProcessId(new_pid):
    # SQL Connection
    conn = sqlite3.connect("12Auto.db")
    cursor = conn.cursor()

    cursor.execute("""
                    UPDATE user
                    SET process_pid = ?
                    Where id = 1
                    """, (new_pid,)
                )

    

# NavBar
nav_frame = customtkinter.CTkFrame(master=root)
nav_frame.pack(side="top", pady=20, fill="x", expand=False)

InfoBtn = customtkinter.CTkButton(master=nav_frame, text="Info", command=lambda: logs_frame.pack_forget() or info_frame.pack())
InfoBtn.pack(side="left", padx=10, pady=10)

LogBtn = customtkinter.CTkButton(master=nav_frame, text="Logs", command=lambda: info_frame.pack_forget() or logs_frame.pack())
LogBtn.pack(side="right", padx=10, pady=10)
# End of NavBar

# Main Frame Section
main_frame = customtkinter.CTkFrame(master=root)
main_frame.pack()

# Info Page / Frame

info_frame = customtkinter.CTkFrame(master=main_frame)
info_frame.pack(pady=20, padx=60, fill="both", expand=True)

info_label = customtkinter.CTkLabel(master=info_frame, text="Update Keys", font=("Roboto", 24))
info_label.pack(pady=12, padx=10)

api_key = customtkinter.CTkEntry(master=info_frame, placeholder_text="Input Api Key Here")
api_key.pack(pady=12, padx=10)

secret_key = customtkinter.CTkEntry(master=info_frame, placeholder_text="Input Secret Key Here")
secret_key.pack(pady=12, padx=10)

update_button= customtkinter.CTkButton(master=info_frame, text= "Update", command= lambda: update_keys(api_key.get(), secret_key.get(), bcknd_script_pid))
update_button.pack(pady=12, padx=10)
# End of Info Page

# Logs Page
style = ttk.Style()
style.configure("Treeview",
                 backgrouund="#242424",
                 foreground="black",
                 font=("Roboto", 12))

style.configure("Treeview.Heading", font=('Roboto', 14, 'bold'))



logs_frame = customtkinter.CTkFrame(master=main_frame)
logs_frame.pack(pady=20, padx=60, fill="both", expand=True)

logs_label = customtkinter.CTkLabel(master=logs_frame, text="Logs", font=("Roboto", 24))
logs_label.pack(pady=8, padx=10)

table = ttk.Treeview(logs_frame, columns=("Log", "Date"), show="headings")
table.heading("Date", text="Date")
table.column("Date", width=100, anchor="center")
table.heading("Log", text="Log")
table.column("Log", width=375)
table.pack(pady=12, padx=10, fill="both", expand=True)


# End of Logs Page


logs_frame.pack_forget()

checkFirstRun()

try:
    getLogs()
except:
    ...

bcknd_script_pid = getProcessId()
bcknd_script_pid = runScript()

# Run application
root.mainloop()