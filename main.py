#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import mail

class MainHandler(webapp2.RequestHandler):
	#main page that handles logging in and out.
    def get(self):
        user = users.get_current_user()
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Login'


        if user:
        	url = users.create_logout_url(self.request.uri)
        	url_linktext = 'Logout'

        ideas = IdeaBookModel.gql("WHERE author = :author and finished=false", author = users.get_current_user())

        values = {
        	'ideas' : ideas,
        	'numberideas' : ideas.count(),
        	'user' : user,
        	'url'	:	url,
        	'url_linktext'	:	url_linktext,
        } 

        self.response.out.write(template.render('index.html', values))

class NewIdea(webapp2.RequestHandler): #this class creates a new post
	def post(self):
		user = users.get_current_user()
		if user:
			testurl = self.request.get('url')
			if not testurl.startswith("http://") and testurl:
				testurl = "http://"+testurl
			newidea = IdeaBookModel(
					author = users.get_current_user(),
					shortDes = self.request.get('shortDescription'),
					longDes = self.request.get('longDescription'),
					dueDate = self.request.get('dueDate'),
					url = testurl,
					finished = False

				)
			newidea.put()
			self.redirect('/')

class DeleteIdea(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			raw_id = self.request.get('id')
			id = int(raw_id)
			idea = IdeaBookModel.get_by_id(id)
			idea.delete()
			self.redirect("/")

class EmailIdea(webapp2.RequestHandler):
	# Email to yourself
	def get(self):
		user = users.get_current_user()
		if user:
			raw_id = self.request.get('id')
			id = int(raw_id)
			idea = IdeaBookModel.get_by_id(id)

		message = mail.EmailMessage(sender = user.email(),
					subject = idea.shortDescrtiption)
		message.to = users.email()
		message.body = idea.longDescrition
		message.send()
		self.redirect('/')



class IdeaBookModel(db.Model):
	author = db.UserProperty(required=True)
	shortDes = db.StringProperty(required=True)
	longDes = db.StringProperty(required=True)
	url = db.StringProperty()
	created = db.DateTimeProperty(auto_now_add=True)
	update = db.DateTimeProperty(auto_now_add=True)
	dueDate = db.StringProperty(required=True)
	finished = db.BooleanProperty()

#Register URL the responssible Classes
app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/new', NewIdea),
    ('/done', DeleteIdea),
    ('/email',EmailIdea)
], debug=True)
