from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import views

application = webapp.WSGIApplication([
	('/', views.MainHandler),
	('/upload', views.UploadHandler),
	('/serve/([^/]+)', views.ServeHandler),
	('/thumb/([0-9]+)/([0-9]+)/([^/]+)', ServeThumbHandler)
	], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == '__main__':
	main()