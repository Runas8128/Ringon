import sqlite3

con = sqlite3.connect('DB/event.db')
cur = con.cursor()



con.commit()
con.close()
