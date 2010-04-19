from google.appengine.ext import db
from models import Image

class ImageProperty(db.ReferenceProperty):
	
	def __init__(self, **attrs):
		super(ImageProperty, self).__init__(Image, **attrs)