import os
import sqlite3

db_path = r".\Alpaca\Database\12Auto.db"


conn = sqlite3.connect(db_path)
cursor = conn.cursor()
info =   cursor.execute("SELECT info, date FROM logs")
logs = cursor.fetchall()

conn.close()

print(os.path.exists(r".\Alpaca\Scripts\alpaca_trading.py"))

for log in logs:
    print(f"Info: ${log}, Date: ${log[1]}")

