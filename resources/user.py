from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    
)
from bson import ObjectId

from models.user import UserModel
from models.alert import AlertModel
from models.stock import StockModel
from flask_bcrypt import generate_password_hash, check_password_hash

from flask import jsonify

import datetime

_user_parser = reqparse.RequestParser()
_user_parser.add_argument('first_name', type=str)
_user_parser.add_argument('last_name', type=str)
_user_parser.add_argument('email', type=str)
_user_parser.add_argument('password', type=str)
_user_parser.add_argument('email', type=str)
_user_parser.add_argument('password', type=str)
_user_parser.add_argument('stock_id', type=str)
_user_parser.add_argument('trigger_price', type=float)
_user_parser.add_argument('operation', type=str)
_user_parser.add_argument('alert_type', type=str)
_user_parser.add_argument('MA_period', type=int)


class User(Resource):
    def get(self, user_id: str):
        user = UserModel.find_by_user_id(user_id).first()
        if user:
            return user.json()
        else:
            return {'message': 'Email does not exist'}

    def delete(self, user_id: str):
        user = UserModel.find_by_user_id(user_id).first()
        if user:
            user.delete()
            return {'message': 'User has been deleted'}
        else:
            return {'message': 'Email does not exist.'}

class UserRegister(Resource): 
    def post(self):
        data = _user_parser.parse_args()
        user = UserModel.find_by_email(data["email"])
        if user:
            return {'message': 'Email is already taken.'}
        else:
            user = UserModel(first_name=data['first_name'], last_name=data['last_name'], email=data['email'].lower(), password=generate_password_hash(data['password']))
            user.save()
            access_token = create_access_token(
                identity={'user_id': str(user.id)},
                expires_delta= datetime.timedelta(days=7)
                )
            user.send_email(access_token)
            return {"message": "Data saved"}

class UserLogin(Resource):
    def post(self):
        data = _user_parser.parse_args()
        user = UserModel.find_by_email(data["email"].lower()).first()
        if user:
            check_password = check_password_hash(user.password, data['password'])
            if check_password:
                if not user.verification:
                    return {'message': "Your account has not been verified. Please verify your account before logging in."}
                access_token = create_access_token(
                    identity={
                        'user_id': str(user.id), 
                        'email': user.email
                        },
                    fresh=True
                    )
                refresh_token = create_refresh_token(
                    identity={
                        'user_id': str(user.id), 
                        'email': user.email
                        })
                return {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'expiry_time': str(datetime.datetime.now() + datetime.timedelta(minutes=15))
                }
            else:
                return {"message": "You have entered an invalid password. Please try again."}
        else:
            return {"message": "You have entered an invalid email address. Please try again."}

class CheckToken(Resource):
    @jwt_required()
    def post (self):
        return {'msg': "Verification success"}

class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {
            'access_token': new_token,
            'expiry_time': str(datetime.datetime.now() + datetime.timedelta(minutes=15))
            }, 200

class UserVerify(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        user = UserModel.find_by_user_id(current_user['user_id']).first()
        user.verification = True
        user.save()
        return {'message': "Your account has been verified."}

    def post(self):
        data = _user_parser.parse_args()
        user = UserModel.find_by_email(data['email']).first()
        if user:
            access_token = create_access_token(
                identity={'user_id': str(user.id)},
                expires_delta= datetime.timedelta(days=7)
                )
            user.send_email(access_token)
            return {'msg': "New link has been sent to your email."}
        else:
            return {'msg': "This email does not exists. Please verify your email."}
