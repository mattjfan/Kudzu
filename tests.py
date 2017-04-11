#kudzu v3 tests
import models2 as models


def demo_init():
	#models.initialize()
	print('database initialized')
	models.Debug_Tools.delete_database()
	print('database cleared')
	models.User.create_user(username='kudzu', first_name='Ku', last_name='Tzu', email='learnwithkudzu@gmail.com',password='treehouse', admin=True)
	models.User.update_bio('kudzu',"Hi, we are Kudzu, an online, project-based learning community and platform!")
	models.Project.make_project(username='kudzu', project_name='default')
	
	models.User.create_user(username='mfan', first_name='Matt', last_name='Fan', email='mfan@umd.edu',password='treehouse', admin=True)
	models.User.update_bio('mfan',"Hi, I'm Matt, co-founder, designer, and developer here at Kudzu!")
	models.Project.make_project(username='mfan', project_name='default')
	models.Project.make_project(username='mfan', project_name='kudzu')
	
	models.User.create_user(username='emilonesty', first_name='Emily', last_name='Gross', email='emily12102016@gmail.com',password='treehouse', admin=True)
	models.User.update_bio('emilonesty',"Hey, I'm Emily, a co-founder and social media manager at Kudzu!")
	models.Project.make_project(username='emilonesty', project_name='default')
	
	models.User.create_user(username='jzhou115', first_name='Joyce', last_name='Zhou', email='jzhou115@terpmail.umd.edu',password='treehouse', admin=True)
	models.User.update_bio('jzhou115',"Hey there, my name's Joyce. I'm a co-founder at Kudzu, and work on marketing.")
	models.Project.make_project(username='jzhou115', project_name='default')
	
	models.User.create_user(username='tojorab', first_name='Tojo', last_name='Rabemananjara', email='tojorab@gmail.com',password='treehouse', admin=True)
	models.User.update_bio('tojorab',"Hello, I'm Tojo. I'm  a co-founder at Kudzu, and music enthusiast.")
	models.Project.make_project(username='tojorab', project_name='default')

	models.Link.make_link(url='https://dogood.umd.edu/', username='kudzu', comment="Who's Ready To Do Good? We know that we are!", title='do good registration page')
	models.Link.make_link(url='https://www.dropbox.com/home/kudzu?preview=kuzuLogo1_dark.png', username='mfan', comment="Kudzu logo concept. What do you guys think?", title='kudzu logo',project_name='kudzu')
	models.Link.make_link(url='https://www.dropbox.com/home/kudzu?preview=twitterBanner.png', username='mfan', comment="Banner image for Kudzu. Independent learning, together.", title='kudzu twitter banner',project_name='kudzu')
	models.Link.make_link(url='https://docs.google.com/spreadsheets/d/1urqwaGVhov-MgVe4Qkd3TeTl8ARW_Itwho74yH40kFE/edit?usp=sharing', username='emilonesty', comment="", title='DGC Gantt Chart')
	models.Link.make_link(url='s', username='tojorab', comment="Hey guys, here's some ideas I jotted down from our last team meeting", title='Brainstorming Notes')
	models.Link.make_link(url='facebooky', username='kudzu', comment="We're on Facebook now. Like our page!", title='kudzu facebook')
	models.Link.make_link(url='twitly', username='kudzu', comment="We're on Twitter- follow us!", title='kudzu twitter')
	models.Link.make_link(url='https://www.dropbox.com/home/kudzu/kudzuApp_v3/static?preview=fullLogo.png', username='mfan', comment="Logo redesign that emphasizes the indpendent project theme. Thoughts?", title='kudzu logo redesign',project_name='kudzu')
	models.Link.make_link(url='https://trello.com/b/xn8xrvCb/kudzu-dev?menu=filter&filter=label:none', username='mfan', comment="Hey guys, I set up a Trello board to keep track of product development. Feel free to add any ideas!", title='Kudzu Trello Board',project_name='kudzu')
	models.Link.make_link(url='p', username='tojorab', comment="Playing around with some new synths. Let me know what you guys think.", title='Sick Beat')
	models.Link.make_link(url='https://learnwithkudzu.slack.com/', username='emilonesty', comment="Guys, I set up the Slack page. Check it out here.", title='Kudzu Slack')
	models.Link.make_link(url='https://www.dropbox.com/home/kudzu/kudzuApp_v3/static', username='mfan', comment="Big ol' source code dump with assets for the new web app! Check it out!", title='Kudzu App Source Files',project_name='kudzu')
	models.Link.make_link(url='v', username='jzhou115', comment="Here's the promotional video for Kudzu- I went around and interviewed a bunch of people to get their thoughts on independent learning. I think it turned out pretty good.", title='Kudzu Customer Discovery Video')
	models.Trade.make_trade(username='kudzu',request='anything',offer='anything',comment="Have any ideas to make Kudzu better? We'd love to trade skills with you!")
	models.Link.make_link(url='m', username='jzhou115', comment="Here's some notes from a customer discovery trip Matt and I took to the Barrie School.", title='Barrie School Notes')
	models.Link.make_link(url='betprasd', username='kudzu', comment="Sign up for our beta program here!", title='Beta Signup')	
	models.Trade.make_trade(username='mfan',request='web development',offer='design',comment='Hey guys, anybody know how to deploy a Flask app with a sqlite database?',project_name='kudzu')
	
if __name__ == '__main__':
	models.initialize()
	demo_init()
	"""
	
	models.User.create_user(username='kudzu', first_name='Ku', last_name='Tzu', email='learnwithkudzu@gmail.com',password='treehouse', admin=True)
	models.User.create_user(username='mfan', first_name='Matt', last_name='Fan', email='mfan@umd.edu',password='treehouse', admin=True)
	models.Project.make_project(username='kudzu', project_name='default')
	models.Project.make_project(username='mfan', project_name='default')
	
	print('users created')
	"""
	"""
	models.Trade.make_trade(username='kudzu',request='time',offer='money',comment='testing if methods are functional')
	print('trade created')
	
	print(models.Post_Index.DEBUG_count_post_ids())
	#models.Comment.make_comment(parent_id=1,parent_type='trade',comment='commenting on trade',username='mfan')
	#models.Link.make_link(url='https://trello.com/b/xn8xrvCb/kudzu-dev', username='kudzu', comment='yep...', title='kudzu dev board')
	#print(models.Post_Index.load_page(username='mfan'))
	print(models.Post_Index.get_project_content(username='kudzu', project_name='default'))
	print('page load ran')
	models.User.update_bio('mfan',"Hi, I'm Matt, co-founder, designer, and developer here at Kudzu!")
	print(models.User.get_user_info('kudzu')['bio'])
	"""
	#models.User.update_bio('kudzu',"Hi, we are Kudzu, an online, project-based learning community and platform!")
	
	models.Direct_Message.send_message('mfan','kudzu',"Sending a message to Kudzu")
	models.Direct_Message.send_message('kudzu','mfan',"Sending a message back to Matt")
	print(models.Direct_Message.get_conversation('mfan','kudzu'))
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	