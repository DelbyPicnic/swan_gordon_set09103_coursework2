import sqlite3 as sql

try:
	DB = 'var/main.db'
	conn = sql.connect(DB)
	cur = conn.cursor()

	print("Successfully connected to database file")
except:
	print("Couldn't connect ro database file (ERR)")
	sys.exit()

cur.execute("INSERT INTO thread (thread_title, thread_content, thread_owner) VALUES (?,?,?)", \
 ("Welcome to Messageboard!","Welcome to messageboard! Please sign in or register to make threads or posts ","root"))
conn.commit()
