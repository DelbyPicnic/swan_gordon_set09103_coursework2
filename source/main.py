# Advanced Web Tech - Coursework 2
# Messageboard App


from flask import Flask, g, request, render_template, url_for, session, redirect, abort
import sqlite3 as sql
import ConfigParser
from HTMLParser import HTMLParser
from Crypto.Hash import SHA256

app = Flask(__name__)
app.secret_key = 'UBbTThWlFeXW4vDXxpvBXAZTDMs7uSJDSDitUKX2'

db_loc = 'var/main.db'

# <-------- HTML Strip Tags  ----------->
# https://stackoverflow.com/questions/753052/strip-html-from-strings-in-python
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()
# <------------------------------------>

def init(app):
	cfg = ConfigParser.ConfigParser()
	try:
		cfg.read("etc/defaults.cfg")

		app.config['DEBUG'] = cfg.get("config","debug")
		app.config['ip_address'] = cfg.get("config","ip_address")
		app.config['port'] = cfg.get("config","port")
		app.config['url'] = cfg.get("config","url")
	except:
		print("Could not retrieve configuration information")

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = sql.connect(db_loc)
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route("/")
def root():

	# Load feed of all active threads, ordered by unicode time
	# Display in a template in that order
	# If active session then show make new post/thread buttons, don't show sign in

	db = get_db()
	cur = db.cursor()
	cur.execute("SELECT * FROM thread WHERE thread_active = 'TRUE' ORDER BY thread_time DESC LIMIT 8")
	data = cur.fetchall()

	return render_template("dashboard.html", threads=data)

@app.route("/account")
def account():
	return render_template("account.html")

@app.route("/viewthread", methods=['GET','POST'])
def view_thread():
	# If no paramiter is sent, redirect to root
	# f paramiter is sent, get data from database
	# If data does not exist then throw 404
	# else redner templte with 

	threadID = request.args.get('id', '')

	if threadID == '':
		return redirect(url_for('root'))
	
	db = get_db()
	cur = db.cursor()
	cur.execute("SELECT * FROM thread WHERE thread_id = ? AND thread_active = 'TRUE'", (threadID,))
	th_data = cur.fetchall()

	if len(th_data) < 1:
		abort(404)

	cur.execute("SELECT * FROM post WHERE post_thread = ? AND post_active = 'TRUE' ORDER BY post_time", (threadID,))
	ps_data = cur.fetchall()

	return render_template("viewthread.html", thread = th_data, posts = ps_data)


@app.route("/sign-in", methods=['GET','POST'])
def login():
	# If not post, show login page
	# If post, accept login information, check user details
	# If correct, set session and load dash with session

	if request.method == 'POST':
		if request.form['username'] == "" or request.form['password'] == "":
			return "All fields are required!"

		db = get_db()
		cur = db.cursor()
		cur.execute("SELECT user_name, user_email, user_password, user_level FROM user WHERE user_name = ?", (request.form['username'],))
		data = cur.fetchall()

		encPass = SHA256.new(request.form['password']).hexdigest()
		
		if len(data) > 0:
			if data[0][2] == encPass:
				session['username'] = data[0][0]
				session['email'] = data[0][1]
				session['status'] = data[0][3]

				return redirect(url_for("root"))
			else:
				return "Username or Password is incorrect"

		else:
			return "Username or Password is incorrect"

	else:
		return render_template("sign-in.html")


@app.route("/register", methods=['GET','POST'])
def register():
	# If not post, show register page
	# If post, check credentials and validate
	# If invalid, redirect to register page with warning
	# If vald, create account and redirect to login page

	if request.method == 'POST':
		if request.form['username'] == "" or request.form['password'] == "" or request.form['email'] == "":
			return "All fields are required!"
		if request.form['password'] != request.form['password2']:
			return "Passwords don't match"

		db = get_db()
		cur = db.cursor()
		cur.execute("SELECT user_name FROM user WHERE user_name = ?", (request.form['username'],))
		data = cur.fetchall()

		if len(data) > 0:
			return "An account with that name already exists"
		else:
			encPass = SHA256.new(request.form['password']).hexdigest()

			cur.execute("INSERT INTO user(user_name, user_email, user_password) VALUES (?,?,?)", \
				(strip_tags(request.form['username']), strip_tags(request.form['email']), encPass,))
			db.commit()

			return redirect(url_for("login"))

	else:
		return render_template("register.html")


@app.route("/sign-out")
def logout():
	# If session active, then kill session
	# redirect to home

	session.clear()
	return redirect(url_for('root'))

@app.route("/new_thread", methods=['POST'])
def mk_thread():
	# Post only route for creating new threads
	# Redirect to root with warning if invalid
	# Requires active session

	if request.method == 'POST':
		try:
			if(session['username']):
				if request.form['title'] == "" or request.form['content'] == "":
					print("ERR: Could not make thread due to missing paramiters")
					return redirect(url_for("root"))
				else:
					if(len(request.form['title']) > 150 or len(request.form['content']) > 800):
						print("ERR: Could not make thread due to oversized paramiters")
						return redirect(url_for("root"))
					else:
						db = get_db()
						cur = db.cursor()
						cur.execute("INSERT INTO thread (thread_title, thread_content, thread_owner, thread_time) VALUES (?,?,?,strftime('%s','now'))", \
							(strip_tags(request.form['title']), strip_tags(request.form['content']), session['username'],))
						db.commit()
						print("Thread created successfully")
						return redirect(url_for('root'))

		except KeyError:
			pass

		print("Could not make thread. Paramiter error")
		return redirect(url_for('root'))
	else:
		return redirect(url_for('root'))



@app.route("/rm_thread", methods=['POST'])
def rm_thread():
	# Post only route for deleting threads
	# Redirect to root with warning if invalid
	# Requires active session, requires session to be owner of thread

	if request.method == 'POST':
		try:
			if(session['username']):
				db = get_db()
				cur = db.cursor()
				cur.execute("SELECT thread_id, thread_owner, thread_active FROM thread WHERE thread_id = ?", (request.form['threadID'],))
				data = cur.fetchall()

				if len(data) == 0:
					print("Could not find thread relating to this id")
					return redirect(url_for('root'))
				
				if data[0][1] == session['username'] or session['status'] > 0:
					cur.execute("UPDATE thread SET thread_active = 'FALSE' WHERE thread_id = ?",(request.form['threadID'],))
					db.commit()
					print("Thread status updated successfully")
					return redirect(url_for('root'))
				else:
					print("Could not remove thread, not authorised")
					return redirect(url_for('root'))
			
		except KeyError:
			pass
		
		print("Could not remove thread, paramiter error")
		return redirect(url_for('root'))
	else:
		return redirect(url_for('root'))

@app.route("/new_post", methods=['POST'])
def mk_post():
	# Post only route for creating new posts
	# Redirect to root with warning if invalid
	# Requirs active session

	if request.method == 'POST':
		try:
			if(session['username']):
				if request.form['content'] == "":
					print("ERR: Could not make post due to missing paramiters")
					return redirect(url_for("root"))
				else:
					if(len(request.form['content']) > 1200):
						print("ERR: Could not make post due to oversized paramiters")
						return redirect(url_for("root"))
					else:
						db = get_db()
						cur = db.cursor()
						cur.execute("SELECT thread_id, thread_active FROM thread WHERE thread_id = ?", (request.form['threadID'],))
						data = cur.fetchall()
						if len(data) == 0:
							print("Could not make post as the associated thread couldn't be found")
							return redirect(url_for('root'))

						if data[0][1] == False:
							print("Could not add post as the thread is no longer active")
							return redirect(url_for('root'))

						cur.execute("INSERT INTO post (post_thread, post_content, post_owner, post_time) VALUES (?,?,?,strftime('%s','now'))", \
							(request.form['threadID'], strip_tags(request.form['content']), session['username'],))
						db.commit()
						
						print("Post created successfully")
						return redirect(url_for('root'))

		except KeyError:
			pass
		
		print("Could not make post. Paramiter error")
		return redirect(url_for('root'))
	else:
		return redirect(url_for('root'))

@app.route("/rm_post", methods=['POST'])
def rm_post():
	# Post only route for deleting posts
	# redirect to root with warning if invalid
	# Requires active session, requires session to be owner of post

	if request.method == 'POST':
		try:
			if(session['username']):
				db = get_db()
				cur = db.cursor()
				cur.execute("SELECT post_id, post_owner, post_active FROM post WHERE post_id = ?", (request.form['postID'],))
				data = cur.fetchall()

				if len(data) == 0:
					print("Could not find post relating to this id")
					return redirect(url_for('root'))
				
				if data[0][1] == session['username'] or session['status'] > 0:
					cur.execute("UPDATE post SET post_active = 'FALSE' WHERE post_id = ?",(request.form['postID'],))
					db.commit()
					print("Post status updated successfully")
					return redirect(url_for('root'))
				else:
					print("Could not remove post, not authorised")
					return redirect(url_for('root'))

		except KeyError:
			pass
			
		print("Could not update post status, paramiter error")
		return redirect(url_for('root'))
	else:
		return redirect(url_for('root'))

@app.errorhandler(404)
def notfound(e):
	return render_template("404.html")


if __name__ == "__main__":
	init(app)
	app.run(host=app.config['ip_address'],
	 port=int(app.config['port']))