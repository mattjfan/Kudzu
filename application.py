# Kudzu App v2
import flask
from flask_login import LoginManager
import models2 as models
from flask_bcrypt import generate_password_hash, check_password_hash
import os
from werkzeug import secure_filename
application = flask.Flask(__name__)
DEBUG=True
application.config['UPLOAD_FOLDER']=os.path.dirname(os.path.realpath(__file__))+'//static//profile_pics'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
# PORT=8000
# HOST='0.0.0.0'
application.secret_key = '[][213*(@!321aasdbFAS(*!@#afA0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
"""
login_manager=LoginManager()
login_manager.init_app(application)
login_manager.login_view = 'login'
"""
@application.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

@application.route('/register')
def register():
	return flask.render_template('registration.html')



@application.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if flask.request.method == 'POST':
		try:
			user = models.User.get(models.User.username == flask.request.form['username'])
		except models.DoesNotExist:
			# flash("email and password don't match", "error")
			# ^flashing doesn't work
			error = "Credentials don't match. Please try again."
			return flask.render_template('login.html', error=error)
		if check_password_hash(user.password, flask.request.form['password']):
			flask.session['username'] = flask.request.form['username'].lower()
			return flask.redirect(flask.url_for('redirect_to_main'))
	return flask.render_template('login.html')


"""
	if 'username' in session:
		return 'Logged in as {}'.format( escape(session['username']))"""
@application.route('/')
@application.route('/home')
def redirect_to_main():
	return flask.redirect('/home/1')

@application.route('/home/<int:page>', methods=['GET', 'POST'])
def main(page):
	postS_PER_PAGE=10
	error = None
	if 'username' in flask.session:
		if flask.request.method == 'POST':
			if flask.request.form['submit'][0]=='$':
				print ("I'm in the main app, and I'm doing some SHIT")
				print ("I'm lookin' for post id number {}".format(flask.request.form['submit'][1:]))
				models.Post_Index.do_button_action(username=flask.session['username'],post_id=flask.request.form['submit'][1:])
				
				
			if flask.request.form['submit'] == 'share':
				try:
					models.Link.make_link(url=flask.request.form['link'],
										  username=flask.session['username'],
										  comment=flask.request.form['comment'],
										  title=flask.request.form['title'],
										  project_name=flask.request.form['project'],
										  privacy=flask.request.form['privacy'])
					#return flask.redirect(flask.url_for('flush'))
				except models.NotUnique:
					pass
					#return flask.redirect(flask.url_for('flush'))
				except:
					error = "Input invalid"
					#return flask.redirect(flask.url_for('flush'))
				
			if flask.request.form['submit'] == 'trade':	
				print("I got your little form")
				try:
					print("tryin to make the trade!")
					models.Trade.make_trade(username=flask.session['username'],
											request=flask.request.form['request'],
											offer=flask.request.form['offer'],
											comment=flask.request.form['comment'],
											project_name=flask.request.form['project'],
											privacy=flask.request.form['privacy'])
				except:print('oops...')
				
			return flask.redirect('/')
		latest_posts = models.Post_Index.load_page(page=page,posts_per_page=postS_PER_PAGE,username=flask.session['username'])
		return (flask.render_template('mainpage.html', latest_posts=latest_posts, error=error,
									  username=flask.session['username'],
									  user_id=models.User.get_id(username=flask.session['username']),
									  projects=models.Project.project_names_owned_by(flask.session['username']),
									  page=page,
									  posts_per_page=postS_PER_PAGE
									  ))
	else:
		return flask.redirect(flask.url_for('login'))


@application.route('/flush/<redirect_url>')
def flush(redirect_url):
	return flask.redirect(flask.url_for(redirect_url))
	
@application.route('/flush/<re1>/<re2>')
def flush2(re1,re2):
	return flask.redirect('/{}/{}'.format(re1,re2))
	
@application.route('/projects')
def projects_redirect():
	return flask.redirect('/projects/{}'.format(flask.session['username']))

@application.route('/trades')
def trades_index():
	return flask.render_template('trades_index.html',username=flask.session['username'])

@application.route('/projects/<username>',methods=['GET', 'POST'])
def projects_index(username):
	if flask.request.method == 'POST':
		print('you said post')
		error=None
		if flask.request.form['submit']=='create_project':
			print('rhymes with ghost')
			try:
				models.Project.make_project(username=flask.session['username'], project_name=flask.request.form['title'],privacy=flask.request.form['privacy'])
				print('I did it')
			except:
				error='Project already exists'
				print('already exists...')
		return flask.redirect('/flush/projects/{}'.format(username))
		
	context = {'projects': models.Project.project_names_owned_by(username), 'username': flask.session['username'],
			   'other_user': username}
	try:context['error']=error
	except:context['error']=None
	#if flask.request.method == 'POST':
	return flask.render_template('projects.html', **context)
	


@application.route('/projects/<username>/<project_name>')
def project(username, project_name):
	context = {
		'username': username,
		'project_name': project_name,
		'posts': models.Post_Index.get_project_content(username=username, project_name=project_name)
	}
	return flask.render_template('project_page.html', **context)


@application.route('/logout')
def logout():
	# remove the username from the session if it's there
	flask.session.pop('username', None)
	return flask.redirect(flask.url_for('login'))


@application.route('/profile')
def my_profile():
	return flask.redirect('/profile/{}'.format(flask.session['username']))

@application.route('/post/<int:post_id>')
def post(post_id):

	context={'post_id':post_id,'username': flask.session['username']}
	return flask.render_template('trade.html', **context)



@application.route('/profile/<username>',methods=['GET', 'POST'])
def profile_page(username):
	print('on the right page')
	if flask.request.method == 'POST':
		print('user is posting')
		if flask.request.form['submit']=='follow':
			print('Trying to follow')
			models.Subscription.subscribe_to(username=flask.session['username'], subscription=username)
		if flask.request.form['submit']=='unfollow':
			models.Subscription.unsubscribe_from(username=flask.session['username'], subscription=username)
		return flask.redirect('/flush/profile/{}'.format(username))
		print('trace going through')
	user = models.User.get(models.User.username == username)
	first_name = user.first_name
	  # makes sharing profile page links broken though...
	context = {'username':flask.session['username'],
				'user_info':models.User.get_user_info(username),
				'is_subscribed':models.Subscription.is_subscribed(flask.session['username'], username)}
	if username == flask.session['username']:context['is_user']=True			  
	else:context['is_user']=False
	
	return flask.render_template('profile.html', **context)


# return "This is the profile page for {}".format(username)

@application.route('/links<int:linkNum>')
def checkLinkFunctionality(linkNum):
	context = {'linkNum': linkNum,'username': username}
	return flask.render_template('linkCheck.html', **context)


@application.route('/messages/<username>')
def direct_messages(username):
	context = {'user_info':models.User.get_user_info(username),'username': flask.session['username'],
			'messages':models.Direct_Message.get_conversation(flask.session['username'],username)}
	return flask.render_template('direct_messages.html', **context)
	
	
@application.route('/update_profile_pic', methods=['GET','POST'])
def upload_file():
	f = flask.request.files['file']
	if flask.request.method == 'POST' and '.' in f.filename and f.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
		extension=f.filename.rsplit('.', 1)[1].lower()
		file_name=secure_filename('{}.{}'.format(flask.session['username'],extension))
		f.save(os.path.join(application.config['UPLOAD_FOLDER'],file_name))
	return flask.redirect(flask.url_for('my_profile'))
	
if __name__ == '__main__':
	models.initialize()
	models.User.create_user(username='kudzu', first_name='Ku', last_name='Tzu', email='learnwithkudzu@gmail.com',
							password='treehouse', admin=True)
	models.User.create_user(username='mfan', first_name='Matt', last_name='Fan', email='mfan@umd.edu',
							password='treehouse', admin=True)
	# models.Link.make_link(link='https://www.bing.com/',username=kudzu )
	# models.post.make_post(link='https://www.google.com/', username='kudzu',comment='posting with valid username works')
	# models.post.make_post(link='https://www.bing.com/', username='mfan',comment='posting with valid username works')
	# models.post.make_post(link='https://www.facebook.com/', username='kudzu',comment='This is a link to facebook')
	# models.post.make_post(link='https://www.google.com/', username='notkudzu',comment='This should not work- username is not valid...')
	# models.Link.DEBUG_print_links()
	# models.post.DEBUG_print_posts()
	# models.Subscription.subscribe_to(username='kudzu',subscription='kudzu')
	# models.Subscription.DEBUG_print_subscriptions()
	# models.Project.make_project(username='kudzu',project_name='default')
	# models.Project.make_project(username='mfan',project_name='default')
	# models.Project.make_project(username='kudzu',project_name='default')
	# models.Project.make_project(username='kudzu',project_name='test_project1')
	# print(models.Project.project_names_owned_by(username='kudzu'))
	# print(models.Link.get_project_links(project_name='default',username='kudzu'))
	"""
	models.post.make_post(link='https://docs.google.com/document/d/1kxXoO8lynFry3BRswPf7_oIV9PFuVTFHJCPmF8RVxHk/edit?usp=sharing', username='kudzu',comment='Our DGC thinking doc. Are you ready to do good?')
	models.post.make_post(link='https://drive.google.com/a/terpmail.umd.edu/file/d/0B1s7g_0TZcouOFBKMkE5UVhEckE/view?usp=sharing', username='kudzu',comment="Link to Joyce's awesome video")
	models.post.make_post(link='https://www.dropbox.com/s/74g14xq5rgxe1yy/fullLogo.png?dl=0', username='mfan',comment="Our new logo redesign!")
	models.post.make_post(link='https://trello.com/b/xn8xrvCb/kudzu-dev', username='mfan',comment="Check out my progress on the site on our trello board!")
	models.post.make_post(link='https://www.dropbox.com/s/d0y57utqwnyry7a/mainpage2.html?dl=0', username='mfan',comment="Source code for our main page's front end... a bit hacky, but it works :)")
	"""
	application.run(debug=DEBUG)  # add in host and port later...
