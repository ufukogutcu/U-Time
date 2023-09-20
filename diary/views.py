from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView

import jwt

from app import app, bcrypt, db
from diary.models import Diary
from auth.models import User, BlacklistToken

from tasks import process_diary

diary_blueprint = Blueprint('diary', __name__)

class DiariesAPI(MethodView):

    def get(self):
        # get the auth token
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                auth_token = auth_header
            except IndexError:
                responseObject = {
                    'status': 'fail',
                    'message': 'Bearer token malformed.'
                }
                return make_response(jsonify(responseObject)), 401
        else:
            auth_token = ''
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                user = User.query.filter_by(id=resp).first()

                if user.admin:
                    diaries = Diary.query.all()
                else:
                    diaries = Diary.query.filter_by(user_id=resp)

                responseObject = {
                    'status': 'success',
                    'data': [diary.myjson() for diary in diaries]
                }
                return make_response(jsonify(responseObject)), 200
            responseObject = {
                'status': 'fail',
                'message': resp
            }
            return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(responseObject)), 401

class DiaryAPI(MethodView):

    def get(self, diary_id):
        # get the auth token
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                auth_token = auth_header
            except IndexError:
                responseObject = {
                    'status': 'fail',
                    'message': 'Bearer token malformed.'
                }
                return make_response(jsonify(responseObject)), 401
        else:
            auth_token = ''
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                user = User.query.filter_by(id=resp).first()
                diary = Diary.query.filter_by(id=diary_id).first()
                if diary is None:
                    responseObject = {
                        'status': 'fail',
                        'data': 'A diary with this id does not exist.'
                        }
                    return make_response(jsonify(responseObject)), 404
                if user.admin or diary.user_id == user.id:
                    diary = Diary.query.filter_by(id=diary_id).first()
                    responseObject = {
                        'status': 'success',
                        'data': diary.myjson()
                        }
                    return make_response(jsonify(responseObject)), 200
                else:
                    responseObject = {
                        'status': 'fail',
                        'message': 'Authorization failed.'
                    }
                    return make_response(jsonify(responseObject)), 401

            responseObject = {
                'status': 'fail',
                'message': resp
            }
            return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(responseObject)), 401

class DiaryCreateAPI(MethodView):

    def post(self):
        # get the post data
        post_data = request.get_json()
        # get the auth token
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                auth_token = auth_header
            except IndexError:
                responseObject = {
                    'status': 'fail',
                    'message': 'Bearer token malformed.'
                }
                return make_response(jsonify(responseObject)), 401
        else:
            auth_token = ''
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):

                if User.query.filter_by(id=resp).first() is None:
                    responseObject = {
                        'status': 'fail',
                        'data': 'No such user.'
                        }
                    return make_response(jsonify(responseObject)), 404
                try:
                    diary = Diary(
                        text=post_data.get('text'),
                        user_id=resp,
                        in_progress=True
                    )
                    # insert the diary
                    db.session.add(diary)
                    db.session.commit()

                    process_diary.delay(diary.id)

                    responseObject = {
                        'status': 'success',
                        'message': 'Diary successfully created.',
                        'diary_id': diary.id
                    }
                    return make_response(jsonify(responseObject)), 201
                except Exception as e:
                    responseObject = {
                        'status': 'fail',
                        'message': 'Some error occurred. Please try again.',
                    }
                    return make_response(jsonify(responseObject)), 401

            responseObject = {
                'status': 'fail',
                'message': resp
            }
            return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(responseObject)), 401

class StatsAPI(MethodView):

    def stats(self, diaries):
        # Return stats object from a list of diaries of a user
        return 'stats'

    def get(self):
        # get the auth token
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                auth_token = auth_header
            except IndexError:
                responseObject = {
                    'status': 'fail',
                    'message': 'Bearer token malformed.'
                }
                return make_response(jsonify(responseObject)), 401
        else:
            auth_token = ''
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):

                if User.query.filter_by().first() is None:
                    responseObject = {
                        'status': 'fail',
                        'data': 'No such user.'
                        }
                    return make_response(jsonify(responseObject)), 404
                diaries = Diary.query.filter_by(user_id=resp).all()
                if diaries == []:
                    responseObject = {
                        'status': 'fail',
                        'data': 'This user has no diaries.'
                        }
                    return make_response(jsonify(responseObject)), 404
                responseObject = {
                    'status': 'success',
                    'data': self.stats(diaries)
                    }
                return make_response(jsonify(responseObject)), 200

            responseObject = {
                'status': 'fail',
                'message': resp
            }
            return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(responseObject)), 401



# define the API resources
diaries_view = DiariesAPI.as_view('diaries_api')
diary_view = DiaryAPI.as_view('diary_api')
diary_create_view = DiaryCreateAPI.as_view('diary_create_api')
stats_view = StatsAPI.as_view('stats_api')


# add Rules for API Endpoints
diary_blueprint.add_url_rule(
    '/api/diary',
    view_func=diaries_view,
    methods=['GET']
)
diary_blueprint.add_url_rule(
    '/api/diary/<diary_id>',
    view_func=diary_view,
    methods=['GET']
)
diary_blueprint.add_url_rule(
    '/api/diary',
    view_func=diary_create_view,
    methods=['POST']
)
diary_blueprint.add_url_rule(
    '/api/stats',
    view_func=stats_view,
    methods=['GET']
)
