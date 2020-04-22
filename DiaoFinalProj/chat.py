#Xingjian Diao xid32
#python3 chat.py 
#export FLASK_APP=chat.py
#flask initdb
#flask run

import time
import base64
import os
import json
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash, _app_ctx_stack, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import or_, and_
from models import db, User, Chatroom, Message, MessagePersonal, Friend, PendingFriend, ExistingFriend

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'chat.db')
SQLALCHEMY_TRACK_MODIFICATIONS = True
SECRET_KEY = 'development key'
app.config.from_object(__name__)
db.init_app(app)
@app.cli.command('initdb')
def initdb_command():
	db.drop_all()
	db.create_all()
	print('Initialized the database.')

@app.before_request
def before_request():
	g.user = None
	if 'user_id' in session:
		g.user = User.query.filter_by(user_id=session['user_id']).first()

def get_user_id(username):
	rv = User.query.filter_by(username=username).first()
	return rv.user_id if rv else None

def get_all_user_id():
	rv = User.query.all()
	return rv if rv else None

def get_chat_id(chat_name):
	rv = Chatroom.query.filter_by(chat_name=chat_name).first()
	return rv.chatroom_id if rv else None

def get_message_id(text):
	rv = Message.query.filter_by(text=text).first()
	return rv.message_id if rv else None

def get_all_rooms():
	rv = Chatroom.query.order_by(Chatroom.chat_name).all()
	return rv if rv else []

def get_chat_by_name(chat_name):
	rv = Chatroom.query.filter_by(chat_name=chat_name).first()
	return rv if rv else None

def get_all_messages(chat_name):
	rv = Message.query.filter_by(chat_name=chat_name).all()
	return rv if rv else []

def get_all_messages_of_two_user(fromuser, touser):
	rv = MessagePersonal.query.filter(or_(and_(MessagePersonal.fromuser==fromuser, MessagePersonal.touser==touser),\
							and_(MessagePersonal.fromuser==touser, MessagePersonal.touser==fromuser))).order_by(MessagePersonal.pub_date).all()
	print(rv)
	return rv if rv else []

def check_availabilty(chat_name):
	rv = Chatroom.query.filter_by(chat_name=chat_name).first()
	return rv if rv else None
	
def get_all_friend_requests(user2, current_user):
	rv = PendingFriend.query.filter_by(user2=current_user).all()
	return rv if rv else []	

def format_datetime(timestamp):
	"""Format a timestamp for display."""
	return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')

# CHECK FRIENDSHIP METHOD
def check_pending_friend_table(user1, user2):
	pending_res = PendingFriend.query.filter_by(user1=user1,user2=user2).all()
	frd_res = ExistingFriend.query.filter_by(user1=user1,user2=user2).all()
	print(pending_res)
	if pending_res: # why !=None doesnt work???
		#Friend request already exists
		return 1
	elif frd_res:
		#You two are already friends
		return 2
	else:
		#Sends friend request
		return 3
	return None


@app.route('/')
@app.route('/index')
def index():
	rooms = get_all_rooms()
	allusers = get_all_user_id()
	print("@@@@")
	print(allusers)
	if g.user:
		user = User.query.filter_by(user_id=g.user.user_id).first()
		user.current_room_id = -1
		db.session.commit()

	return render_template('index.html', rooms=rooms, allusers=allusers)

@app.route('/login', methods=['GET', 'POST'])
def login():
	"""Logs the user in."""
	if g.user:
		return redirect(url_for('index'))
	error = None
	if request.method == 'POST':
		user = User.query.filter_by(username=request.form['username']).first()
		if user is None:
			error = 'Invalid username'
		elif user.password != request.form['password']:
			error = 'Invalid password'
		else:
			session['user_id'] = user.user_id
			if user.current_room_id != -1:
				return redirect(url_for('chat', chatroom_id=user.current_room_id))
			else:
				return redirect(url_for('index'))
	return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
	error = None
	if request.method == 'POST':
		if not request.form['username']:
			error = 'You need to enter a username'
		elif not request.form['password']:
			error = 'You need to enter a password'
		elif request.form['password'] != request.form['password2']:
			error = 'Two passwords do not match'
		elif get_user_id(request.form['username']) is not None:
			error = 'The username is already used by others'
		else:
			db.session.add(User(request.form['username'], request.form['password'],request.form['first_name'], request.form['last_name'], -1))
			db.session.commit()
			return redirect(url_for('login'))
	return render_template('register.html', error=error)

### Added Profile Page 
@app.route('/profile',  methods=['GET', 'POST'])
def profile ():
	
	if 'user_id' in session:
		g.user = User.query.filter_by(username=g.user.username).first()
		if request.method == 'POST':
			if not request.form['username']:
				error = 'You need to enter a username'
				flash('You need to enter a username')
			elif not request.form['password']:
				error = 'You need to enter a password'
				flash('You need to enter a password')
			elif request.form['password'] != request.form['password2']:
				error = 'Two passwords do not match'
			# elif get_user_id(request.form['username']) is not None:
			# 	error = 'The username is already used by others'
			else:
				g.user.username = request.form['username']
				g.user.password = request.form['password']
				g.user.first_name = request.form['first_name']
				g.user.last_name = request.form['last_name']
				db.session.add(g.user)
				db.session.commit()
				flash('Profile has been updated!', 'success')
				return redirect(url_for('profile'))

	return render_template('profile.html', user= g.user)
	
###

@app.route('/logout')
def logout():
	"""Logs the user out."""
	curr_room = g.user.current_room_id
	session.pop('user_id', None)
	return redirect(url_for('index'))

@app.route('/chat/<chatroom_id>')
def chat(chatroom_id):
	error = None
	chatroom = Chatroom.query.get(chatroom_id)
	messages = get_all_messages(chatroom.chat_name)
	if g.user:
		g.user.current_room_id = chatroom_id
		user = User.query.filter_by(user_id=g.user.user_id).first()
		user.current_room_id = chatroom_id
		db.session.commit()
	return render_template('chat.html', chatroom=chatroom, messages=messages)

@app.route('/chatwithuser/<username>')
def chatwithuser(username):
	error = None
	print(g.user)
	messages = get_all_messages_of_two_user(g.user.username, username)
	for msg in messages:
		if msg.image:
			msg.image = str(base64.b64encode(msg.image), 'utf-8')
	print(username)
	return render_template('chatwithuser.html', messages=messages, tousername=username)

@app.route('/get_new_messages', methods=['POST'])
def get_new_messages():
	t = int(float(request.form['timestamp']) * 0.001)
	msgs = Message.query.filter_by(chat_name=request.form['chat_name']).all()
	
	for msg in msgs:
		if msg.pub_date > t:
			return jsonify({
				"author": msg.author,
				"chat_name": msg.chat_name,
				"text": msg.text,
				"pub_date": format_datetime(msg.pub_date),
				"img": str(base64.b64encode(msg.image), 'utf-8') if msg.image else ""
				})
	return "null"

@app.route('/add_message', methods=['POST'])
def add_message():
	"""Registers a new message for the user."""
	if 'user_id' not in session:
		abort(401)
	if request.form['text']:
		new_msg = Message(request.form['author'], request.form['chat_name'], request.form['text'], int(time.time()))
		db.session.add(new_msg)
		db.session.commit()
	return jsonify({
			"author": new_msg.author,
			"chat_name": new_msg.chat_name,
			"text": new_msg.text,
			"pub_date": format_datetime(new_msg.pub_date)
		})


@app.route('/add_message_two_user', methods=['POST'])
def add_message_two_user():
	"""Registers a new message for the user."""
	if 'user_id' not in session:
		abort(401)
	if request.form['text']:
		new_msg = MessagePersonal(request.form['fromuser'], request.form['touser'], request.form['text'], int(time.time()), None)
		db.session.add(new_msg)
		db.session.commit()
	return jsonify({
			"fromuser": new_msg.fromuser,
			"touser": new_msg.touser,
			"text": new_msg.text,
			"pub_date": format_datetime(new_msg.pub_date)
	})

@app.route('/add_image_two_user', methods=['POST'])	
def add_image_two_user():
	if 'user_id' not in session:
		abort(403)
	if request.method == 'POST':
		if not 'file' in request.files:
			abort(403)
		file = request.files.get('file')
		filein = file.read()
		try:
			new_msg = MessagePersonal(request.form['fromuser'], request.form['touser'], "image", int(time.time()), filein)
			db.session.add(new_msg)
			db.session.commit()
		except Exception as e:
			abort(500)

		return jsonify({
			"fromuser": new_msg.fromuser,
			"touser": new_msg.touser,
			"text": new_msg.text,
			"pub_date": format_datetime(new_msg.pub_date),
			'image' : str(base64.b64encode(new_msg.image), 'utf-8')
		})
	else:
		abort(403)


@app.route('/create_room', methods=['POST'])
def create_room():
	if check_availabilty(request.form['chat_name']):
		flash("Sorrry, that name is unavailable")
	else:
		db.session.add(Chatroom(chat_name=request.form['chat_name'], creator_id=request.form['creator_id']))
		db.session.commit()
	return redirect(url_for('index'))


#####################CASPER#####################



# this method checks whether in pending_friend and friendship
# if not, sends friend request

#	- need to check if user is registered in user_profile
#	- cannot send request to self
# 	- otherway around for pending friend request and existing friend request
@app.route('/add_friend', methods=['POST'])
def add_friend():

	user1 = request.form['frd_initiator_id']
	user2 = request.form['friend_to_add_id']
	check_res = check_pending_friend_table(user1,user2)

	if check_res == 1:
		flash("You already have a pending friend request")
	elif check_res == 2:
		flash("You two are already friends")
	elif check_res == 3:
		try:
			db.session.add(PendingFriend(user1=user1, user2=user2))
			db.session.commit()
			all_pending = PendingFriend.query.all()
			print('pendingquery is %s here' %all_pending)

			flash("You have sent %s a friend request." %user2)
		except Exception as inst:
		    print(type(inst))
		    print(inst.args) # arguments stored in .args
		    print(inst)
	
	return redirect(url_for('index'))


# view friend list
@app.route('/view_friends_list')
def view_friends_list():
	# if request.method=='POST':
	all_friends = ExistingFriend.query.filter_by(user2=g.user.user_id).all()
		
	for frd in all_friends:
		return render_template('friends.html', all_friends=all_friends)

	# else:
	# 	print("no post?")
	
	return render_template('friends.html')



#https://stackoverflow.com/questions/22640996/change-text-on-submit-button-after-submission
#view friend requests
@app.route('/view_friend_requests')
def view_friend_requests():

	# if request.method == 'POST':
	user1 = g.user.user_id #user1=g.user.user_id
	friend_requests = get_all_friend_requests(PendingFriend.user2,g.user.user_id)
	print('_________________')
	print(friend_requests)
	print('__________________')

	for fr in friend_requests:
		recordObject = {'user_initiated_req': fr.user1,
           				'user_receive_req': fr.user2}
		flash("You have received a friend request from user %s ." %str(fr.user1))
	return render_template('friend_req.html', friend_requests=friend_requests)

	#friend_requests = #get friend requests in db method
	#for each friend req, print it out in friend_req.html
	# else:
	# 	print("no post?")
	# 	return redirect(url_for('index'))

	return redirect(url_for('index'))

#accept friend requests
@app.route('/accept_friend_request', methods=['POST'])
def accept_friend_request():
	if request.method == 'POST':
		#for all the queries 
		
		user1 = request.form['creating_user']
		user2 = request.form['receiving_user']

		# for accepting all friends
		#friend_requests = PendingFriend.query.filter_by(user2=g.user.user_id).all()

		friend_requests = PendingFriend.query.filter_by(user1 = user1, user2=g.user.user_id).all()
		for fr in friend_requests: #doesnt really run cuz only 1 resultset

			print_db = ExistingFriend.query.all()
			print("this is existing friend - before")
			print(print_db)
			print_db2 = PendingFriend.query.all()
			print("this is pending friend - before")
			print(print_db2)

			# add to friends list
			db.session.add(ExistingFriend(user1=fr.user1, user2=fr.user2))

			# delete from pending list
			PendingFriend.query.filter(PendingFriend.user1==fr.user1, PendingFriend.user2==fr.user2).delete()
			db.session.commit()

			print_db = ExistingFriend.query.all()
			print("this is existing friend - after")
			print(print_db)
			print_db2 = PendingFriend.query.all()
			print("this is pending friend - after")
			print(print_db2)
			
			# return render_template('index.html')
			return redirect(url_for('index'))





#delete friend
@app.route('/remove_friend', methods=['POST'])
def remove_friend():
	if request.method=='POST':
		user1 = request.form['friend_of_current_user']
		user2 = request.form['current_user']

		# delete from existing list
		ExistingFriend.query.filter(ExistingFriend.user1==user1, ExistingFriend.user2==user2).delete()
		db.session.commit()

	# return render_template('index.html')
	return redirect(url_for('index'))

# Go play game
@app.route('/play_game', methods=['POST'])
def play_game():
	if request.method=='POST':
		# frog = frog.jpeg
		return render_template('game.html')

	#return render_template('index.html')
	return redirect(url_for('index'))


##############################^^^^^^up




@app.route('/leave')
def leave():
	return redirect(url_for('index'))

@app.route('/delete', methods=['POST'])
def delete():
	db.session.delete(Chatroom.query.get(request.form['chatroom_id']))
	db.session.commit()
	return redirect(url_for('index'))

@app.route('/space')
def space():
	return render_template('info.html')	

app.jinja_env.filters['datetimeformat'] = format_datetime