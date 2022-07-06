#-*- coding: utf-8 -*-

import sqlite3

con = sqlite3.connect('DB/detect.db')
cur = con.cursor()

con.commit()
con.close()
