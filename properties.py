from google.appengine.ext import db
from models import Image

class ImageProperty(db.Property):
	
	def validate(self, value):
		if isinstance(value, basestring):
			value = db.Key(value)
		
		if value is not None:
			if not isinstance(value, db.Key):
				raise TypeError("Property %s must be an instance of db.Key"
							% (self.name,))
		return super(ImageProperty, self).validate(value)
		