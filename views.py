import os
import urllib
import logging

from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext import webapp
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import template

from models import Image, Thumbnail

try:
	import settings
	IMAGE_APP_PATH = getattr(settings, 'IMAGE_APP_PATH', 'imageapp')
except ImportError:
	IMAGE_APP_PATH = 'imageapp'

class MainHandler(webapp.RequestHandler):
	def get(self):
		upload_url = blobstore.create_upload_url('/%s/upload' % IMAGE_APP_PATH)
		self.response.out.write('<html><body>')
		self.response.out.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
		self.response.out.write("""Upload File: <input type="file" name="file"><br> <input type="submit" 
			name="submit" value="Submit"> </form></body></html>""")

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):

	def get(self):
		from django.utils import simplejson
		
		key = urllib.unquote(self.request.GET.get('key',''))
		newurl = urllib.unquote(self.request.GET.get('newurl', ''))
		
		self.response.headers['Content-Type'] = "application/json"

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
		
		upload_url = urllib.quote(blobstore.create_upload_url('/%s/upload' % IMAGE_APP_PATH))
		self.response.set_status(303)
		self.redirect('/%s/upload?key=%s&newurl=%s' % (
			IMAGE_APP_PATH,
			urllib.quote(str(img.key())), upload_url))
			
class UploadInternalHandler(blobstore_handlers.BlobstoreUploadHandler):

	def get(self):
		from django.utils import simplejson
		
		key = urllib.unquote(self.request.GET.get('key',''))
		newurl = urllib.unquote(self.request.GET.get('newurl', ''))
		
		self.response.headers['Content-Type'] = "application/json"

		self.response.out.write(simplejson.dumps({
			'key':key,
			'newurl':newurl
		}))
	
	def post(self):
		" Post to blobstore, create Image object and redirect to info URL. "
		upload_files = self.get_uploads('file')
		blob_info = upload_files[0]
		
		upload_url = urllib.quote(blobstore.create_upload_url('/%s/internal/upload' % IMAGE_APP_PATH))
		self.response.set_status(303)
		self.redirect('/%s/internal/upload?key=%s&newurl=%s' % (
			IMAGE_APP_PATH,
			urllib.quote(str(blob_info.key())), upload_url))

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
	def get(self, image_key):
		if len(image_key) < 30:
			self.send_blob(blobstore.BlobInfo.get(image_key))
		else:
			img = Image.get(image_key)
			self.send_blob(img.image)
		
class ServeThumbHandler(webapp.RequestHandler):
	def get(self, width, height, image_key):
		
		if len(image_key) < 30:
			img = images.Image(blob_key = urllib.unquote(image_key))
			img.resize(width=int(width), height=int(height))
			self.response.headers['Content-Type'] = "image/jpeg"
			return self.response.out.write(img.execute_transforms(output_encoding=images.JPEG))
		
		width, height = int(width), int(height)
		index = '%d,%d' % (width, height)
		
		image_key = db.Key(image_key)
		thumb_key = db.Key.from_path('Image', image_key.id(), 'Thumb', index)
		
		thumb = db.get(thumb_key)
		if thumb is None:
			img = db.get(image_key)
			thumb = img.get_thumb(width, height)
		
		self.response.headers['Content-Type'] = "image/jpeg"
		self.response.out.write(thumb.data)
		
class CropHandler(webapp.RequestHandler):

	def get(self, image_key):
		img = Image.get(image_key)
		
		width = int(self.request.GET.get('width', '300'))
		
		# If no ratio we need to compute the ratio first thing
		# this is a small performance hit the first time.

		if img.ratio is None:
			thumb = img.get_thumb(width, commit=False)
			img.ratio = float(thumb.height)/float(thumb.width)
			db.put([thumb, img])
			
		height = int(float(width)*img.ratio)
		
		path = os.path.join(os.path.dirname(__file__), 'templates', 'crop.html')
		
		self.response.out.write(template.render(path, { 
			'img':img, 
			'width': width,
			'height': height,
			'IMAGE_APP_PATH':IMAGE_APP_PATH 
		}))
		
	def post(self, image_key):
		"""<input type="hidden" name="crop[x]" value="0" />
		<input type="hidden" name="crop[y]" value="0" />
		<input type="hidden" name="crop[w]" value="0" />
		<input type="hidden" name="crop[h]" value="0" />"""
		
		left = float(self.request.POST['crop[x]'])
		top = float(self.request.POST['crop[y]'])
		right = float(self.request.POST['crop[w]'])
		bottom = float(self.request.POST['crop[h]'])
		
		img = Image.get(image_key)
		img.do_crop(left, top, right, bottom)
		
		self.redirect('/%s/crop/%s' % (IMAGE_APP_PATH, str(img.key())))