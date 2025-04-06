import sqlite3
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)

class DBConnector:
    def __init__(self, db_name="albums.db"):
        self.db_name = db_name
        self.connection = None
        self.create_table()

    def connect(self):
        """Establish a connection to the database."""
        if self.connection is None:
            try:
                self.connection = sqlite3.connect(self.db_name)
            except sqlite3.Error as e:
                logging.error(f"Error connecting to database: {e}")
                raise

    def close(self):
        """Close the database connection."""
        if self.connection:
            try:
                self.connection.close()
                self.connection = None
            except sqlite3.Error as e:
                logging.error(f"Error closing database connection: {e}")

    def create_table(self):
        """Create the albums table if it doesn't exist."""
        self.connect()
        cursor = self.connection.cursor()
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS albums (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    artist TEXT NOT NULL,
                    album TEXT NOT NULL,
                    release_date TEXT,
                    spotify_uri TEXT UNIQUE,
                    nfc_id TEXT UNIQUE,
                    play_count INTEGER DEFAULT 0,
                    last_played_date TEXT,
                    album_length INTEGER,
                    date_added TEXT DEFAULT CURRENT_TIMESTAMP,
                    album_art TEXT
                )
            ''')
            self.connection.commit()
        except sqlite3.Error as e:
            logging.error(f"Error creating table: {e}")
            self.connection.rollback()
            raise

    def add_album(self, artist, album, release_date, spotify_uri, nfc_id, album_length, album_art):
        """Add a new album to the database."""
        self.connect()
        cursor = self.connection.cursor()
        try:
            cursor.execute('''
                INSERT INTO albums (artist, album, release_date, spotify_uri, nfc_id, album_length, album_art)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (artist, album, release_date, spotify_uri, nfc_id, album_length, album_art))
            self.connection.commit()
        except sqlite3.Error as e:
            logging.error(f"Error adding album: {e}")
            self.connection.rollback()
            raise

    def update_play_count(self, spotify_uri):
        """Update the play count and last played date for an album."""
        self.connect()
        cursor = self.connection.cursor()
        try:
            cursor.execute('''
                UPDATE albums
                SET play_count = play_count + 1,
                    last_played_date = ?
                WHERE spotify_uri = ?
            ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), spotify_uri))
            self.connection.commit()
        except sqlite3.Error as e:
            logging.error(f"Error updating play count: {e}")
            self.connection.rollback()
            raise

    def get_album(self, nfc_id):
        """Retrieve an album by its NFC ID."""
        self.connect()
        cursor = self.connection.cursor()
        try:
            cursor.execute('''
                SELECT * FROM albums WHERE nfc_id = ?
            ''', (nfc_id,))
            return cursor.fetchone()
        except sqlite3.Error as e:
            logging.error(f"Error getting album: {e}")
            raise

    def delete_album(self, spotify_uri):
        """Delete an album from the database."""
        self.connect()
        cursor = self.connection.cursor()
        try:
            cursor.execute('''
                DELETE FROM albums WHERE spotify_uri = ?
            ''', (spotify_uri,))
            self.connection.commit()
        except sqlite3.Error as e:
            logging.error(f"Error deleting album: {e}")
            self.connection.rollback()
            raise
    
    def get_all_albums(self):
        """Retrieve all albums from the database."""
        self.connect()
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT * FROM albums ORDER BY artist, album")
            albums = cursor.fetchall()
            album_list = []
            for album in albums:
                album_dict = {
                    'id': album[0],
                    'artist': album[1],
                    'album': album[2],
                    'release_date': album[3],
                    'spotify_uri': album[4],
                    'nfc_id': album[5],
                    'play_count': album[6],
                    'last_played_date': album[7],
                    'album_length': album[8],
                    'date_added': album[9],
                    'album_art': album[10]
                }
                album_list.append(album_dict)
            return album_list
        except sqlite3.Error as e:
            logging.error(f"Error getting all albums: {e}")
            raise

if __name__=="__main__":
    db = DBConnector()
    db.add_album("test", "test", "2021", "spotify:playlist:37i9dQZF1E8GTM5dxZeoc2", bytearray(b'7\x8fM\x05'), 50, "https://wiki.project1999.com/images/C_druid.gif")