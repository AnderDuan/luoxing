# from gevent import monkey

# monkey.patch_all()

from app import create_app
from flask_script import Manager
from app.views import controller
from app.api import api
from app.restful import restful
from app.admin import admin
from flask import session



app = create_app()
app.register_blueprint(controller)
app.register_blueprint(api)
app.register_blueprint(restful)
app.register_blueprint(admin)
app.secret_key = 'abcdef'
manager = Manager(app=app)


# session.clear
if __name__ == '__main__':
    # from gevent import pywsgi
    # app.debug = True
    # server = pywsgi.WSGIServer(('127.0.0.1', 5000), app)
    # server.serve_forever()
    manager.run()
