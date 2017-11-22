import sys
import sqlite3 as sql

try:
	DB = 'var/main.db'
	conn = sql.connect(DB)
	cur = conn.cursor()

	print("Successfully connected to database file")
except:
	print("Couldn't connect ro database file (ERR)")
	sys.exit()


sql = "SELECT * FROM thread"

cur.execute(sql)
ddata = cur.fetchall()

print(str(ddata))
