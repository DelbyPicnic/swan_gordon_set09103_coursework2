CREATE TABLE IF NOT EXISTS thread (
	thread_id integer PRIMARY KEY AUTOINCREMENT,
	thread_title text,
	thread_content text,
	thread_owner varchar,
	thread_active boolean DEFAULT TRUE,
	thread_time integer
);

CREATE TABLE IF NOT EXISTS post (
	post_id integer PRIMARY KEY AUTOINCREMENT,
	post_thread integer,
	post_content text,
	post_owner integer,
	post_active boolean DEFAULT TRUE,
	post_time integer,

	FOREIGN KEY (post_thread) REFERENCES thread (thread_id)
	FOREIGN KEY (post_owner) REFERENCES user (user_id)
);

CREATE TABLE IF NOT EXISTS user (
	user_id integer PRIMARY KEY AUTOINCREMENT,
	user_level integer DEFAULT 0,
	user_name varchar,
	user_email varchar UNIQUE,
	user_password varchar,
	user_active boolean DEFAULT TRUE
);