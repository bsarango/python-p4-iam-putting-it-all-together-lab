#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    
    def post(self):
        json = request.get_json()
        new_user = User(username=json.get('username'),image_url=json.get('image_url'),bio=json.get('bio'))
        new_user.password_hash=json['password']
        # breakpoint()
        try:
            db.session.add(new_user)
            db.session.commit()
            # breakpoint()
            return new_user.to_dict(), 201
        except IntegrityError:
            return {'error':"Invalid new user"}, 422

class CheckSession(Resource):
    
    def get(self):

        user = User.query.filter(User.id == session.get('user_id')).first()

        if user:
            return user.to_dict(),200

        return {'error': "User not recognized, please log in"}, 401

class Login(Resource):
    
    def post(self):
        json = request.get_json()
        user = User.query.filter(User.username == json.get('username')).first()
        password = json.get('password')

        if user:
            if user.authenticate(password):
                session['user_id']=user.id
                return user.to_dict(), 201

        return {'error':"Unable to login with credentials"},401


class Logout(Resource):
    
    def delete(self):
        user = User.query.filter(User.id == session.get('user_id')).first()

        if user:
            session['user_id'] = None 

            return {'message':""}, 204
        
        return {'error':'Cannot log out, no user logged in'}, 401

class RecipeIndex(Resource):
    
    def get(self):
        if session.get('user_id'):
            recipes = [recipe.to_dict() for recipe in Recipe.query.all()]

            return recipes,200
        else:
            return {'error':'User not logged in; Unable to process request'}, 401

    def post(self):
        if session.get('user_id'):
            json = request.get_json()
            new_recipe = Recipe(title=json.get('title'), instructions=json.get('instructions'), minutes_to_complete=json.get('minutes_to_get'))
            new_recipe.user_id = session.get('user_id')

            try:
                db.session.add(new_recipe)
                db.session.commit()
                
                return new_recipe.to_dict(), 201

            except IntegrityError:
                return {'error':'Invalid recipe, try again'},422

        return {'message':"A valid user isn't logged in. Please log in."}, 401

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)