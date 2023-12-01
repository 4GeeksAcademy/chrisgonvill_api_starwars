"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planets, Favorites
import json
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/user', methods=['GET'])
def get_all_users():
    users = User.query.all()
    if len(users) < 1:
        return jsonify({"msg": "not found"}), 404
    serialized_users = list(map(lambda x: x.serialize(), users))
    return serialized_users, 200

@app.route('/character', methods=['GET'])
def get_all_character():
    character = Character.query.all()
    if len(character) < 1:
        return jsonify({"msg": "not found"}), 404
    serialized_character = list(map(lambda x: x.serialize(), character))
    return serialized_character, 200

@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planets.query.all()
    if len(planets) < 1:
        return jsonify({"msg": "not found"}), 404
    serialized_planets = list(map(lambda x: x.serialize(), planets))
    return serialized_planets, 200

@app.route('/user/<int:user_id>', methods=['GET'])
def get_one_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"msg": f"user with id {user_id} not found"}), 404
    serialized_user = user.serialize()
    return serialized_user, 200

@app.route('/character/<int:character_id>', methods=['GET'])
def get_one_character(character_id):
    character = Character.query.get(character_id)
    if character is None:
        return jsonify({"msg": f"character with id {character_id} not found"}), 404
    serialized_character = character.serialize()
    return serialized_character, 200

@app.route('/planets/<int:planets_id>', methods=['GET'])
def get_one_planets(planets_id):
    planets = Planets.query.get(planets_id)
    if planets is None:
        return jsonify({"msg": f"planets with id {planets_id} not found"}), 404
    serialized_planets = planets.serialize()
    return serialized_planets, 200


@app.route('/favorites', methods=['POST'])
def create_one_favorites():
    body = json.loads(request.data)
    new_favorites = Favorites(
        user = body["user"],
        character = body["character"],
        planets = body["planets"],
        
    )
    db.session.add(new_favorites)
    db.session.commit()
    return jsonify({"msg": "favorites created succesfull"}), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
