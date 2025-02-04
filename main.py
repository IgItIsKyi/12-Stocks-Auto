# Modules
import customtkinter
import platform
import sqlite3
import tkinter.messagebox as messagebox
import sys
from cryptography.fernet import Fernet
import os
import subprocess
import psutil

# Global Variables
bcknd_script_pid = 0

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("dark-blue")

root = customtkinter.CTk()
root.title("12 Auto Stocks")
root.geometry("500x350")

def checkFirstRun():
    try:
        conn = sqlite3.connect("12Auto.db")
        cursor = conn.cursor()
        cursor.execute("SELECT key FROM user WHERE id = 1")
        
    except:
        # Create popup to get initial SQL information
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
        cur_stock TEXT
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
    buildTables()

    conn = sqlite3.connect("12Auto.db")
    cursor = conn.cursor()

    key = Fernet.generate_key()
    cipher = Fernet(key)
    initial_stock = 1

    encrypted_api_key = cipher.encrypt(api.encode())
    encrypted_secret_key = cipher.encrypt(secret.encode())

    cursor.execute("INSERT INTO user (api_key, secret, key, pay_date, cur_stock) VALUES (?,?,?,?,?)", (encrypted_api_key, encrypted_secret_key, key, payday, initial_stock ))

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
    # Run script for stocks
    platform = get_platform()

    current_working_dir = os.getcwd()
    bcknd_script = os.path.join(current_working_dir, "script.py")

    print(bcknd_script)

    if platform == "Windows":
        process = subprocess.Popen(["pythonw", bcknd_script])
        
        return process.pid
    else:
        process = subprocess.Popen(["python3", bcknd_script, "&"])
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
logs_frame = customtkinter.CTkFrame(master=main_frame)
logs_frame.pack(pady=20, padx=60, fill="both", expand=True)

logs_label = customtkinter.CTkLabel(master=logs_frame, text="Logs", font=("Roboto", 24))
logs_label.pack(pady=12, padx=10)

logs_text = customtkinter.CTkTextbox(master=logs_frame)
logs_text.pack(pady=12, padx=10, fill="both", expand=True)


logs_frame.pack_forget()

bcknd_script_pid = runScript()
checkFirstRun()
print(f"Process id is {bcknd_script_pid}")
# Run application
root.mainloop()