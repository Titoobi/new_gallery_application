from google.appengine.ext import ndb


class MyUser(ndb.Model):
    email = ndb.StringProperty(indexed=False)
    gallery_key = ndb.KeyProperty(repeated=True)

