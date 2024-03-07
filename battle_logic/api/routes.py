import requests
from flask import Blueprint, request, jsonify
from flask_migrate import Migrate 
from flask_cors import CORS
from datetime import datetime
import uuid
import firebase_admin
from firebase_admin import auth



# internal imports
from config import Config 
from ..models import login_manager, db, Pokemon


api = Blueprint('api', __name__, url_prefix='/api') # every route needs to be preceeded with /api


@api.route('/protected', methods=['POST'])
def protected():
    # Extract the token from the Authorization header
    token_header = request.headers.get('Authorization')
    if not token_header:
        return jsonify({"error": "Authorization header is missing"}), 401
    
    # The token usually comes in the format "Bearer {TOKEN_VALUE}"
    id_token = token_header.split('Bearer ')[1]
    
    try:
        # Verify the token with Firebase Admin SDK
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        
        # Now you can use the UID to get user-specific data
        # and perform operations restricted to authenticated users
        
        return jsonify({"message": "Access granted", "uid": uid}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 401


@api.route('/catch-pokemon', methods=['POST'])
def catch_pokemon():
    data = request.json
    pokemon_name = data['pokemon_name']
    poke_api_response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{pokemon_name}')

    if poke_api_response.status_code == 200:
        pokemon_data = poke_api_response.json()

        # Assuming your model accepts these fields and you've parsed them correctly from the response
        new_pokemon = Pokemon(
            poke_id=str(uuid.uuid4()),  # Assuming auto-generation here, you might not need to explicitly set it
            pokemon_id=pokemon_data['id'],
            pokemon_name=pokemon_data['name'],
            image_url=pokemon_data['sprites']['other']['showdown']['front_default'],
            shiny_image_url=pokemon_data['sprites']['other']['showdown']['front_shiny'],
            base_experience=pokemon_data['base_experience'],
            hp=[stat['base_stat'] for stat in pokemon_data['stats'] if stat['stat']['name'] == 'hp'][0],
            attack=[stat['base_stat'] for stat in pokemon_data['stats'] if stat['stat']['name'] == 'attack'][0],
            defense=[stat['base_stat'] for stat in pokemon_data['stats'] if stat['stat']['name'] == 'defense'][0],
            special_attack=[stat['base_stat'] for stat in pokemon_data['stats'] if stat['stat']['name'] == 'special-attack'][0],
            special_defense=[stat['base_stat'] for stat in pokemon_data['stats'] if stat['stat']['name'] == 'special-defense'][0],
            speed=[stat['base_stat'] for stat in pokemon_data['stats'] if stat['stat']['name'] == 'speed'][0],
            type=','.join([t['type']['name'] for t in pokemon_data['types']]),
            abilities=','.join([a['ability']['name'] for a in pokemon_data['abilities']]),
            moves=','.join([m['move']['name'] for m in pokemon_data['moves'][:5]]),  # Adjust as needed
            date_added=datetime.utcnow(),
            # user_id= should be set according to your user management logic
        )

        # Serialize the new_pokemon object data for the response
        pokemon_response = {
            'poke_id': new_pokemon.poke_id,
            'pokemon_id': str(new_pokemon.pokemon_id), # Ensure this is a string if your frontend expects it
            'pokemon_name': new_pokemon.pokemon_name,
            'image_url': new_pokemon.image_url,
            'shiny_image_url': new_pokemon.shiny_image_url,
            'base_experience': new_pokemon.base_experience,
            'hp': new_pokemon.hp,
            'attack': new_pokemon.attack,
            'defense': new_pokemon.defense,
            'special_attack': new_pokemon.special_attack,
            'special_defense': new_pokemon.special_defense,
            'speed': new_pokemon.speed,
            'type': new_pokemon.type,
            'abilities': new_pokemon.abilities,
            'moves': new_pokemon.moves,
            'date_added': new_pokemon.date_added.isoformat(), # Convert datetime to string
            # Include other fields as necessary
        }
        
        db.session.add(new_pokemon)
        db.session.commit()

        return jsonify({
        'status': 'success',
        'message': f"{pokemon_name} added to the database.",
        'pokemon': pokemon_response  # Make sure to include the actual data here
        }), 200
    else:
        return jsonify({'status': 'error', 'message': 'Pokemon not found'}), 404
