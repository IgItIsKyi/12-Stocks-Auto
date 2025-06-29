# Modules
import customtkinter
import platform
import sqlite3
from tkinter import StringVar, ttk
import tkinter.messagebox as messagebox
from cryptography.fernet import Fernet
import os
import subprocess
import psutil
import webbrowser

# Global Variables


customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("dark-blue")

root = customtkinter.CTk()
root.title("12 Auto Stocks")
root.geometry("500x500")
root.resizable(False, False)

db_path = r".\Alpaca\Database\12Auto.db"

def checkFirstRun():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT key FROM user WHERE id = 1")
        
    except:
        # Create popup to get initial SQL information
        buildTables()
        show_alpaca_popup()

def buildTables():
    # SQL Connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create the alpaca user table
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

    # Create the webull user table
#     cursor.execute("""
#     CREATE TABLE IF NOT EXISTS user (
#     id INTEGER PRIMARY KEY,
#     email BLOB,
#     password BLOB,
#     did BLOB,
#     key BLOB,
#     pay_date TEXT,
#     cur_stock TEXT, 
#     process_pid TEXT
# )
# """)

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

def show_choice_popup():
    popup = customtkinter.CTkToplevel(root)
    popup.geometry("300x300")
    popup.title("First Run")
    popup.resizable(False, False)

    popup_label = customtkinter.CTkLabel(master=popup, text="First Time Setup")
    popup_label.pack(pady=10,padx=10)
    alpaca_choice = customtkinter.CTkButton(master=popup, text="Alpaca", command=show_alpaca_popup)
    alpaca_choice.pack(pady=12, padx=10)
    webull_choice = customtkinter.CTkButton(master=popup, text="Webull", command=show_webull_popup)
    webull_choice.pack(pady=12, padx=10)

def initial_alpaca_setup(api, secret, payday, popup, initial_stock):

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f'Stock: {initial_stock}')
    try:
        cursor.execute("SELECT id FROM stocks WHERE stock_sym = ?", (initial_stock, ))
        stock = cursor.fetchone()[0]
    except:
        stock = 1

    print(f"Stock number: {stock}")

    key = Fernet.generate_key()
    print(f"Key: {key}")
    cipher = Fernet(key)

    encrypted_api_key = cipher.encrypt(api.encode())
    encrypted_secret_key = cipher.encrypt(secret.encode())

    cursor.execute("INSERT INTO user (api_key, secret, key, pay_date, cur_stock) VALUES (?,?,?,?,?)", (encrypted_api_key, encrypted_secret_key, key, payday, stock, ))

    conn.commit()
    conn.close()
    popup.destroy()

def show_alpaca_popup():
        
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

        options = [
            ' ',
            'CSCO', 
            'LNC', 
            'ABBV', 
            'CFG', 
            'KMI', 
            'DUK', 
            'MMM', 
            'WHR', 
            'KEY', 
            'CCI', 
            'MO', 
            'WPC'
        ]

        clicked = StringVar()

        clicked.set('CSCO')

        drop = ttk.OptionMenu(popup, clicked, *options)
        drop.pack()

        submit_button = customtkinter.CTkButton(master=popup, text= "Submit", command= lambda: initial_alpaca_setup(api_key.get(), secret_key.get(), next_payday.get(), popup, clicked.get()))
        submit_button.pack(pady=12, padx=10) 

def initial_webull_setup(email, password, device_id, payday, popup, initial_stock,):

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM stocks WHERE stock_sym = ?", (initial_stock, ))
        stock = cursor.fetchone()[0]
    except:
        stock = 1

    key = Fernet.generate_key()
    print(f"Key: {key}")
    cipher = Fernet(key)

    encrypted_email = cipher.encrypt(email.encode())
    encrypted_password = cipher.encrypt(password.encode())
    encrypted_did = cipher.encrypt(device_id.encode())

    cursor.execute("INSERT INTO user (email, password, did,  key, pay_date, cur_stock) VALUES (?,?,?,?,?,?)", (encrypted_email, encrypted_password, encrypted_did, key, payday, stock, ))

    conn.commit()
    conn.close()
    popup.destroy()        

def show_webull_popup():
        popup = customtkinter.CTkToplevel(root)
        popup.geometry("300x400")
        popup.title("First Run")
        popup.resizable(False, False)

        popup_label = customtkinter.CTkLabel(master=popup, text="First Time Setup")
        popup_label.pack(pady=10, padx=10)
        webull_email = customtkinter.CTkEntry(master=popup, placeholder_text="Input Webull Email Here")
        webull_email.pack(pady=12, padx=10)

        webull_password = customtkinter.CTkEntry(master=popup, placeholder_text="Input Webull Password Here")
        webull_password.pack(pady=12, padx=10)

        device_id = customtkinter.CTkEntry(master=popup, placeholder_text="Input Device ID Here (follow doc to get it)")
        device_id.pack(pady=12, padx=10)

        next_payday = customtkinter.CTkEntry(master=popup, placeholder_text="Next Pay Day ( MM/DD/YYYY )")
        next_payday.pack(pady=12, padx=10)

        options = [
            ' ',
            'CSCO', 
            'LNC', 
            'ABBV', 
            'CFG', 
            'KMI', 
            'DUK', 
            'MMM', 
            'WHR', 
            'KEY', 
            'CCI', 
            'MO', 
            'WPC'
        ]

        clicked = StringVar()

        clicked.set('CSCO')

        drop = ttk.OptionMenu(popup, clicked, *options)
        drop.pack()

        submit_button = customtkinter.CTkButton(master=popup, text= "Submit", command= lambda: initial_webull_setup(webull_email.get(), webull_password.get(), device_id.get(), next_payday.get(), popup, clicked.get()))
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
        bcknd_script =  r".\Alpaca\Scripts\alpaca_trading.py"



        if platform == "Windows":
            process = subprocess.Popen(["pythonw", bcknd_script])
            updateProcessId(process.pid)
            print(process.pid)
            return process.pid
        else:
            process = subprocess.Popen(["python3", bcknd_script, "&"])
            updateProcessId(process.pid)
            print(process.pid)
            return process.pid

def stopScript(target_pid):
    target_pid = int(target_pid)
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
    
def update_keys(email, password, did, process_id):

    stopScript(process_id)

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        if email == "" or password == "":
            messagebox.showerror("Missing Info", "One or more boxes are empty")
        else:
            cursor.execute("SELECT key FROM user WHERE id = 1")
            key = cursor.fetchone()
            cipher = Fernet(key[0])
        
            encrypted_email = cipher.encrypt(email.encode())
            encrypted_password = cipher.encrypt(password.encode())
            encrypted_did = cipher.encrypt(did.encode())

            cursor.execute("""
                UPDATE user
                SET email = ?, password = ?, did = ?
                Where id = 1
                """, (encrypted_email, encrypted_password, did )
            )

            messagebox.showinfo("Success", "Email, password and did updated successfully")
            email.delete(0, "end") 
            password.delete(0, "end") 


            conn.commit()
            conn.close()

        runScript()

    except:
        messagebox.showwarning("Error", "Unable to update")  

def getLogs():
    # SQL Connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all log information from SQL Table
    cursor.execute("SELECT info, date FROM logs")
    logs = cursor.fetchall()


    conn.close()

    for log in logs:
        table.insert("", "end", values=log)


def getProcessId():
    # SQL Connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try: 
        cursor.execute("SELECT process_pid FROM user WHERE id = 1")
        pid = cursor.fetchone()
        return pid[0]

    except:
        return 0


def checkScriptRunning(target_pid):

    try:
        process = psutil.Process(int(target_pid))

        if process.name() == "pythonw.exe" or process.name() == "python.exe":
            print("Script running at " + target_pid)
            return True

    except:
        print('Script not running')
        return False

def updateProcessId(new_pid):
    # SQL Connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
                    UPDATE user
                    SET process_pid = ?
                    Where id = 1
                    """, (new_pid,)
                )
    
    conn.commit()
    conn.close()

def findDID():
    webbrowser.open("https://github.com/tedchou12/webull/wiki/Workaround-for-Login-%E2%80%90-Method-2")
    

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

email = customtkinter.CTkEntry(master=info_frame, placeholder_text="Input Email Here")
email.pack(pady=12, padx=10)

password = customtkinter.CTkEntry(master=info_frame, placeholder_text="Input Password Here")
password.pack(pady=12, padx=10)

device_id = customtkinter.CTkEntry(master=info_frame, placeholder_text="Input Device ID Here")
device_id.pack(pady=12, padx=10)

find_did_link = customtkinter.CTkButton(master=info_frame, text="Find Device ID here", bg_color="blue", cursor="hand2", command= lambda: findDID())
find_did_link.pack(pady=20)

update_button = customtkinter.CTkButton(master=info_frame, text= "Update", command= lambda: update_keys(email.get(), password.get(), device_id.get(), bcknd_script_pid))
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
running = checkScriptRunning(bcknd_script_pid)
if running == False:
    print("Script starting now")
    bcknd_script_pid = runScript()
else:
    print("Script running at PID: ", bcknd_script_pid)


# Run application
root.mainloop()
