import os

import jinja2
import webapp2
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from myuser import MyUser
from gallery import Gallery
from images import Image


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)


class GalleryPage(webapp2.RequestHandler):
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

            user_info = MyUser.get_by_id(myuser_key.id())
            user_galleries = user_info.gallery_key

        else:
            url = users.create_login_url(self.request.uri)
            login_status = 'Login'

        url_link = self.request.get('url')
        url_info = ndb.Key(urlsafe=url_link)
        url_id = url_info.id()

        gallery_details = Gallery.get_by_id(url_id)
        pictures_in_gallery = gallery_details.image_key

        count = 0
        duplicate_count = 0
        img_in_gallery = []
        duplicates = []
        final_duplicates = []

        for i in pictures_in_gallery:
            count += 1
            img_in_gallery.append(Image.get_by_id(i.id()).image_name)

        for x in img_in_gallery:
            if img_in_gallery.count(x) > 1:
                duplicates.append(x)
                for y in duplicates:
                    if y not in final_duplicates:
                        final_duplicates.append(y)

        duplicate_count = len(final_duplicates)

        template_values = {
            'url': url,
            'user': user,
            'welcome': welcome,
            'login_status': login_status,
            'user_email': user.email(),
            'gallery_details': gallery_details,
            'myuser_key': myuser_key,
            'Gallery': Gallery,
            'upload_url': blobstore.create_upload_url('/upload'),
            'pictures_in_gallery': pictures_in_gallery,
            'Image': Image,
            'count': count,
            'duplicates': duplicates,
            'duplicate_count': duplicate_count,
        }

        template = JINJA_ENVIRONMENT.get_template('gallery.html')
        self.response.write(template.render(template_values))

    def post(self):
        self.response.headers['Content-Type'] = 'text/html'

        # GET USER KEY
        user = users.get_current_user()
        myuser_key = ndb.Key('MyUser', user.user_id())

        url_id = int(self.request.get('gallery_id_delete'))
        gallery_details = Gallery.get_by_id(url_id)

        # GET NEW IMAGE DETAILS
        image_id = int(self.request.get('image_key'))
        image_details = Image.get_by_id(image_id)

        action = self.request.get('button')

        if action == 'Yes':
            # DELETE PICTURE
            # self.response.write(image_details)
            gallery_details.image_key.remove(image_details.key)
            gallery_details.put()
            image_details.key.delete()
            self.redirect('/gallery?url=' + str(gallery_details.key.urlsafe()))



class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        url_id = int(self.request.get('gallery_id'))
        gallery_details = Gallery.get_by_id(url_id)

        upload = self.get_uploads()[0]
        blobinfo = blobstore.BlobInfo(upload.key())
        filename = blobinfo.filename

        upload_image = Image()
        upload_image.image_name = filename
        upload_image.blobs = upload.key()
        upload_image.put()

        gallery_details.image_key.append(upload_image.key)
        gallery_details.put()

        self.redirect('/gallery?url=' + str(gallery_details.key.urlsafe()))


class ViewPhotoHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, photo_key):
        self.send_blob(photo_key)

