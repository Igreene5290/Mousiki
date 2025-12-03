import csv
import mysql.connector
import os

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Euclid2015!',
    'database': 'mousiki'
}

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)  # Go up one level from app folder
SPOTIFY_CSV = os.path.join(PARENT_DIR, 'Spotify Tracks Dataset', 'dataset.csv')
BILLBOARD_CSV = os.path.join(PARENT_DIR, 'Billboard Hot 100', 'charts.csv')

artist_cache = {}
album_cache = {}
genre_cache = {}
track_cache = {}

def get_or_create_artist(cursor, name):
    if not name: return None
    name = name.strip()
    if name in artist_cache: return artist_cache[name]
    cursor.execute("SELECT artist_id FROM artist WHERE name = %s", (name,))
    result = cursor.fetchone()
    if result:
        artist_id = result[0]
    else:
        cursor.execute("INSERT INTO artist (name) VALUES (%s)", (name,))
        artist_id = cursor.lastrowid
    artist_cache[name] = artist_id
    return artist_id

def get_or_create_album(cursor, title, artist_id):
    if not title: return None
    title = title.strip()
    key = (title, artist_id)
    if key in album_cache: return album_cache[key]
    cursor.execute("SELECT album_id FROM album WHERE title = %s AND artist_id = %s", (title, artist_id))
    result = cursor.fetchone()
    if result:
        album_id = result[0]
    else:
        cursor.execute("INSERT INTO album (title, artist_id) VALUES (%s, %s)", (title, artist_id))
        album_id = cursor.lastrowid
    album_cache[key] = album_id
    return album_id

def get_or_create_genre(cursor, name):
    if not name: return None
    name = name.strip()
    if name in genre_cache: return genre_cache[name]
    cursor.execute("SELECT genre_id FROM genre WHERE name = %s", (name,))
    result = cursor.fetchone()
    if result:
        genre_id = result[0]
    else:
        cursor.execute("INSERT INTO genre (name) VALUES (%s)", (name,))
        genre_id = cursor.lastrowid
    genre_cache[name] = genre_id
    return genre_id

def get_or_create_track(cursor, title, artist_id, album_id, popularity):
    key = (title, artist_id)
    if key in track_cache: return track_cache[key]
    cursor.execute("SELECT track_id FROM track WHERE title = %s AND artist_id = %s", (title, artist_id))
    result = cursor.fetchone()
    if result:
        track_id = result[0]
    else:
        cursor.execute("INSERT INTO track (title, artist_id, album_id, popularity) VALUES (%s, %s, %s, %s)", (title, artist_id, album_id, popularity))
        track_id = cursor.lastrowid
    track_cache[key] = track_id
    return track_id

def load_spotify_data(conn, cursor):
    print("Loading Spotify data...")
    if not os.path.exists(SPOTIFY_CSV):
        print(f"File not found: {SPOTIFY_CSV}")
        return
    count = 0
    with open(SPOTIFY_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            track_name = row.get('track_name', '').strip()
            artist_name = row.get('artists', '').strip().split(';')[0]
            album_name = row.get('album_name', '').strip()
            genre_name = row.get('track_genre', '').strip()
            try: popularity = int(row.get('popularity', 0))
            except: popularity = 0
            if not track_name or not artist_name: continue
            artist_id = get_or_create_artist(cursor, artist_name)
            album_id = get_or_create_album(cursor, album_name, artist_id) if album_name else None
            track_id = get_or_create_track(cursor, track_name, artist_id, album_id, popularity)
            if genre_name:
                genre_id = get_or_create_genre(cursor, genre_name)
                if genre_id:
                    cursor.execute("INSERT IGNORE INTO track_genre (track_id, genre_id) VALUES (%s, %s)", (track_id, genre_id))
            count += 1
            if count % 5000 == 0:
                print(f"  Processed {count} rows...")
                conn.commit()
    conn.commit()
    print(f"Loaded {count} Spotify tracks")

def load_billboard_data(conn, cursor):
    print("Loading Billboard data...")
    if not os.path.exists(BILLBOARD_CSV):
        print(f"File not found: {BILLBOARD_CSV}")
        return
    count = 0
    with open(BILLBOARD_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            song = row.get('song', '').strip()
            artist_name = row.get('artist', '').strip().split(' Featuring ')[0]
            try:
                rank = int(row.get('rank', 100))
                popularity = max(0, 100 - rank)
            except: popularity = 0
            if not song or not artist_name: continue
            artist_id = get_or_create_artist(cursor, artist_name)
            get_or_create_track(cursor, song, artist_id, None, popularity)
            count += 1
            if count % 10000 == 0:
                print(f"  Processed {count} rows...")
                conn.commit()
    conn.commit()
    print(f"Loaded {count} Billboard entries")

def main():
    print("Mousiki Dataset Loader")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("Connected to database")
        load_spotify_data(conn, cursor)
        load_billboard_data(conn, cursor)
        cursor.execute("SELECT COUNT(*) FROM track")
        print(f"Total tracks: {cursor.fetchone()[0]}")
        cursor.close()
        conn.close()
        print("Done!")
    except mysql.connector.Error as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    main()
