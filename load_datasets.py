import csv
import mysql.connector
import os
import sys

# MySQL Connection Configuration
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'Euclid2015!'
MYSQL_DATABASE = 'mousiki'

# File paths (relative to script location)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BILLBOARD_CSV = os.path.join(SCRIPT_DIR, 'Billboard Hot 100', 'charts.csv')
SPOTIFY_CSV = os.path.join(SCRIPT_DIR, 'Spotify Tracks Dataset', 'dataset.csv')

# Global caches for deduplication
artist_cache = {}  # name -> artist_id
album_cache = {}   # (title, artist_id) -> album_id
genre_cache = {}   # name -> genre_id
track_cache = {}   # (title, artist_id) -> track_id

# Statistics
stats = {
    'artists_inserted': 0,
    'albums_inserted': 0,
    'tracks_inserted': 0,
    'genres_inserted': 0,
    'track_genres_inserted': 0,
    'billboard_rows_processed': 0,
    'spotify_rows_processed': 0,
}


def parse_artist_name(artist_string):
    """Extract primary artist from multi-artist strings."""
    if not artist_string:
        return None
    
    # Common separators for featured artists
    separators = [' Featuring ', ' featuring ', ' feat. ', ' Feat. ', 
                  ' & ', ' and ', ';', ' x ', ' X ']
    
    artist_name = artist_string
    for sep in separators:
        if sep in artist_name:
            artist_name = artist_name.split(sep)[0]
            break
    
    return artist_name.strip()


def get_or_create_artist(cursor, artist_name):
    """Get artist_id or create new artist if not exists."""
    if not artist_name or artist_name.strip() == '':
        return None
    
    artist_name = artist_name.strip()
    
    # Check cache
    if artist_name in artist_cache:
        return artist_cache[artist_name]
    
    # Check database
    cursor.execute("SELECT artist_id FROM artist WHERE name = %s", (artist_name,))
    result = cursor.fetchone()
    
    if result:
        artist_id = result[0]
    else:
        # Insert new artist
        cursor.execute("INSERT INTO artist (name) VALUES (%s)", (artist_name,))
        artist_id = cursor.lastrowid
        stats['artists_inserted'] += 1
    
    artist_cache[artist_name] = artist_id
    return artist_id


def get_or_create_album(cursor, album_title, artist_id):
    """Get album_id or create new album if not exists."""
    if not album_title or album_title.strip() == '':
        return None
    
    album_title = album_title.strip()
    cache_key = (album_title, artist_id)
    
    # Check cache
    if cache_key in album_cache:
        return album_cache[cache_key]
    
    # Check database
    cursor.execute(
        "SELECT album_id FROM album WHERE title = %s AND artist_id = %s",
        (album_title, artist_id)
    )
    result = cursor.fetchone()
    
    if result:
        album_id = result[0]
    else:
        # Insert new album
        cursor.execute(
            "INSERT INTO album (title, artist_id, release_year) VALUES (%s, %s, NULL)",
            (album_title, artist_id)
        )
        album_id = cursor.lastrowid
        stats['albums_inserted'] += 1
    
    album_cache[cache_key] = album_id
    return album_id


def get_or_create_genre(cursor, genre_name):
    """Get genre_id or create new genre if not exists."""
    if not genre_name or genre_name.strip() == '':
        return None
    
    genre_name = genre_name.strip()
    
    # Check cache
    if genre_name in genre_cache:
        return genre_cache[genre_name]
    
    # Check database
    cursor.execute("SELECT genre_id FROM genre WHERE name = %s", (genre_name,))
    result = cursor.fetchone()
    
    if result:
        genre_id = result[0]
    else:
        # Insert new genre
        cursor.execute("INSERT INTO genre (name) VALUES (%s)", (genre_name,))
        genre_id = cursor.lastrowid
        stats['genres_inserted'] += 1
    
    genre_cache[genre_name] = genre_id
    return genre_id


def create_track(cursor, title, artist_id, album_id=None, popularity=0):
    """Create a new track record or update existing popularity."""
    cache_key = (title.strip(), artist_id)
    
    # Check cache
    if cache_key in track_cache:
        track_id = track_cache[cache_key]
        # Update popularity if new value is higher
        cursor.execute(
            "UPDATE track SET popularity = GREATEST(popularity, %s) WHERE track_id = %s",
            (popularity, track_id)
        )
        return track_id
    
    # Check database
    cursor.execute(
        "SELECT track_id FROM track WHERE title = %s AND artist_id = %s",
        (title, artist_id)
    )
    result = cursor.fetchone()
    
    if result:
        track_id = result[0]
        # Update popularity if new value is higher
        cursor.execute(
            "UPDATE track SET popularity = GREATEST(popularity, %s) WHERE track_id = %s",
            (popularity, track_id)
        )
    else:
        # Insert new track
        cursor.execute(
            "INSERT INTO track (title, artist_id, album_id, popularity) VALUES (%s, %s, %s, %s)",
            (title, artist_id, album_id, popularity)
        )
        track_id = cursor.lastrowid
        stats['tracks_inserted'] += 1
    
    track_cache[cache_key] = track_id
    return track_id


def link_track_genre(cursor, track_id, genre_id):
    """Link a track to a genre (many-to-many)."""
    if not track_id or not genre_id:
        return
    
    cursor.execute(
        "INSERT IGNORE INTO track_genre (track_id, genre_id) VALUES (%s, %s)",
        (track_id, genre_id)
    )
    if cursor.rowcount > 0:
        stats['track_genres_inserted'] += 1


def load_spotify_data(connection, cursor):
    """Load Spotify Tracks dataset into artist, album, track, genre, track_genre tables."""
    print(f"\n{'='*60}")
    print("Loading Spotify Tracks Data")
    print(f"{'='*60}")
    
    if not os.path.exists(SPOTIFY_CSV):
        print(f"✗ Spotify CSV not found: {SPOTIFY_CSV}")
        return False
    
    try:
        with open(SPOTIFY_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            row_count = 0
            
            for row in reader:
                row_count += 1
                
                # Parse data
                track_name = row.get('track_name', '').strip()
                artist_string = row.get('artists', '').strip()
                album_name = row.get('album_name', '').strip()
                genre_name = row.get('track_genre', '').strip()
                
                if not track_name or not artist_string:
                    continue
                
                # Get primary artist
                artist_name = parse_artist_name(artist_string)
                artist_id = get_or_create_artist(cursor, artist_name)
                
                if not artist_id:
                    continue
                
                # Get or create album
                album_id = None
                if album_name:
                    album_id = get_or_create_album(cursor, album_name, artist_id)
                
                # Get popularity
                try:
                    popularity = int(row.get('popularity', 0))
                except ValueError:
                    popularity = 0
                
                # Create track
                track_id = create_track(cursor, track_name, artist_id, album_id, popularity)
                
                # Link genre
                if genre_name:
                    genre_id = get_or_create_genre(cursor, genre_name)
                    if genre_id:
                        link_track_genre(cursor, track_id, genre_id)
                
                stats['spotify_rows_processed'] += 1
                
                # Print progress and commit every 5000 rows
                if row_count % 5000 == 0:
                    print(f"  Processed {row_count:,} Spotify rows...")
                    connection.commit()
            
            connection.commit()
            print(f"✓ Spotify data loaded: {row_count:,} rows processed")
            return True
            
    except Exception as e:
        print(f"✗ Error loading Spotify data: {e}")
        import traceback
        traceback.print_exc()
        connection.rollback()
        return False


def load_billboard_data(connection, cursor):
    """Load Billboard Hot 100 charts data into artist and track tables."""
    print(f"\n{'='*60}")
    print("Loading Billboard Hot 100 Data")
    print(f"{'='*60}")
    
    if not os.path.exists(BILLBOARD_CSV):
        print(f"✗ Billboard CSV not found: {BILLBOARD_CSV}")
        return False
    
    try:
        with open(BILLBOARD_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            row_count = 0
            
            for row in reader:
                row_count += 1
                
                # Parse data
                song_title = row.get('song', '').strip()
                artist_string = row.get('artist', '').strip()
                
                if not song_title or not artist_string:
                    continue
                
                # Get primary artist
                artist_name = parse_artist_name(artist_string)
                artist_id = get_or_create_artist(cursor, artist_name)
                
                if not artist_id:
                    continue
                
                # Convert rank to popularity score (rank 1 = popularity 99)
                try:
                    rank = int(row.get('rank', 100))
                    popularity = max(0, 100 - rank)
                except ValueError:
                    popularity = 0
                
                # Create track (no album info in Billboard data)
                create_track(cursor, song_title, artist_id, popularity=popularity)
                
                stats['billboard_rows_processed'] += 1
                
                # Print progress every 10000 rows
                if row_count % 10000 == 0:
                    print(f"  Processed {row_count:,} Billboard rows...")
                    connection.commit()
            
            connection.commit()
            print(f"✓ Billboard data loaded: {row_count:,} rows processed")
            return True
            
    except Exception as e:
        print(f"✗ Error loading Billboard data: {e}")
        connection.rollback()
        return False


def print_statistics():
    """Print loading statistics."""
    print(f"\n{'='*60}")
    print("Loading Statistics")
    print(f"{'='*60}")
    print(f"Billboard rows processed:    {stats['billboard_rows_processed']:,}")
    print(f"Spotify rows processed:      {stats['spotify_rows_processed']:,}")
    print(f"Artists inserted:            {stats['artists_inserted']:,}")
    print(f"Albums inserted:             {stats['albums_inserted']:,}")
    print(f"Tracks inserted:             {stats['tracks_inserted']:,}")
    print(f"Genres inserted:             {stats['genres_inserted']:,}")
    print(f"Track-Genre links inserted:  {stats['track_genres_inserted']:,}")
    print(f"{'='*60}\n")


def main():
    """Main execution function."""
    print("\n" + "="*60)
    print("Mousiki Dataset Loader")
    print("="*60)
    
    connection = None
    cursor = None
    
    try:
        # Connect to database
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        cursor = connection.cursor()
        print(f"✓ Connected to MySQL database: {MYSQL_DATABASE}")
        
        # Load datasets
        print("\nStarting data import...")
        
        # Load Spotify first (has more metadata)
        if not load_spotify_data(connection, cursor):
            print("\n✗ Failed to load Spotify data")
            sys.exit(1)
        
        # Load Billboard (will update popularity for existing tracks)
        if not load_billboard_data(connection, cursor):
            print("\n✗ Failed to load Billboard data")
            sys.exit(1)
        
        # Print statistics
        print_statistics()
        
        print("✓ All datasets loaded successfully!")
        
    except mysql.connector.Error as e:
        print(f"✗ Database error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n✗ Import interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            print("\n✓ Database connection closed")


if __name__ == "__main__":
    main()
