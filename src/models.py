from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable = False)
    last_name = db.Column(db.String(20), nullable = False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    created_at = db.Column(db.DateTime, nullable = False, default = datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable = False, default = datetime.now(timezone.utc), onupdate = datetime.now(timezone.utc))
    
    favorites = db.relationship('Favorite', back_populates = 'user')

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            'first_name': self.first_name,
            'last_name': self.last_name
            # do not serialize the password, its a security breach
        }
    def serialize_favorite(self):
        return{
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "favorites": list(map(lambda item: item.serialize(), self.favorites))
        }
class People(db.Model):
    __tablename__ = 'people'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable = False)
    height = db.Column(db.String(20), nullable = False)
    mass = db.Column(db.String(20), nullable = False)
    hair_color = db.Column(db.String(20), nullable = False)
    skin_color = db.Column(db.String(20), nullable = False)
    eye_color = db.Column(db.String(50), nullable = False)
    birth_year = db.Column(db.String(50), nullable = False)
    gender = db.Column(db.String(50), nullable = False)
    created = db.Column(db.DateTime, nullable = False, default = datetime.now(timezone.utc))
    
    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "height": self.height,
            "mass": self.mass,
            "hair_color": self.hair_color,
            "skin_color": self.skin_color,
            "eye_color": self.eye_color,
            "birth_year": self.birth_year,
            "gender": self.gender,
            "created": self.created
        }
        
class Planet(db.Model):
    __tablename__ = 'planet'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False)
    climate = db.Column(db.String(50), nullable = False)
    diameter = db.Column(db.String(50), nullable = False)
    gravity = db.Column(db.String(50), nullable=False)
    orbital_period = db.Column(db.String(50), nullable=False)
    rotation_period = db.Column(db.String(50), nullable = False)
    population = db.Column(db.String(50), nullable = False)
    terrain = db.Column(db.String(50), nullable = False)
    surface_water = db.Column(db.String(50), nullable = False)
    created = db.Column(db.DateTime, nullable = False, default= datetime.now(timezone.utc))
    
    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "diameter": self.diameter,
            "gravity": self.gravity,
            "orbital_period": self.orbital_period,
            "rotation_period": self.rotation_period,
            "population": self.population,
            "terrain": self.terrain,
            "surface_water": self.surface_water,
            "created": self.created
        }

class Favorite(db.Model):
    __tablename__ = 'favorite'
    id = db.Column(db.Integer, primary_key = True)
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable = True)
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.id'), nullable = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    
    user = db.relationship("User", back_populates = 'favorites')
    planet = db.relationship('Planet')
    people = db.relationship('People')
    
    def serialize(self):
        return{
            "people_id": self.people_id,
            "planet_id": self.planet_id,
            "user_id": self.user_id,
            "planet_name": self.planet.name if self.planet else None,
            "people_name": self.people.name if self.people else None
        }