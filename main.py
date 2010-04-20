from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from imageapp import views

application = webapp.WSGIApplication([
	('/%s/' % views.IMAGE_APP_PATH, views.MainHandler),
	('/%s/upload' % views.IMAGE_APP_PATH, views.UploadHandler),
	('/%s/internal/upload' % views.IMAGE_APP_PATH, views.UploadInternalHandler),
	('/%s/crop/([^/]+)' % views.IMAGE_APP_PATH, views.CropHandler),
	('/%s/serve/([^/]+)' % views.IMAGE_APP_PATH, views.ServeHandler),
	('/%s/thumb/([0-9]+)/([0-9]+)/([^/]+)' % views.IMAGE_APP_PATH, views.ServeThumbHandler)
	], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == '__main__':
	main()