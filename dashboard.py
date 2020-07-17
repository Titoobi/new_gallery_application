import os

import jinja2
import webapp2
from google.appengine.api import users
from google.appengine.ext import ndb

from myuser import MyUser
from gallery import Gallery
from images import Image

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape', 'jinja2.ext.loopcontrols'],
    autoescape=True
)


class Dashboard(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'

        url = ''
        welcome = ''
        login_status = ''

        user = users.get_current_user()

        if user:
            url = users.create_logout_url('/')
            login_status = 'Logout'

            myuser_key = ndb.Key('MyUser', user.user_id())
            myuser = myuser_key.get()

            if myuser == None:
                myuser = MyUser(id=user.user_id(), email=user.email())
                myuser.put()

            user_info = MyUser.get_by_id(myuser_key.id())
            user_galleries = user_info.gallery_key

            # all_imgs_in_gallery = []
            # all_gallery_names = []
            #
            # for i in user_galleries:
            #     aa = []
            #     gallery_deets = Gallery.get_by_id(i.id()).image_key
            #     for g in gallery_deets:
            #         aa.append(Image.get_by_id(g.id()).image_name)
            #     all_imgs_in_gallery.append(aa)
            #     all_gallery_names.append(Gallery.get_by_id(i.id()).gallery_name)

        else:
            url = users.create_login_url(self.request.uri)
            login_status = 'Login'

        template_values = {
            'url': url,
            'user': user,
            'welcome': welcome,
            'login_status': login_status,
            'user_email': user.email(),
            'user_galleries': user_galleries,
            'myuser_key': myuser_key,
            'Gallery': Gallery,
            'Image': Image,
        }

        template = JINJA_ENVIRONMENT.get_template('dashboard.html')
        self.response.write(template.render(template_values))

    def post(self):
        self.response.headers['Content-Type'] = 'text/html'

        # GET USER KEY
        user = users.get_current_user()
        myuser_key = ndb.Key('MyUser', user.user_id())
        user_info = MyUser.get_by_id(myuser_key.id())

        action = self.request.get('button')

        # CREATE NEW GALLERY
        if action == 'Create New Gallery':
            # GET NEW GALLERY NAME
            gallery_name = self.request.get('gallery_name')

            # CREATE NEW GALLERY
            new_gallery = Gallery(creator=myuser_key, gallery_name=gallery_name)
            new_gallery.put()

            # We also have to pass the details of this gallery to the MyUser datastore
            associate_gallery_to_user = MyUser.get_by_id(myuser_key.id())
            associate_gallery_to_user.gallery_key.append(new_gallery.key)
            associate_gallery_to_user.put()
            self.redirect('/dashboard')

        elif action == 'Edit Gallery':
            # GET CURRENT GALLERY DETAILS
            gallery_key = int(self.request.get('gallery_key'))
            current_gallery = Gallery.get_by_id(gallery_key)

            # GET NEW GALLERY NAME
            new_gallery_name = self.request.get('edit_gallery_name')
            # self.response.write(gallery_id.gallery_name)

            current_gallery.gallery_name = new_gallery_name
            current_gallery.put()
            self.redirect('/')

        elif action == 'Yes':
            # DELETE GALLERY
            gall_id = int(self.request.get('delete_gallery_id'))
            current_gallery = Gallery.get_by_id(gall_id)

            user_info.gallery_key.remove(current_gallery.key)
            user_info.put()
            current_gallery.key.delete()
            self.redirect('/')

