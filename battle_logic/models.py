from werkzeug.security import generate_password_hash #generates a unique password hash for extra security 
from flask_sqlalchemy import SQLAlchemy #this is our ORM (Object Relational Mapper)
from flask_login import UserMixin, LoginManager #helping us load a user as our current_user 
from datetime import datetime #put a timestamp on any data we create (Users, Products, etc)
import uuid #makes a unique id for our data (primary key)
from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields, validates, ValidationError, post_load
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field

#instantiate all our classes
db = SQLAlchemy() #make database object
login_manager = LoginManager() #makes login object 
ma = Marshmallow() #makes marshmallow object


#use login_manager object to create a user_loader function
@login_manager.user_loader
def load_user(user_id):
    """Given *user_id*, return the associated User object.

    :param unicode user_id: user_id (email) user to retrieve

    """
    return User.query.get(user_id) #this is a basic query inside our database to bring back a specific User object

#think of these as admin (keeping track of what products are available to sell)
class User(db.Model, UserMixin): 
    #CREATE TABLE User, all the columns we create
    user_id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    pokemons = db.relationship('Pokemon', backref='user', lazy='dynamic')


    
    date_added = db.Column(db.DateTime, default=datetime.utcnow) #this is going to grab a timestamp as soon as a User object is instantiated


    #INSERT INTO User() Values()
    def __init__(self, username, email, password):
        self.user_id = self.set_id()
        self.email = email 
        self.password = self.set_password(password) 



    #methods for editting our attributes 
    def set_id(self):
        return str(uuid.uuid4()) #all this is doing is creating a unique identification token
    

    def get_id(self):
        return str(self.user_id) #UserMixin using this method to grab the user_id on the object logged in
    
    
    def set_password(self, password):
        return generate_password_hash(password) #hashes the password so it is secure (aka no one can see it)
    

    def __repr__(self):
        return f"<User: {self.email}>"

class Pokemon(db.Model):
    poke_id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    pokemon_id = db.Column(db.Integer, unique=False, nullable=False)
    pokemon_name = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(255))  # URL to the default sprite
    shiny_image_url = db.Column(db.String(255))  # URL to the shiny sprite
    base_experience = db.Column(db.Integer)
    hp = db.Column(db.Integer)
    attack = db.Column(db.Integer)
    defense = db.Column(db.Integer)
    special_attack = db.Column(db.Integer)
    special_defense = db.Column(db.Integer)
    speed = db.Column(db.Integer)
    type = db.Column(db.String(50), nullable=False)
    abilities = db.Column(db.String(200))
    moves = db.Column(db.String(255))  # Stores moves as a comma-separated string
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.String, db.ForeignKey('user.user_id'))


    def set_moves(self, moves_list):
        """Set the Pokemon's moves from a list."""
        self.moves = ','.join(moves_list)

    def get_moves(self):
        """Get the Pokemon's moves as a list."""
        return self.moves.split(',') if self.moves else []
    
    def __repr__(self):
        return f"<Pokemon: {self.pokemon_name}>"


class PokemonSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Pokemon
        sqla_session = db.session
        load_instance = True
        include_fk = True
        include_relationships = True  # Include relationships in serialization

    #  fields to be included
    poke_id = auto_field(dump_only=True)  # Generated by the system, so it's only for dumping
    pokemon_id = auto_field(required=True)
    pokemon_name = auto_field(required=True)
    image_url = auto_field(required=True)
    shiny_image_url = auto_field(required=False)
    base_experience = auto_field(required=False)
    hp = auto_field(required=False)
    attack = auto_field(required=False)
    defense = auto_field(required=False)
    special_attack = auto_field(required=False)
    special_defense = auto_field(required=False)
    speed = auto_field(required=False)
    moves = auto_field()
    type = auto_field(required=True)
    abilities = auto_field(required=True)
    user_id = auto_field()  # Included for both loading and dumping

    @validates('pokemon_name')
    def validate_pokemon_name(self, value):
        if len(value) < 1:
            raise ValidationError("Pokemon name must not be empty.")
        
# Instantiate schemas
pokemon_schema = PokemonSchema()
pokemons_schema = PokemonSchema(many=True)
