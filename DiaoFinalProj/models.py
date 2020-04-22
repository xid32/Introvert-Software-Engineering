from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model): 
	user_id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(24), nullable=False, unique=True)
	password = db.Column(db.String(80), nullable=False)
	first_name = db.Column(db.String(24), nullable=False)
	last_name = db.Column(db.String(24), nullable=False)
	current_room_id = db.Column(db.Integer, nullable=False)
	
	def __init__(self, username, password, first_name, last_name, current_room_id):
		self.username = username
		self.password = password
		self.first_name = first_name
		self.last_name = last_name
		self.current_room_id = current_room_id

	def __repr__(self):
		return '<User {}>'.format(self.username)

#request from username_from to username_to to be friend
class Friend(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username_from = db.Column(db.String(24), nullable=False, unique=True)
	username_to = db.Column(db.String(80), nullable=False)
	agree = db.Column(db.Boolean, nullable=False)
	msg = db.Column(db.String(256), nullable=False)
	
	def __init__(self, username, password, current_room_id):
		self.username = username
		self.password = password
		self.current_room_id = current_room_id

	def __repr__(self):
		return '<User {}>'.format(self.username)

class Chatroom(db.Model):
	chatroom_id = db.Column(db.Integer, primary_key=True)
	chat_name = db.Column(db.String(24), nullable=False, unique=True)
	creator_id = db.Column(db.Integer, nullable=False)

	def __init__(self, chat_name, creator_id):
		self.chat_name = chat_name
		self.creator_id = creator_id

	def __repr__(self):
		return '<Chatroom Name {}>'.format(self.chat_name)

class Message(db.Model):
	messgae_id = db.Column(db.Integer, primary_key=True)
	author = db.Column(db.String(24), nullable=False)
	chat_name = db.Column(db.String(24), nullable=False)
	text = db.Column(db.String(200), nullable=False)
	pub_date = db.Column(db.Integer)

	def __init__(self, author, chat_name, text, pub_date):
		self.author = author
		self.chat_name = chat_name
		self.text = text
		self.pub_date = pub_date

	def __repr__(self):
		return '<Message {}'.format(self.messgae_id)

#message send by one person to another person
class MessagePersonal(db.Model):
	messgae_id = db.Column(db.Integer, primary_key=True)
	fromuser = db.Column(db.String(24), nullable=False)
	touser = db.Column(db.String(24), nullable=False)
	text = db.Column(db.String(200), nullable=False)
	pub_date = db.Column(db.Integer)
	image = db.Column(db.LargeBinary(length=204800), nullable=True)

	def __init__(self, fromuser, touser, text, pub_date, image):
		self.fromuser = fromuser
		self.touser = touser
		self.text = text
		self.pub_date = pub_date
		self.image = image

	def __repr__(self):
		return '<MessagePersonal {}'.format(self.messgae_id)

		######################################################## down1

# friend DB
class PendingFriend(db.Model):
	# __init__ = (
 #        ForeignKeyConstraint(
 #            ['user1', 'user2'],
 #            ['User.user_id', 'User.user_id']
 #        ),
	# )
	#primary key ensures that it is unique. so 1-2, 1-2 duplicates wont happen
	user1 = db.Column(db.Integer, db.ForeignKey(User.user_id), primary_key=True, nullable=False)
	user2 = db.Column(db.Integer, db.ForeignKey(User.user_id, ondelete="CASCADE"), primary_key=True, nullable=False)
	pub_date = db.Column(db.Integer)

	# def __init__(self, user1, user2, pub_date):
	# 	self.user1 = user1
	# 	self.user2 = user2
	# 	self.pub_date = pub_date


class ExistingFriend(db.Model):
 	user1 = db.Column(db.Integer, db.ForeignKey(User.user_id), primary_key=True, nullable=False)
 	user2 = db.Column(db.Integer, db.ForeignKey(User.user_id, ondelete="CASCADE"), primary_key=True, nullable=False)


######################################################## up1
