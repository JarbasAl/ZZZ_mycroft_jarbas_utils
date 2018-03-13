import json
import os
import ssl
import time
from functools import wraps

from flask import Flask, make_response
from flask import request, Response
from flask_sslify import SSLify

from mycroft_jarbas_utils.server.microservices import gen_api
from mycroft_jarbas_utils.server.database.user import UserDatabase


def root_dir():
    """ Returns root directory for this project """
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__ + '/.')))


def nice_json(arg):
    response = make_response(json.dumps(arg, sort_keys = True, indent=4))
    response.headers['Content-type'] = "application/json"
    return response

app = Flask(__name__)
sslify = SSLify(app)
port = 5678


users = UserDatabase()


def add_response_headers(headers=None):
    """This decorator adds the headers passed in to the response"""
    headers = headers or {}

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            resp = make_response(f(*args, **kwargs))
            h = resp.headers
            for header, value in headers.items():
                h[header] = value
            return resp

        return decorated_function

    return decorator


def noindex(f):
    """This decorator passes X-Robots-Tag: noindex"""
    return add_response_headers({'X-Robots-Tag': 'noindex'})(f)


def donation(f):
    """This decorator passes btc request """
    return add_response_headers({'BTC':
                                     '1aeuaAijzwK4Jk2ixomRkqjF6Q3JxXp9Q',
                                 "Patreon": "patreon.com/jarbasAI",
                                 "Paypal": "paypal.me/jarbasAI"})(
        f)


def check_auth(api_key):
    """This function is called to check if a api key is valid."""
    user = users.get_user_by_api_key(api_key)
    if not user:
        return False
    users.update_timestamp(api_key, time.time())
    return True


def check_admin_auth(api_key):
    """This function is called to check if a admin api key is valid."""
    user = users.get_user_by_api_key(api_key)
    if not user:
        return False
    if not user.is_admin:
        return False
    users.update_timestamp(api_key, time.time())
    return True


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Api Key Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        if not auth or not check_auth(auth):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


def requires_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        if not auth or not check_admin_auth(auth):
            print "not admin"
            return authenticate()
        return f(*args, **kwargs)

    return decorated


@app.route("/", methods=['GET'])
@noindex
@donation
def hello():
    return nice_json({
        "uri": "/",
        "welcome to jarbas microservices": {
            "under": "construction"
        }
    })


@app.route("/revoke_api/<api>", methods=['PUT'])
@noindex
@donation
@requires_admin
def revoke_api(api):
    if users.delete_user(api):
        result = {"removed": True}
    else:
        result = {"removed": False, "error": "does not exist"}
    return nice_json(
        result
    )


@app.route("/new_user/<api>/<mail>/<name>", methods=['PUT'])
@noindex
@donation
@requires_admin
def add_user(api, mail, name):
    result = {"success": False}
    if users.add_user(name, mail, api):
        result = {"success": True}
    return nice_json(
        result
    )


@app.route("/get_api", methods=['GET'])
@noindex
@donation
@requires_admin
def new_api():
    api = gen_api(save=False)
    return nice_json(
        {"api": api}
    )


def start(app, port=6666):
    cert = "{}/certs/JarbasServer.crt".format(root_dir())
    key = "{}/certs/JarbasServer.key".format(root_dir())
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(cert, key)
    app.run(host="0.0.0.0", port=port, debug=False, ssl_context=context)


if __name__ == "__main__":
    global app
    start(app, port)
