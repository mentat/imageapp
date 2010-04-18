import os
import urllib

from google.appengine.ext import blobstore
from google.appengine.ext import webapp
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import template

from models import Image, Thumbnail

class MainHandler(webapp.RequestHandler):
	def get(self):
		upload_url = blobstore.create_upload_url('/upload')
		self.response.out.write('<html><body>')
		self.response.out.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
		self.response.out.write("""Upload File: <input type="file" name="file"><br> <input type="submit" 
			name="submit" value="Submit"> </form></body></html>""")

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
	
	def get(self):
		from django.utils import simplejson
		
		key = self.request.GET.get('key','')
		newurl = self.request.GET.get('newurl', '')
		
		self.response.headers['Content-Type'] = "application/json"
		self.response.set_status(303)
		self.response.out.write(simplejson.dumps({
			'key':key,
			'newurl':newurl
		}))
	
	def post(self):
		" Post to blobstore, create Image object and redirect to info URL. "
		upload_files = self.get_uploads('file')
		blob_info = upload_files[0]
		
		img = Image(title=self.request.POST.get('title', ''), image=blob_info)
		img.put()
		
		upload_url = urllib.urlencode(blobstore.create_upload_url('/upload'))
		
		self.redirect('/upload/key=%s&newurl=%s' % (urllib.urlencode(img.key()), upload_url))

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
	def get(self, image_key):
		
		img = Image.get(image_key)
		self.send_blob(img.image)
		
class ServeThumbHandler(webapp.RequestHandler):
	def get(self, width, height, image_key):
		
		index = '%d,%d' % (width, height)
		
		image_key = db.Key(image_key)
		thumb_key = db.Key.from_path('Image', image_key.id(), 'Thumb', index)
		
		thumb = db.get(thumb_key)
		if thumb is None:
			img = db.get(image_key)
			thumb = img.get_thumb(width, heigt)
		
		self.response.headers['Content-Type'] = "image/jpeg"
		self.response.out.write(thumb.data)
		
class CropHandler(webapp.RequestHandler):
	
	def get(self, image_key):
		img = Image.get(image_key)
		
		path = os.path.join(os.path.dirname(__file__), 'templates', 'crop.html')
        self.response.out.write(template.render(path, { 'img':img }))
		
	def post(self, image_key):
		
		pass