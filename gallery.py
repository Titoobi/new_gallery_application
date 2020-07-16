from google.appengine.ext import ndb

from myuser import MyUser
from images import Image


class Gallery(ndb.Model):
    creator = ndb.KeyProperty(kind=MyUser)
    gallery_name = ndb.StringProperty()
    image_key = ndb.KeyProperty(repeated=True)
