from google.appengine.ext.db import djangoforms
from google.appengine.api.users import get_current_user
from google.appengine.ext import blobstore

from django import forms
from django.utils.safestring import mark_safe

from lib.aframe.forms import ModelMultipleChoiceField, RichTextEditor

import models

from django.forms.widgets import Widget
from django.forms.fields import Field

class ImageInput(forms.FileInput):
	def render(self, name, value, attrs):
		# Get the default rendering of the widget
		base = super(self.__class__, self).render(name, None, attrs=attrs)

		# Wrap it in a special <span> so that it can be replaced by an Ajax
		# uploader, if necessary, with an id of "uploader:fieldname"
		wrapper = '<span id="uploader:%s" class="uploader">%s</span>'
		name = name.split('-')[-1]
		base = wrapper % (name, base)

		# If we've already got an image, display it above the widget, along
		# with a button to delete it
		if value:
			template = """
<div class="image field">
	<img src="%(src)s" class="preview">
	<a href="%(src)s" class="delete" title="Delete image?">&#10008;</a>
	%(widget)s
</div>"""
			return template % dict(src=value, widget=base)

		return base
		
class ImageAppWidget(Widget):
	def render(self, name, value, attrs):
		# Get the default rendering of the widget
		
		from views import IMAGE_APP_PATH
			
		env = {
			'name':name, 
			'value':value and value or '', 
			'field':name,
			'path':IMAGE_APP_PATH,
			'upload_url':''
		}
		env.update(attrs)

		base = """
	<div id="imageField%(name)s" class="image field">
	<button id="idImageAppUpload%(name)s">Choose File</button>
	<input type="hidden" name="%(name)s" id="id_%(name)s" value=""/>
	<script type="text/javascript">
		new Asset.javascript('/static/%(path)s/imageapp_admin.js', {
			onload: function() {
				setupImages('%(path)s', '%(field)s', '%(upload_url)s', '%(value)s');
			}
		});
	</script>
	</div>""" % env
		return base

class BlobImageWidget(ImageAppWidget):
	
	def render(self, name, value, attrs):
		from views import IMAGE_APP_PATH
		upload_url = blobstore.create_upload_url('/%s/internal/upload' % IMAGE_APP_PATH)
		return super(BlobImageWidget, self).render(name, value, {'upload_url':upload_url})
		

class ImageWidget(ImageAppWidget):
	
	def render(self, name, value, attrs):
		from views import IMAGE_APP_PATH
		upload_url = blobstore.create_upload_url('/%s/upload' % IMAGE_APP_PATH)
		return super(ImageWidget, self).render(name, value, {'upload_url':upload_url})


class ImageForm(djangoforms.ModelForm):
	class Meta:
		model = models.Image
		exclude = ['ratio', 'thumbs', 'thumb_sizes']
		
	image = forms.FileField(widget=BlobImageWidget)