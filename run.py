# Run a test server.
from app import app
app.run()


# from tornado.wsgi import WSGIContainer
# from tornado.httpserver import HTTPServer
# from tornado.ioloop import IOLoop
# from app import app

# http_server = HTTPServer(WSGIContainer(app))
# http_server.listen(8888)
# IOLoop.instance().start()