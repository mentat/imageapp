from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from images import views

application = webapp.WSGIApplication([
	('%s' % views.IMAGE_APP_PREFIX, views.MainHandler),
	('%supload' % views.IMAGE_APP_PREFIX, views.UploadHandler),
	('%scrop/([^/]+)' % views.IMAGE_APP_PREFIX, views.CropHandler),
	('%sserve/([^/]+)' % views.IMAGE_APP_PREFIX, views.ServeHandler),
	('%sthumb/([0-9]+)/([0-9]+)/([^/]+)' % views.IMAGE_APP_PREFIX, views.ServeThumbHandler)
	], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == '__main__':
	main()