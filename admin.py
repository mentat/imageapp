from lib.aframe.handlers import AdminHandler

class Images(blobstore_handlers.BlobstoreUploadHandler, AdminHandler):
	"""The collection of images."""

	def post(self, key):
		chapter = entity_or_404(key)
		# Create a dummy image so that we can set its parent to the chapter to
		# which it is being added.  The title will be replaced by the
		# submitted data.
		
		upload_files = self.get_uploads('file')
		blob_info = upload_files[0]
		
		img = Image(title=self.request.POST.get('title', ''), image=blob_info)
		img.put()
		
		self.respond_json(resp, status_code=201)
		