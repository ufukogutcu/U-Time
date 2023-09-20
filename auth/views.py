from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView

import jwt

from app import bcrypt, db
from auth.models import User, BlacklistToken

auth_blueprint = Blueprint("auth", __name__)


class RegisterAPI(MethodView):
    """
    User Registration Resource
    """

    def post(self):
        # get the post data
        post_data = request.get_json()
        # check if user already exists
        user = User.query.filter_by(email=post_data.get("email")).first()
        if not user:
            try:
                user = User(
                    email=post_data.get("email"), password=post_data.get("password")
                )
                # insert the user
                db.session.add(user)
                db.session.commit()
                # generate the auth token
                auth_token = user.encode_auth_token(user.id)
                responseObject = {
                    "status": "success",
                    "message": "Successfully registered.",
                    "auth_token": auth_token,
                }
                return make_response(jsonify(responseObject)), 201
            except Exception as e:
                responseObject = {
                    "status": "fail",
                    "message": str(e),
                }
                return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                "status": "fail",
                "message": "User already exists. Please Log in.",
            }
            return make_response(jsonify(responseObject)), 202


class LoginAPI(MethodView):
    """
    User Login Resource
    """

    def post(self):
        # get the post data
        post_data = request.get_json()
        try:
            # fetch the user data
            user = User.query.filter_by(email=post_data.get("email")).first()
            if user and bcrypt.check_password_hash(
                user.password, post_data.get("password")
            ):
                auth_token = user.encode_auth_token(user.id)
                if auth_token:
                    responseObject = {
                        "status": "success",
                        "message": "Successfully logged in.",
                        "auth_token": auth_token,
                    }
                    return make_response(jsonify(responseObject)), 200
            else:
                responseObject = {"status": "fail", "message": "User does not exist."}
                return make_response(jsonify(responseObject)), 404
        except Exception as e:
            print(e)
            responseObject = {"status": "fail", "message": "Try again"}
            return make_response(jsonify(responseObject)), 500


class UserAPI(MethodView):
    """
    User Resource
    """

    def get(self):
        # get the auth token
        auth_header = request.headers.get("Authorization")
        if auth_header:
            try:
                auth_token = auth_header
            except IndexError:
                responseObject = {
                    "status": "fail",
                    "message": "Bearer token malformed.",
                }
                return make_response(jsonify(responseObject)), 401
        else:
            auth_token = ""
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                user = User.query.filter_by(id=resp).first()
                if user:
                    responseObject = {
                        "status": "success",
                        "data": {
                            "user_id": user.id,
                            "email": user.email,
                            "admin": user.admin,
                            "registered_on": user.registered_on,
                        },
                    }
                    return make_response(jsonify(responseObject)), 200
                else:
                    responseObject = {
                        "status": "fail",
                        "message": "A user with this auth token does not exist.",
                    }
                    return make_response(jsonify(responseObject)), 401
            responseObject = {"status": "fail", "message": resp}
            return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                "status": "fail",
                "message": "Provide a valid auth token.",
            }
            return make_response(jsonify(responseObject)), 401

    def put(self):
        # get the auth token
        auth_header = request.headers.get("Authorization")
        if auth_header:
            try:
                auth_token = auth_header
            except IndexError:
                responseObject = {
                    "status": "fail",
                    "message": "Bearer token malformed.",
                }
                return make_response(jsonify(responseObject)), 401
        else:
            auth_token = ""
        # get the post data
        post_data = request.get_json()
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                user = User.query.filter_by(id=resp).first()
                if user:
                    try:
                        resp = user.update(post_data)
                        responseObject = {"status": "success", "message": resp}
                        return make_response(jsonify(responseObject)), 200
                    except Exception as e:
                        print(e)
                        responseObject = {"status": "success", "message": "Try again"}
                        return make_response(jsonify(responseObject)), 500
                else:
                    responseObject = {
                        "status": "fail",
                        "message": "A user with this auth token does not exist.",
                    }
                    return make_response(jsonify(responseObject)), 401
            responseObject = {"status": "fail", "message": resp}
            return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                "status": "fail",
                "message": "Provide a valid auth token.",
            }
            return make_response(jsonify(responseObject)), 401


class LogoutAPI(MethodView):
    """
    Logout Resource
    """

    def post(self):
        # get auth token
        auth_header = request.headers.get("Authorization")
        if auth_header:
            auth_token = auth_header
        else:
            auth_token = ""
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                # mark the token as blacklisted
                blacklist_token = BlacklistToken(token=auth_token)
                try:
                    # insert the token
                    db.session.add(blacklist_token)
                    db.session.commit()
                    responseObject = {
                        "status": "success",
                        "message": "Successfully logged out.",
                    }
                    return make_response(jsonify(responseObject)), 200
                except Exception as e:
                    responseObject = {"status": "fail", "message": e}
                    return make_response(jsonify(responseObject)), 200
            else:
                responseObject = {"status": "fail", "message": resp}
                return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                "status": "fail",
                "message": "Provide a valid auth token.",
            }
            return make_response(jsonify(responseObject)), 403


# define the API resources
registration_view = RegisterAPI.as_view("register_api")
login_view = LoginAPI.as_view("login_api")
user_view = UserAPI.as_view("user_api")
logout_view = LogoutAPI.as_view("logout_api")

# add Rules for API Endpoints
auth_blueprint.add_url_rule(
    "/api/auth/register", view_func=registration_view, methods=["POST"]
)
auth_blueprint.add_url_rule("/api/auth/login", view_func=login_view, methods=["POST"])
auth_blueprint.add_url_rule(
    "/api/auth/profile", view_func=user_view, methods=["GET", "PUT"]
)
auth_blueprint.add_url_rule("/api/auth/logout", view_func=logout_view, methods=["POST"])
