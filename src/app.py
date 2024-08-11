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
from models import db, People, Planet, User, Favorite
import requests
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
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

# end point to populate the table people with info of the API swapi.tech
@app.route('/people/populatedb', methods=["GET"])
def populatePeopledb():
    response = requests.get('https://www.swapi.tech/api/people?page=1&limit=300')
    response = response.json()
    response = response.get("results")
    
    for item in response:
        result = requests.get(item.get('url'))
        result = result.json()
        result = result.get('result')
        people = People()
        people.name = result.get('properties').get('name')
        people.birth_year = result.get('properties').get('birth_year')
        people.eye_color = result.get('properties').get('eye_color')
        people.gender = result.get('properties').get('gender')
        people.hair_color = result.get('properties').get('hair_color')
        people.height  = result.get('properties').get('height')
        people.mass  = result.get('properties').get('mass')
        people.skin_color = result.get('properties').get('skin_color')
        db.session.add(people)
    try:
        db.session.commit()
        return jsonify('personajes agregados'), 200
    except Exception as error:
        print(error)
        db.session.rollback()
        return jsonify('Error'), 500

# end point to populate the table planet with info of the API swapi.tech    
@app.route('/planet/populatedb', methods=["GET"])
def populatePlanetdb():
    response = requests.get('https://www.swapi.tech/api/planets?page=1&limit=300')
    response = response.json()
    response = response.get('results')
    
    for item in response:
        result = requests.get(item.get('url'))
        result = result.json()
        result = result.get('result')
        planet = Planet()
        planet.name = result.get('properties').get('name')
        planet.climate = result.get('properties').get('climate')
        planet.diameter = result.get('properties').get('diameter')
        planet.gravity = result.get('properties').get('gravity')
        planet.orbital_period = result.get('properties').get('orbital_period')
        planet.rotation_period = result.get('properties').get('orbital_period')
        planet.surface_water = result.get('properties').get('surface_water')
        planet.population = result.get('properties').get("population")
        planet.terrain = result.get('properties').get('terrain')
        db.session.add(planet)
    try:
        db.session.commit()
        return jsonify('Planetas agregados'), 200
    except Exception as error:
        print(error)
        db.session.rollback()
        return jsonify('Error'), 500
    

#Get all users with a response of a list of dictionaries 
@app.route('/users', methods=['GET'])
def getAllUsers():
    users = User()
    users = users.query.all()
    users = list(map(lambda item: item.serialize(), users))
    
    return jsonify(users),200

#Get all favorites of the actual user
@app.route('/users/favorites/<int:favorite_id>', methods=['GET'])
def getAllFavorites(favorite_id):
    user = User()
    user = user.query.filter_by(id=favorite_id).first()
    
    return jsonify(user.serialize_favorite()), 200

# adds a new planet to the favorite users table
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def addPlanetFavorite(planet_id):
    userId = 1
    favorite = Favorite()
    favorite.user_id = userId
    favorite.planet_id = planet_id
    
    db.session.add(favorite)
    try:
        db.session.commit()
        return jsonify('Planeta agreado a favoritos'), 200
    except Exception as error:
        print(error)
        db.session.rollback()
        return ('error al agregar planeta a favoritos'), 201
# adds a new person to the favorite users table
@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def addPersonFavorite(people_id):
    userId = 1
    favorite = Favorite()
    favorite.user_id = userId
    favorite.people_id = people_id
    
    db.session.add(favorite)
    
    try:
        db.session.commit()
        return jsonify('Persona agregada a favorito'), 200
    except Exception as error:
        print(error)
        db.session.rollback()
        return jsonify('Error al agregar personaje a favoritos'), 201
    
#Deletes the planet favroite by the ID
@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def deletePlanetFavorite(planet_id):
    userId = 1
    favorite = Favorite()
    
    favorite = favorite.query.filter_by(user_id=userId, planet_id=planet_id).first()
    
    if favorite:
        db.session.delete(favorite)
    
        try:
            db.session.commit()
            return jsonify('planeta eliminado de favoritos'), 200
        except Exception as error:
            print(error)
            db.session.rollback()
            return jsonify('No se pudo eliminar planeta de favorito'), 201
    else:
        return jsonify('Planeta favorito no encontrado'), 404

#Deletes the person favroite by the ID
@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def deletePersonFavorite(people_id):
    userId = 1
    favorite = Favorite()
    favorite = favorite.query.filter_by(user_id = userId, people_id = people_id).first()
    
    if favorite:
        db.session.delete(favorite)
        
        try:
            db.session.commit()
            return jsonify('Personaje eliminado de favoritos'), 200
        except Exception as error:
            print(error)
            return jsonify('Error al eliminar personaje de favoritos'), 201
    else:
        return jsonify('No se ecnontro el personaje en favoritos'), 404
    
#Get all people with a response of a list of dictionaries 
@app.route('/people', methods=['GET'])
def getAllPeople():
    people = People()
    people = people.query.all()
    people = list(map(lambda item: item.serialize(), people))
    
    return jsonify(people), 200

#Get a specific person with a repsonse of all the info with the ID
@app.route('/people/<int:people_id>', methods=['GET']) 
def getPerson(people_id):
    person = People()
    person = person.query.get(people_id)
    
    if person is None:
        raise APIException('Person not found', status_code=404)
    else:
        return jsonify(person.serialize()),200
    
#Get all planets with a response of a list of dictionaries
@app.route('/planets', methods=['GET'])
def getAllPlantes():
    planet = Planet()
    planet = planet.query.all()
    planet = list(map(lambda item: item.serialize(), planet))
    
    return jsonify(planet), 200


#Get a specific planet with a repsonse of all the info with the ID
@app.route('/planets/<int:planet_id>', methods=['GET'])
def getPlanet(planet_id):
    planet = Planet()
    planet = planet.query.get(planet_id)

    if planet is None:
        raise APIException('Planet not found', status_code=404)
    else:
        return jsonify(planet.serialize()), 200
    


        

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
