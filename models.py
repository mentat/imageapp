import logging

from google.appengine.api import images
from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.api.images import LargeImageError

class Image(db.Model):
	" An original image, stored in the blobstore. "
	title = db.StringProperty(required=False)
	added_at = db.DateTimeProperty(auto_now_add=True)
	
	image = blobstore.BlobReferenceProperty()
	cropped = db.BlobProperty()
	
	# This is the w/h ratio, needed for cropping and
	# not easy to get from a blob image.
	ratio = db.FloatProperty()
		
	thumbs = db.ListProperty(db.Key)
	# A list of thumb sizes, stored as width,height
	thumb_sizes = db.StringListProperty()
	
	def cleanup(self):
		" Cleanup and remove all the extra stuff for this image. "
		blobstore.delete(self.image)
		
		if self.cropped:
			blobstore.delete(self.cropped)
			
		db.delete(self.thumbs)
		
	def do_crop(self, left, top, right, bottom, commit=True):
		
		img = images.Image(blob_key = str(self.image.key()))
		img.crop(left, top, right, bottom)
		
		try:
			img.cropped = img.execute_transforms(output_encoding=images.JPEG)
		except LargeImageError, message:
			logging.warning("Image too large, trying again.")
			img.resize(1024,1024)
			img.cropped = img.execute_transforms(output_encoding=images.JPEG)
		
		# All thumbs are now invalid
		self.thumb_sizes = []
		db.delete(self.thumbs)
		self.thumbs = []
		
		if commit:
			db.put(self)
			
		return img
		
	def get_thumb(self, width=None, height=None, commit=True):
		" Get a thumbnail based on width and/or height. Optionally commit. "
		
		index = u'%s,%s' % (width and width or '', height and height or '')
		
		if index in list(self.thumb_sizes):
			logging.info("In thumb sizes.")
			return db.get(self.thumbs[self.thumb_sizes.index(index)])
		
		if self.cropped:
			img = images.Image(self.cropped)
		else:
			img = images.Image(blob_key=str(self.image.key()))
		
		if width and height:
			img.resize(width=width, height=height)
		elif width:
			img.resize(width=width)
		else:
			img.resize(height=height)
		
		data = None
		
		try:
			data = img.execute_transforms(output_encoding=images.JPEG)
		except LargeImageError, message:
			logging.error(str(message))
			raise
			
		newimg = images.Image(data)
		
		index = u'%d,%d' % (newimg.width, newimg.height)
		
		thumb = Thumbnail(parent=self, key_name=index,
			width=newimg.width, height=newimg.height, data=db.Blob(data))
		
		self.thumb_sizes.append(index)
		self.thumbs.append(thumb.key())
		
		if commit:
			db.put([self, thumb])
		
		return thumb
	
class Thumbnail(db.Model):
	" A thumbnail of an image. "
	width = db.IntegerProperty()
	height = db.IntegerProperty()
	
	data = db.BlobProperty()
	