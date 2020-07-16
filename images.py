from google.appengine.ext import ndb


class Image(ndb.Model):
    image_name = ndb.StringProperty()
    blobs = ndb.BlobKeyProperty()
