# Init Database
# Create a new SQL database in the target file, if it already exists, drop and rewrite
# Gordon Swan - Advanced Web Tech Coursework 2

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


schFile = open("var/Schema.sql", "r")
cur.executescript(schFile.read())
print("Successfully executed schema file")
