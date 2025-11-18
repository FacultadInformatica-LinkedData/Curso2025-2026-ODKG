import flask
from routers.router_API import routes_api
from routers.router_templates import routes

app = flask.Flask(__name__)

#Routes to server
app.register_blueprint(routes)
app.register_blueprint(routes_api)

#Run server
if __name__ == '__main__':
    app.run()