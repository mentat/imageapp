import logging

from google.appengine.api import images
from google.appengine.ext import db
from google.appengine.ext import blobstore

class Image(db.Model):
	title = db.StringProperty(required=False)
	added_at = db.DateTimeProperty(auto_now_add=True)
	
	image = blobstore.BlobReferenceProperty()
	cropped = blobstore.BlobReferenceProperty()
		
	thumbs = db.ListProperty(db.Key)
	# A list of thumb sizes, stored as width,height
	thumb_sizes = db.StringListProperty()
	
	def cleanup(self):
		" Cleanup and remove all the extra stuff for this image. "
		blobstore.delete(self.image)
		if self.cropped:
			blobstore.delete(self.cropped)
		db.delete(self.thumbs)
		
	def get_thumb(self, width, height):
		index = '%d,%d' % (width, height)
		if index in self.thumb_sizes:
			return db.get(self.thumbs[self.thumb_sizes.index(index)])
		
		img = images.Image(blob_key=self.cropped and \
			str(self.cropped.key()) or str(self.image.key()))
			
		img.resize(width=width, height=height)
		
		data = img.execute_transforms(output_encoding=images.JPEG)
		
		thumb = Thumbnail(parent=self, key_name=index,
			width=width, height=height, data=db.Blob(data))
		
		self.thumb_sizes.append(index)
		self.thumbs.append(thumb.key())
		
		db.put([self, thumb])
		
		return thumb
	
class Thumbnail(db.Model):
	width = db.IntegerProperty()
	height = db.IntegerProperty()
	
	data = db.BlobProperty()
	