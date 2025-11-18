import flask

routes = flask.Blueprint("routes", __name__, url_prefix="/")

@routes.route("/")
def get_main_menu():
    return flask.render_template("index.html")

