import sqlite3
from flask_restful import Resource, reqparse
from modals.user import UserModel
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import  jwt_required

_user_parser = reqparse.RequestParser()
_user_parser.add_argument( 'username',
                            type=str,
                            required=True,
                            help="This field cannot be blank."
    )

_user_parser.add_argument('password',
                            type=str,
                            required=True,
                            help="This field cannot be blank."
    )

class UserRegister(Resource):
    def post(self):
        data = _user_parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {"message": "A user with that username already exists"}, 400

        user = UserModel(**data) #**data data['username'], data['password']
        user.save_to_db()

        return {"message": "User created successfully."}, 201
    
class User(Resource):
    @classmethod
    @jwt_required
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        return user.json()
    
    @classmethod
    @jwt_required
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        user.delete_from_db()
        return {'message': 'User deleted'}, 200

class UsersList(Resource):
    @classmethod
    @jwt_required
    def get(self):
        return {'users': [user.json() for user in UserModel.find_all()]}

class UserLogin(Resource):
    @classmethod
    def post(cls):
        #get data from parser
        data = _user_parser.parse_args()
        # find user in database
        user = UserModel.find_by_username(data['username'])
        # check password
        if user and safe_str_cmp(user.password, data['password']):
            #create access token 
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200

        return { 'message': 'Invalid credential'}, 401


