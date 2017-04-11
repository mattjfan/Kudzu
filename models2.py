# Kudzu V2 Models
from peewee import *
import datetime
import os

from flask_login import UserMixin
from flask_bcrypt import generate_password_hash, check_password_hash

DATABASE = SqliteDatabase(
	os.path.join(
		os.path.dirname(os.path.realpath(__file__)),
		'social.db'
	),
	threadlocals=True  # will this work on server?
)

class NotUnique(Exception):
    pass
	
class User(UserMixin, Model):
	username = CharField(unique=True)
	first_name = CharField()  # no validation to exclude numbers...
	last_name = CharField()
	email = CharField(unique=True)
	password = CharField(max_length=100)
	joined_at = DateTimeField(default=datetime.datetime.now)
	bio = TextField(default='')
	is_admin = BooleanField(default=False)
	suspended = BooleanField(default=False)

	class Meta:
		database = DATABASE
		order_by = ('-joined_at',)

	@classmethod
	def create_user(cls, username, email, password, first_name, last_name, admin=False,bio=''):
		try:
			cls.create(
				first_name=first_name.title(),
				last_name=last_name.title(),
				username=username.lower(),
				email=email.lower(),
				password=generate_password_hash(password),
				bio=bio,
				is_admin=admin)
			Project.make_project(username=username, project_name='default')  # generate a default project directory for the user
		except IntegrityError:
			pass
	def get_id(username):
		if User.select().where(User.username==username).exists():
			my_user=User.get(User.username==username)
			return my_user.id
		return None
	def get_username(id):
		if User.select().where(User.id==id).exists():
			my_user=User.get(User.id==id)
			return my_user.username
		return None
	def update_bio(username,new_bio):
		try:
			my_user=User.get(User.username==username)
			query=my_user.update(bio=new_bio)
			query.execute()
		except:print("It didnt work...")
	def get_user_info(username):
		try:
			my_user=User.get(User.username==username)
			
			return ({
			'username':my_user.username,
			'first_name':my_user.first_name,
			'last_name':my_user.last_name,
			'email':my_user.email,
			'joined_at':prettify_timestamp(my_user.joined_at),
			'bio':my_user.bio,
			'is_admin':my_user.is_admin,
			'is_suspended':my_user.suspended
			})
			
		except:
			raise NotUnique

class Post_Index(Model):  # Reference info for 'all' post data
	timestamp = DateTimeField(default=datetime.datetime.now)
	privacy = CharField(default='public')
	owner = ForeignKeyField(User)
	flagged = BooleanField(default=False)
	deleted = BooleanField(default=False)
	ref_id = IntegerField()
	ref_type = CharField()

	class Meta:
		database = DATABASE
		order_by = ('-timestamp',)
	def make_index(username,ref_id,ref_type,privacy='public'):
		if Post_Index.select().where((Post_Index.ref_id==ref_id)&(Post_Index.ref_type==ref_type)).exists():print ('buga buga bug')
		else:
			print('some shit is happening')
			Post_Index.create(ref_id=ref_id,ref_type=ref_type,owner=User.select().where(User.username == username))
	
	def load_page(username, page=1, posts_per_page=10):
		posts = []
		for post_id in Post_Index.select().where(((Post_Index.privacy == 'public') | (Post_Index.owner == User.select().where(User.username==username))) & (~Post_Index.deleted)).paginate(page, posts_per_page):
			posts.append(Post_Index.unpack_post(post_id))	
			# ADD CODE TO RETRIEVE POSTS FROM RESPECTIVE MODELS
			# APPEND UNWRAPPED POSTS TO THE LIST 'posts'
		return posts
		
	def unpack_post(post_id):#Pass a selected post_index object
		if post_id.ref_type=='trade':
			return Trade.unpack_trade(Trade.get(Trade.id==post_id.ref_id))
		if post_id.ref_type=='comment':
			return Comment.unpack_comment(Comment.get(Comment.id==post_id.ref_id))
		if post_id.ref_type=='link':
			return Link.unpack_link(Link.get(Link.id==post_id.ref_id))	
	def get_project_content(username,project_name='default'):
		posts=[]
		for post_id in Post_Index.select().where(((Post_Index.ref_type=='link')|(Post_Index.ref_type=='trade'))&(Post_Index.owner==User.select().where(User.username==username))):
			print(Post_Index.unpack_post(post_id))
			if post_id.ref_type=='link':
				object= Link.get(Link.id==post_id.ref_id)
			if post_id.ref_type=='trade':
				object= Trade.get(Trade.id==post_id.ref_id)
			if object.project.name==project_name:
				posts.append(Post_Index.unpack_post(post_id))
		return posts
	@classmethod
	def do_button_action(cls,username,post_id):
		post_id=int(post_id)
		#print(post_id+3)
		if cls.select().where(cls.id==post_id).exists():
			my_post=cls.get(cls.id==post_id)
			print (my_post)
			if my_post.ref_type=='trade':
				Trade.toggle_trade_button(username,post_id)
			

	def DEBUG_count_post_ids():
		count=0
		for post_id in Post_Index.select():
			count+=1
		return count
class Project(Model):
	name = CharField()
	timestamp = DateTimeField(default=datetime.datetime.now)
	owner = ForeignKeyField(
		rel_model=User,
		related_name='projects'
	)

	class Meta:
		database = DATABASE
		order_by = ('-timestamp',)

	@classmethod
	def project_names_owned_by(cls, username):
		projects = []
		for project in Project.select():
			if project.owner.username == username:
				projects.append(project.name)
		return projects

	@classmethod
	def make_project(cls, username, project_name,privacy='public'):
		try:
			cls.get_or_create(owner=User.get(User.username == username), name=project_name.lower())
		except:
			raise NotUnique

"""
class Link(Model):
	title = CharField(unique=True)
	url = CharField(unique=True)
	owner = ForeignKeyField(
		rel_model=User,
		related_name='links')
	project = ForeignKeyField(
		rel_model=Project,
		related_name='links')

	class Meta:
		database = DATABASE
		order_by = ('-id',)

	@classmethod
	def link_is_new(url):
		if Link.select().where(Link.url == url).exists():
			return False
		else:
			return True
	def make_link(cls, link, username, project_name='default'):
		if Link.select().where(Link.url == link).exists():
			return Link.select().where(Link.url == link)
		else:
			try:
				if User.select().where(User.username == username).exists() and Project.select().where(
								Project.name == project_name,
								Project.owner == User.select().where(User.username == username)).exists():
					return cls.create(url=link, owner=User.select().where(User.username == username),
									  project=Project.select().where(Project.name == project_name,
																	 Project.owner == User.select().where(
																		 User.username == username)))
			except IntegrityError:
				pass

	def DEBUG_print_links():
		allLinks = []
		for link in Link.select():
			allLinks.append({'url': link.url, 'owner': link.owner.username, 'project': link.project.name})
		print(allLinks)

	def get_project_links(project_name,
						  username):  # IDK why it's raising this DOES NOT EXIST exception: guess we're going with an ugly work-around
		links = []
		for link in Link.select():
			if link.owner.username == username and link.project.name == project_name:
				links.append({'url': link.url, 'owner': link.owner.username, 'project': link.project.name})
		return links
"""
"""
class Post_depricated(Model):
	comment = TextField()  # do these fields need to be initialized?
	parent_ID = IntegerField(default=-1)  # -1 signifies no parent
	isPublic = TextField(default='public')
	timestamp = DateTimeField(default=datetime.datetime.now)

	user = ForeignKeyField(
		rel_model=User,
		related_name='posts'
	)
	link = ForeignKeyField(
		rel_model=Link,
		related_name='posts'
	)

	class Meta:
		database = DATABASE
		order_by = ('-timestamp',)

	@classmethod
	def make_post(cls, link, username, comment, isPublic='public'):
		if User.select().where(User.username == username).exists() and comment != "" and link != "":
			try:
				cls.create(
					link=Link.make_link(link, username),  # makes a link if one doens't already exist
					user=User.select().where(User.username == username),
					comment=comment,
					isPublic=isPublic
				)
			except IntegrityError:
				# raise ValueError("User Already Exists")
				pass

	def get_public_link_posts(link_url):
		all_posts = []
		for post in Post.select(Post.link.url == link_url):
			if post.isPublic == 'public' or post.user.username == username:
				latestPosts.append(Post.unpack_post(post))
		return latestPosts

	def get_all_posts():
		latestPosts = []
		for post in Post.select():
			latestPosts.append(Post.unpack_post(post))
		return latestPosts

	def get_public_posts(username):
		latestPosts = []
		for post in Post.select():
			if post.isPublic == 'public' or post.user.username == username:
				latestPosts.append(Post.unpack_post(post))
		return latestPosts

	def return_page(page=1, posts_per_page=10):
		my_posts = []
		for post in Post.select().where(Post.is_viewable(Post)).paginate(page, posts_per_page):
			# if post.isPublic=='public' or post.user.username==username:
			my_posts.append(Post.unpack_post(post))
		return my_posts

	def is_viewable(Post):
		True

	def unpack_post(post):  # needs to br passed a selected post object
		return ({'comment': post.comment,
				 'parent_ID': post.parent_ID,  # Need to implement functionality for parent_ID
				 'isPublic': post.isPublic,
				 'timestamp': prettify_timestamp(timestamp=post.timestamp),
				 'timestamp_raw': post.timestamp,
				 'user': post.user,
				 'link': post.link,
				 'link_name': post.link.url,
				 'username': post.user.username,
				 'is_admin': post.user.is_admin
				 })

	def DEBUG_print_posts():
		print(Post.get_all_posts())

	def get_my_posts(self):
		return Post.select().where(Post.user == self)

	def get_stream(self):
		return Post.select().where(Post.user == self)
"""

class Link(Model):
	url=CharField()
	title= CharField()
	comment = TextField() 
	project = ForeignKeyField(
		rel_model=Project,
		related_name='')
	class Meta:
		database = DATABASE
		order_by = ('id',)

	def link_is_new(url):
		if Link.select().where(Link.url == url).exists():
			return False
		else:
			return True
	@classmethod
	def make_link(cls, url, username, comment, title, project_name='default',privacy='public'):
		if User.select().where(User.username == username).exists() and comment != "" and url != ""  and Project.select().where(Project.name == project_name, Project.owner == User.select().where(User.username == username)).exists():
			if cls.link_is_new(url):
				my_link=cls.create(
					title=title,
					url=url,
					comment=comment,
					project=Project.select().where(Project.name == project_name, Project.owner == User.select().where(User.username == username))
					)
				Post_Index.make_index(username=username,ref_id=my_link.id,ref_type='link',privacy=privacy)
			else:raise NotUnique
	def unpack_link(link):
		post_id=Post_Index.get(ref_id=link.id,ref_type='link')
		return({
			'type':'link',
			'comment':link.comment,
			'url':link.url,
			'title':link.title,
			'project_name':link.project.name,
			'username':post_id.owner.username,
			'privacy':post_id.privacy,
			'time_stamp':prettify_timestamp(post_id.timestamp),
			'is_flagged':post_id.flagged,
			'post_id':post_id.id
		})
class Trade(Model):
	request = CharField()
	offer = CharField()
	comment = TextField()
	#accepted = BooleanField(default=False)#kind of redundant with below field...
	accepted_by = IntegerField(default=-1)#-1 indicates not accepted, not 'officially' implemented as Foreign Key Field...
	project = ForeignKeyField(
		rel_model=Project,
		related_name='')
	turned_in=False
	is_completed=False
	class Meta:
		database = DATABASE
		order_by = ('id',)
	@classmethod
	def make_trade(cls,username,request,offer,comment,project_name='default',privacy='public'):
		if User.select().where(User.username == username).exists():
			my_trade=cls.create(request=request,offer=offer,comment=comment,project=Project.select().where(Project.name == project_name, Project.owner == User.select().where(User.username == username)))
			#print('trade ID:{}'.format(my_trade.id))
			Post_Index.make_index(username=username,ref_id=my_trade.id,ref_type='trade',privacy=privacy)
	def unpack_trade(trade):
		is_accepted=False
		if trade.accepted_by !=-1:
			is_accepted=True
		post_id=Post_Index.get(ref_id=trade.id,ref_type='trade')
		return({
			'type':'trade',
			'id':trade.id,
			'project_name':trade.project.name,
			'request':trade.request,
			'offer':trade.offer,
			'comment':trade.comment,
			'is_accepted':is_accepted,
			'accepted_by':trade.accepted_by,
			'accepted_by_user':User.get_username(trade.accepted_by),
			'username':post_id.owner.username,
			'privacy':post_id.privacy,
			'time_stamp':prettify_timestamp(post_id.timestamp),
			'is_flagged':post_id.flagged,
			'comments':Comment.grab_comments(parent_id=trade.id, parent_type='trade'),
			'turned_in':trade.turned_in,
			'is_completed':trade.is_completed,
			'post_id':post_id.id
		})
	def accept_trade(username,post_id):#post_id
		my_post=Post_Index.get(Post_Index.id==post_id)
		if User.select().where(User.username==username).exists():
			try:
				print('I is trying')
				#my_trade==Trade.get(Trade.id==post_id.ref_id)
				query=Trade.update(accepted_by=User.get_id(username)).where(Trade.id==my_post.ref_id)
				query.execute()
			except:print('sadness...')

	def unaccept_trade(username,post_id):#post_id
		my_post=Post_Index.get(Post_Index.id==post_id)
		if User.select().where(User.username==username).exists():
			try:
				print('I is trying')
				#my_trade==Trade.get(Trade.id==post_id.ref_id)
				query=Trade.update(accepted_by=-1).where(Trade.id==my_post.ref_id)
				query.execute()
			except:print('sadness...')
	def toggle_trade_button(username,post_id):
		my_post=Post_Index.get(Post_Index.id==post_id)
		if my_post.ref_type == 'trade':
			my_trade=Trade.get(Trade.id==my_post.ref_id)
			if my_trade.accepted_by == -1:
				Trade.accept_trade(username,post_id)
			else:Trade.unaccept_trade(username,post_id)

class Pitch(Model):
	class Meta:
		database = DATABASE
		order_by = ('id',)

class Comment(Model):  # Allows comment annotation for *any 'post' type
	parent = ForeignKeyField(Post_Index)
	comment = TextField()
	class Meta:
		database = DATABASE
		order_by = ('id',)
	@classmethod
	def make_comment(cls,parent_id,parent_type,comment,username,privacy='public'):
		if User.select().where(User.username == username).exists():
			my_post=cls.create(
				parent=Post_Index.select().where(Post_Index.ref_id==parent_id,Post_Index.ref_type==parent_type),
				comment=comment
			)
			Post_Index.make_index(username=username,ref_id=my_post.id,ref_type='comment',privacy=privacy)
	def unpack_comment(comment):
		post_id=Post_Index.get(ref_id=comment.id,ref_type='comment')
		return({
			'type':'comment',
			'comment':comment.comment,
			'parent_id':comment.parent.ref_id,
			'parent_type':comment.parent.ref_type,
			'username':post_id.owner.username,
			'privacy':post_id.privacy,
			'time_stamp':prettify_timestamp(post_id.timestamp),
			'is_flagged':post_id.flagged,
			'post_id':post_id.id
		})
	def grab_comments(parent_id,parent_type):#Might not work...
		comments=[]
		for comment in Comment.select().where(Comment.parent==Post_Index.select().where((Post_Index.ref_id==parent_id)&(Post_Index.ref_type==parent_type))):
			comments.append(Comment.unpack_comment(comment))
		return comments
class Subscription(Model):
	timestamp = DateTimeField(default=datetime.datetime.now)
	subscriber = ForeignKeyField(  # am I doing that right?
		rel_model=User,
		related_name='subscriptions'
	)
	subscription = ForeignKeyField(
		rel_model=User,
		related_name='subscribers'
	)
	class Meta:
		database = DATABASE
		order_by = ('-timestamp',)

	@classmethod
	def subscribe_to(cls, username, subscription):
		if username != subscription:
			try:
				cls.get_or_create(subscriber=User.select().where(User.username == username),
								  subscription=User.select().where(User.username == subscription))
			except:
				pass
		else:
			pass
			
	@classmethod
	def unsubscribe_from(cls, username, subscription):
		if Subscription.is_subscribed(username,subscription):
			query=Subscription.delete().where((Subscription.subscriber==User.select().where(User.username == username))&(Subscription.subscription==User.select().where(User.username == subscription)))
			query.execute()

	# print('You cannot subscribe to yourself')
	def is_subscribed(username, subscription):
		if Subscription.select().where((Subscription.subscriber==User.select().where(User.username == username))&(Subscription.subscription==User.select().where(User.username == subscription))).exists():
			return True
		else:
			return False

	def DEBUG_print_subscriptions():
		all_subscriptions = []
		for subscription in Subscription.select():
			print('{} is subscribed to {}'.format(subscription.subscriber.username, subscription.subscription.username))


class Group(Model):
	timestamp = DateTimeField(default=datetime.datetime.now)
	group_name = CharField(unique=True)
	isPublic = BooleanField(default='public')

	class Meta:
		database = DATABASE
		order_by = ('-timestamp',)


class Membership(Model):
	user = ForeignKeyField(rel_model=User, related_name='groups')
	group = ForeignKeyField(rel_model=Group, related_name='members')


class Project_Links(Model):  # hacky way for link connections... bc I don't want to break existing code...
	project = ForeignKeyField(
		rel_model=Project,
		related_name='pl')
	link = ForeignKeyField(
		rel_model=Link,
		related_name='pl')

	class Meta:
		database = DATABASE
		order_by = ('-id',)

	def make_linkage(project_name, link_name):
		pass
		
class Direct_Message(Model): #NEED TO IMPLEMENT
	sender=ForeignKeyField(rel_model=User,related_name='dmss')
	receiver=ForeignKeyField(rel_model=User,related_name='dmsr')
	message = TextField()
	timestamp=DateTimeField(default=datetime.datetime.now)
	class Meta:
		database = DATABASE
		order_by = ('timestamp',)
	def send_message(sender,receiver,message):	
		try:
			if message != "":
				Direct_Message.create(sender=User.select().where(User.username==sender), receiver=User.select().where(User.username==receiver), message=message)
			print ('dm created')
		except:pass
	def get_messages(user):
		dms=[]
		print ('starting shit')
		for dm in Direct_Message.select().where((Direct_Message.sender==User.select().where(User.username == user)) | (Direct_Message.receiver==User.select().where(User.username == user) )):
			print('adding shit')
			sent_by_user=False
			if dm.sender.username==user:
				sent_by_user=True
			dms.append({'sender':dm.sender.username,'receiver':dm.receiver.username,'message':dm.message,'sent_by_user':sent_by_user})
		return dms
	def get_conversation(main_user,other_user):
		dms=[]
		print ('starting shit')
		for dm in Direct_Message.select().where(((Direct_Message.sender==User.select().where(User.username == main_user)) &(Direct_Message.receiver==User.select().where(User.username == other_user)))
					| ((Direct_Message.sender==User.select().where(User.username == other_user)) &(Direct_Message.receiver==User.select().where(User.username == main_user)) )):
			print('adding shit')
			sent_by_user=False
			if dm.sender.username==main_user:
				sent_by_user=True
			dms.append({'sender':dm.sender.username,'receiver':dm.receiver.username,'message':dm.message,'sent_by_user':sent_by_user})
		return dms
class Link_Update(Model): #NEED TO IMPLEMENT
	class Meta:
		database = DATABASE
		order_by = ('-id',)		
class Change_Log(Model):
	class Meta:
		database = DATABASE
		order_by = ('-id',)		
def simple_timestamp_translator(timestamp):
	pass
	
def prettify_timestamp(timestamp):
	hour = timestamp.hour
	hemi = 'AM'
	if timestamp.hour > 12:
		hour -= 12
		hemi = 'PM'
	if timestamp.hour == 0:
		hour = 12
	minute = str(timestamp.minute)
	if timestamp.minute < 10:
		minute = '0{}'.format(timestamp.minute)
	months = {
		1: 'Jan',
		2: 'Feb',
		3: 'Mar',
		4: 'Apr',
		5: 'May',
		6: 'Jun',
		7: 'Jul',
		8: 'Aug',
		9: 'Sep',
		10: 'Oct',
		11: 'Nov',
		12: 'Dec'
	}
	month = months[timestamp.month]
	return "{} {}, {} ({}:{} {})".format(month, timestamp.day, timestamp.year, hour, minute, hemi)
class Debug_Tools:
	def delete_database():
		a = Link.delete().where(True)
		a.execute() 
		b = Post_Index.delete().where(True)
		b.execute() 
		c = Trade.delete().where(True)
		c.execute() 
		d = Project.delete().where(True)
		d.execute() 
		e = Pitch.delete().where(True)
		e.execute() 
		f = Comment.delete().where(True)
		f.execute() 
		g = Subscription.delete().where(True)
		g.execute() 
		h = Group.delete().where(True)
		h.execute() 
		i = Direct_Message.delete().where(True)
		i.execute() 

def initialize():
	DATABASE.connect()
	DATABASE.create_tables([User], safe=True)
	DATABASE.create_tables([Link], safe=True)
	DATABASE.create_tables([Post_Index], safe=True)
	#DATABASE.create_tables([Post], safe=True)
	DATABASE.create_tables([Trade], safe=True)
	DATABASE.create_tables([Direct_Message], safe=True)
	DATABASE.create_tables([Pitch], safe=True)
	DATABASE.create_tables([Comment], safe=True)
	DATABASE.create_tables([Project], safe=True)
	DATABASE.create_tables([Subscription], safe=True)
	DATABASE.create_tables([Group], safe=True)
	DATABASE.create_tables([Project_Links], safe=True)
	DATABASE.close()
