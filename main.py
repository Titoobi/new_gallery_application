import os

import jinja2
import webapp2
from google.appengine.api import users
from google.appengine.ext import ndb


from dashboard import Dashboard
# from galleryPage import GalleryPage

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'

        url = ''
        login_status = ''

        user = users.get_current_user()

        if user:
            url = users.create_logout_url(self.request.uri)
            login_status = 'Logout'
            self.redirect('/dashboard')

            myuser_key = ndb.Key('MyUser', user.user_id())
            myuser = myuser_key.get()

        else:
            url = users.create_login_url(self.request.uri)
            login_status = 'Login'

        template_values = {
            'url': url,
            'user': user,
            'login_status': login_status
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


# starts the application
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/dashboard', Dashboard),
    # ('/gallery', GalleryPage),
], debug=True)
