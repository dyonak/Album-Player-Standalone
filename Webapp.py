from flask import Flask, render_template, request, jsonify, g
from Registrar import Registrar
import json
import random
import logging  # Import the logging module
from DBConnector import DBConnector

app = Flask(__name__)
registrar = Registrar()

configfile = open('./config.json')
data = json.load(configfile)
PORT = data["port"]

# Configure logging
logging.basicConfig(level=logging.ERROR)  # Set the logging level to ERROR or DEBUG if needed

def get_db():
    """Get the database connection for the current request."""
    if 'db' not in g:
        g.db = DBConnector()
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    """Close the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    db = get_db()
    albums = db.get_all_albums()
    return render_template('index.html', albums=albums)

@app.route('/delete_album/<path:album_uri>', methods=['DELETE'])
def delete_album(album_uri):
    db = get_db()  # Use get_db() instead of registrar.get_db()
    try:
        db.delete_album(album_uri)
        return jsonify({'status': 'success'})
    except Exception as e:
        logging.error(f"Error deleting album: {e}")
        return jsonify({'status': 'error'}), 500

@app.route('/config')
def config():
    with open('config.json', 'r') as f:
        config = json.load(f)
    return render_template('config.html', config=config)

@app.route('/save', methods=['POST'])
def save_config():
    data = request.get_json()
    with open('config.json', 'w') as f:
        json.dump(data, f, indent=4)
    return jsonify({'status': 'success'})

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/search', methods=['POST'])
def search():
    search_term = request.form['search_term']
    albums = registrar.lookup_albums(search_term)
    db = get_db()
    existing_albums = db.get_all_albums()
    
    # Convert existing_albums to a list of dictionaries with artist and album_name
    existing_albums_list = [{'artist': album.get('artist', ''), 'album_name': album.get('album', ''), 'spotify_uri': album.get('spotify_uri', '')} for album in existing_albums]
    return jsonify({'albums': albums, 'existing_albums': existing_albums_list})

@app.route('/add_album', methods=['POST'])
def add_album():
    album_data = request.get_json()
    nfc_id = random.randrange(99999999)
    db = get_db()
    try:
        # Extract data from album_data
        artist = album_data['artist']
        album_name = album_data['album_name']
        release_date = album_data['release_date']
        spotify_uri = album_data['spotify_uri']
        album_length = album_data['total_duration_seconds']
        album_art = album_data['album_art']

        # Call db.add_album with all required arguments
        db.add_album(artist, album_name, release_date, spotify_uri, nfc_id, album_length, album_art)
        return jsonify({'status': 'success'})
    except Exception as e:
        logging.error(f"Error adding album: {e}")
        return jsonify({'status': 'error'})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=PORT)
