from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from images import views

application = webapp.WSGIApplication([
	('/images/', views.MainHandler),
	('/images/upload', views.UploadHandler),
	('/images/serve/([^/]+)', views.ServeHandler),
	('/images/thumb/([0-9]+)/([0-9]+)/([^/]+)', views.ServeThumbHandler)
	], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == '__main__':
	main()