import webapp2
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import images
import jinja2
import os
import urllib
import logging
import json

JINJA_ENVIRONMENT = jinja2.Environment(
        loader = jinja2.FileSystemLoader(os.path.dirname(__file__)), 
        extensions = ['jinja2.ext.autoescape'], autoescape = True)
DEFAULT_GUESTBOOK_NAME='default'

guestbook_name = DEFAULT_GUESTBOOK_NAME

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity.
    We use guestbook_name as the key.
    """
    return ndb.Key('Guestbook', guestbook_name)

class User(ndb.Model):
    identity = ndb.StringProperty(indexed = False)
    email = ndb.StringProperty(indexed = False)

class Content(ndb.Model):
    contentText = ndb.StringProperty(indexed = False)
    contentImage = ndb.BlobKeyProperty()
    
class Greeting(ndb.Model):
    user = ndb.StructuredProperty(User)
    content= ndb.StringProperty(indexed = False)
    avatar = ndb.BlobKeyProperty()
    date = ndb.DateTimeProperty(auto_now_add= True)
    vote_count = ndb.IntegerProperty(default = 0)

class MainPage(webapp2.RequestHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/upload')
        
        global guestbook_name 
        guestbook_name = self.request.get('guestbook_name', DEFAULT_GUESTBOOK_NAME)
        
        greetings_query = Greeting.query(ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
        greetings = greetings_query.fetch(10)
        
        user = users.get_current_user()
        
        if user :
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else :
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        
        template_values = {
                'user' : user,
                'greetings' : greetings,
                'upload_url' : upload_url,
                'guestbook_name': urllib.quote_plus(guestbook_name),
                'url' : url,
                'url_linktext' : url_linktext
        }
        
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))
        
class Guestbook(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
                # We set the same parent key on the 'Greeting' to ensure each
        # Greeting is in the same entity group. Queries across the
        # single entity group will be consistent. However, the write
        # rate to a single entity group should be limited to
        # ~1/second.
        #guestbook_name = self.request.get('guestbook_name',
         #                                 DEFAULT_GUESTBOOK_NAME)
        global guestbook_name
        greeting = Greeting(parent=guestbook_key(guestbook_name))

        if users.get_current_user():
            greeting.user = User(
                    identity=users.get_current_user().user_id(),
                    email=users.get_current_user().email())

        greeting.content = self.request.get('content')
        
        #Get image data
        uploadData = self.get_uploads('img')
        if uploadData :
            greeting.avatar = uploadData[0].key()
        
        greeting.put()

        query_params = {'guestbook_name': guestbook_name}
        self.redirect('/?' + urllib.urlencode(query_params))

class ViewPhoto(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, photo_key):
        logging.info('image key' + photo_key)
        if not blobstore.get(photo_key):
            self.error(404)
        else :
            self.send_blob(photo_key)        
# [START image_handler]
class Image(webapp2.RequestHandler):
    def get(self):
        greeting_key = ndb.Key(urlsafe=self.request.get('img_id'))
        greeting = greeting_key.get()
        if greeting.avatar:
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(greeting.avatar)
        else:
            self.response.out.write('No image')
# [END image_handler]

class VoteHandler(webapp2.RequestHandler):
    def post(self):
        global guestbook_name
        logging.info(self.request.body)
        data = json.loads(self.request.body)
        logging.info(data['greetingKey'])
        greeting = Greeting.get_by_id(int(data['greetingKey']), parent=guestbook_key(guestbook_name))
        #logging.info(greeting)
        #greeting = ndb.Key(Greeting, 'ahBkZXZ-bW9tcy1wcmVzZW50cisLEglHdWVzdGJvb2siB2RlZmF1bHQMCxIIR3JlZXRpbmcYgICAgIDArwkM').get()
        greeting.vote_count +=1
        greeting.put()
        self.response.out.write(json.dumps(({'storyid':int(data['greetingKey']),'storyvote':greeting.vote_count})))
    
app = webapp2.WSGIApplication([
        ('/', MainPage), 
         ('/img/([^/]+)?', ViewPhoto),
         ('/upload', Guestbook),
         ('/vote/', VoteHandler)
    ], debug=True)