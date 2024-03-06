import requests
from flask import Blueprint, request, jsonify
from flask_migrate import Migrate 
from flask_cors import CORS
from datetime import datetime
import uuid


# internal imports
from config import Config 
from ..models import login_manager, db, Pokemon


api = Blueprint('api', __name__, url_prefix='/api') # every route needs to be preceeded with /api

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
            image_url=pokemon_data['sprites']['front_default'],
            shiny_image_url=pokemon_data['sprites']['other']['home']['front_shiny'],
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

        db.session.add(new_pokemon)
        db.session.commit()

        return jsonify({'status': 'success', 'message': f"{pokemon_name} added to the database."}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Pokemon not found'}), 404
