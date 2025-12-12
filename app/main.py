"""
Mousiki - Music Recommendation App
CS3620 Team Project
"""

import mysql.connector
import os

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Euclid2015!',
    'database': 'mousiki'
}

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def connect_db():
    """Connect to MySQL database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return None


# ============ CRUD OPERATIONS ============

def create_user(conn, email):
    """CREATE - Add a new user to the database."""
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO user (email, password_hash) VALUES (%s, 'default')",
            (email,)
        )
        conn.commit()
        user_id = cursor.lastrowid
        print(f"{Colors.GREEN}✓ Created user with email '{email}' (ID: {user_id}){Colors.RESET}")
        return user_id
    except mysql.connector.Error as e:
        print(f"{Colors.RED}✗ Error: {e}{Colors.RESET}")
        return None
    finally:
        cursor.close()


def read_users(conn):
    """READ - Display all users from the database."""
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT user_id, email, created_at FROM user ORDER BY user_id")
    users = cursor.fetchall()
    cursor.close()
    
    if users:
        print(f"\n{Colors.CYAN}{'─'*50}")
        print(f"  ALL USERS")
        print(f"{'─'*50}{Colors.RESET}")
        for u in users:
            print(f"  {Colors.YELLOW}ID:{Colors.RESET} {u['user_id']}  {Colors.YELLOW}Email:{Colors.RESET} {u['email']}")
        print(f"{Colors.CYAN}{'─'*50}{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}No users found.{Colors.RESET}")
    return users


def update_user(conn, user_id, new_email):
    """UPDATE - Update a user's email."""
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE user SET email = %s WHERE user_id = %s",
            (new_email, user_id)
        )
        conn.commit()
        if cursor.rowcount > 0:
            print(f"{Colors.GREEN}✓ Updated user {user_id}'s email to '{new_email}'{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}User {user_id} not found.{Colors.RESET}")
    except mysql.connector.Error as e:
        print(f"{Colors.RED}✗ Error: {e}{Colors.RESET}")
    finally:
        cursor.close()


def delete_user(conn, user_id):
    """DELETE - Remove a user from the database."""
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM user WHERE user_id = %s", (user_id,))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"{Colors.GREEN}✓ Deleted user {user_id}{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}User {user_id} not found.{Colors.RESET}")
    except mysql.connector.Error as e:
        print(f"{Colors.RED}✗ Error: {e}{Colors.RESET}")
    finally:
        cursor.close()


# ============ MUSIC QUERIES ============

def create_playlist(conn, user_id, playlist_name):
    """Create a new playlist for the current user."""
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO playlist (user_id, name) VALUES (%s, %s)",
            (user_id, playlist_name)
        )
        conn.commit()
        playlist_id = cursor.lastrowid
        print(f"{Colors.GREEN}✓ Created playlist '{playlist_name}' (ID: {playlist_id}){Colors.RESET}")
        return playlist_id
    except mysql.connector.Error as e:
        print(f"{Colors.RED}✗ Error: {e}{Colors.RESET}")
        return None
    finally:
        cursor.close()


def view_my_playlists(conn, user_id):
    """View all playlists for the current user."""
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT p.playlist_id, p.name, p.created_at,
               COUNT(pt.track_id) as track_count
        FROM playlist p
        LEFT JOIN playlist_track pt ON p.playlist_id = pt.playlist_id
        WHERE p.user_id = %s
        GROUP BY p.playlist_id, p.name, p.created_at
        ORDER BY p.created_at DESC
    """
    cursor.execute(query, (user_id,))
    playlists = cursor.fetchall()
    cursor.close()
    
    if playlists:
        print(f"\n{Colors.CYAN}{'─'*60}")
        print(f"  MY PLAYLISTS")
        print(f"{'─'*60}{Colors.RESET}")
        for p in playlists:
            print(f"\n  {Colors.YELLOW}ID:{Colors.RESET} {p['playlist_id']}  {Colors.GREEN}{p['name']}{Colors.RESET}")
            print(f"      {Colors.YELLOW}Tracks:{Colors.RESET} {p['track_count']}  {Colors.YELLOW}Created:{Colors.RESET} {p['created_at']}")
        print(f"\n{Colors.CYAN}{'─'*60}{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}You don't have any playlists yet. Create one!{Colors.RESET}")
    return playlists


def add_track_to_playlist(conn, playlist_id, track_id):
    """Add a track to a playlist."""
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO playlist_track (playlist_id, track_id) VALUES (%s, %s)",
            (playlist_id, track_id)
        )
        conn.commit()
        print(f"{Colors.GREEN}✓ Added track to playlist!{Colors.RESET}")
    except mysql.connector.Error as e:
        if "Duplicate entry" in str(e):
            print(f"{Colors.YELLOW}Track already in this playlist.{Colors.RESET}")
        else:
            print(f"{Colors.RED}✗ Error: {e}{Colors.RESET}")
    finally:
        cursor.close()


def rate_track(conn, user_id, track_id, rating):
    """Rate a track (1-5 stars)."""
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO user_rating (user_id, track_id, rating) 
               VALUES (%s, %s, %s)
               ON DUPLICATE KEY UPDATE rating = %s""",
            (user_id, track_id, rating, rating)
        )
        conn.commit()
        print(f"{Colors.GREEN}✓ Rated track {rating}/5 stars!{Colors.RESET}")
    except mysql.connector.Error as e:
        print(f"{Colors.RED}✗ Error: {e}{Colors.RESET}")
    finally:
        cursor.close()


def get_top_artists(conn, limit=10):
    """Analytical view: Top artists by average track popularity."""
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT a.artist_id, a.name,
               COUNT(t.track_id) as track_count,
               AVG(t.popularity) as avg_popularity,
               MAX(t.popularity) as max_popularity
        FROM artist a
        JOIN track t ON a.artist_id = t.artist_id
        GROUP BY a.artist_id, a.name
        HAVING track_count > 0
        ORDER BY avg_popularity DESC, track_count DESC
        LIMIT %s
    """
    cursor.execute(query, (limit,))
    artists = cursor.fetchall()
    cursor.close()
    
    if artists:
        print(f"\n{Colors.CYAN}{'─'*70}")
        print(f"  TOP {limit} ARTISTS BY POPULARITY")
        print(f"{'─'*70}{Colors.RESET}")
        for i, a in enumerate(artists, 1):
            print(f"\n  {Colors.BOLD}{i:2}.{Colors.RESET} {Colors.GREEN}{a['name']}{Colors.RESET}")
            print(f"      {Colors.YELLOW}Tracks:{Colors.RESET} {a['track_count']}  {Colors.YELLOW}Avg Popularity:{Colors.RESET} {a['avg_popularity']:.1f}  {Colors.YELLOW}Peak:{Colors.RESET} {a['max_popularity']}")
        print(f"\n{Colors.CYAN}{'─'*70}{Colors.RESET}")
    return artists


def search_tracks_by_genre(conn, genre):
    """Search for tracks by genre."""
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT t.track_id, t.title, a.name as artist, al.title as album, t.popularity
        FROM track t
        JOIN artist a ON t.artist_id = a.artist_id
        LEFT JOIN album al ON t.album_id = al.album_id
        JOIN track_genre tg ON t.track_id = tg.track_id
        JOIN genre g ON tg.genre_id = g.genre_id
        WHERE g.name = %s
        ORDER BY t.popularity DESC
        LIMIT 10
    """
    cursor.execute(query, (genre,))
    tracks = cursor.fetchall()
    cursor.close()
    
    if tracks:
        print(f"\n{Colors.CYAN}{'─'*60}")
        print(f"  TOP 10 {genre.upper()} TRACKS")
        print(f"{'─'*60}{Colors.RESET}")
        for i, t in enumerate(tracks, 1):
            album = t['album'] or 'Unknown Album'
            print(f"\n  {Colors.BOLD}{i:2}.{Colors.RESET} {Colors.GREEN}{t['title']}{Colors.RESET} {Colors.YELLOW}(ID: {t['track_id']}){Colors.RESET}")
            print(f"      {Colors.YELLOW}Artist:{Colors.RESET} {t['artist']}")
            print(f"      {Colors.YELLOW}Album:{Colors.RESET} {album}")
        print(f"\n{Colors.CYAN}{'─'*60}{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}No tracks found for genre '{genre}'.{Colors.RESET}")
    return tracks


def get_all_genres(conn):
    """Get list of all genres in database."""
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT name FROM genre ORDER BY name")
    genres = [row['name'] for row in cursor.fetchall()]
    cursor.close()
    return genres


def get_recommendations(conn, genre, limit=10):
    """Get song recommendations based on genre preference."""
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT t.track_id, t.title, a.name as artist, al.title as album, t.popularity
        FROM track t
        JOIN artist a ON t.artist_id = a.artist_id
        LEFT JOIN album al ON t.album_id = al.album_id
        JOIN track_genre tg ON t.track_id = tg.track_id
        JOIN genre g ON tg.genre_id = g.genre_id
        WHERE g.name = %s
        ORDER BY t.popularity DESC
        LIMIT %s
    """
    cursor.execute(query, (genre, limit))
    tracks = cursor.fetchall()
    cursor.close()
    return tracks


# ============ MAIN MENU ============

def show_menu():
    print(f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════╗
║                                                      ║
║   {Colors.BOLD}{Colors.HEADER}M O U S I K I{Colors.RESET}{Colors.CYAN}                                      ║
║   {Colors.RESET}Music Recommendation App{Colors.CYAN}                           ║
║                                                      ║
╠══════════════════════════════════════════════════════╣
║  {Colors.BOLD}USER MANAGEMENT{Colors.RESET}{Colors.CYAN}                                     ║
║   {Colors.YELLOW}[1]{Colors.RESET} View All Users                                 {Colors.CYAN}║
║   {Colors.YELLOW}[2]{Colors.RESET} Update User Email                              {Colors.CYAN}║
║   {Colors.YELLOW}[3]{Colors.RESET} Delete User                                    {Colors.CYAN}║
║                                                      ║
║  {Colors.BOLD}MY PLAYLISTS{Colors.RESET}{Colors.CYAN}                                        ║
║   {Colors.YELLOW}[4]{Colors.RESET} Create Playlist                                {Colors.CYAN}║
║   {Colors.YELLOW}[5]{Colors.RESET} View My Playlists                              {Colors.CYAN}║
║   {Colors.YELLOW}[6]{Colors.RESET} Add Track to Playlist                          {Colors.CYAN}║
║                                                      ║
║  {Colors.BOLD}MUSIC DISCOVERY{Colors.RESET}{Colors.CYAN}                                     ║
║   {Colors.YELLOW}[7]{Colors.RESET} Search Tracks by Genre                         {Colors.CYAN}║
║   {Colors.YELLOW}[8]{Colors.RESET} Get Recommendations                            {Colors.CYAN}║
║   {Colors.YELLOW}[9]{Colors.RESET} Rate a Track                                   {Colors.CYAN}║
║  {Colors.YELLOW}[10]{Colors.RESET} View All Genres                                {Colors.CYAN}║
║                                                      ║
║  {Colors.BOLD}ANALYTICS{Colors.RESET}{Colors.CYAN}                                           ║
║  {Colors.YELLOW}[11]{Colors.RESET} Top Artists                                    {Colors.CYAN}║
║                                                      ║
║   {Colors.RED}[0]{Colors.RESET} Exit                                           {Colors.CYAN}║
║                                                      ║
╚══════════════════════════════════════════════════════╝{Colors.RESET}""")


def get_current_user(conn):
    """Get and validate the current user (simple access control)."""
    while True:
        print(f"\n{Colors.CYAN}{'─'*50}")
        print(f"  ACCESS CONTROL - User Verification")
        print(f"{'─'*50}{Colors.RESET}")
        
        choice = input(f"\n{Colors.YELLOW}[1]{Colors.RESET} Login with existing User ID\n{Colors.YELLOW}[2]{Colors.RESET} Create new account\n{Colors.YELLOW}Enter choice:{Colors.RESET} ").strip()
        
        if choice == '1':
            user_id = input(f"{Colors.YELLOW}Enter your User ID:{Colors.RESET} ").strip()
            if user_id.isdigit():
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT user_id, email FROM user WHERE user_id = %s", (int(user_id),))
                user = cursor.fetchone()
                cursor.close()
                
                if user:
                    print(f"{Colors.GREEN}✓ Welcome back, {user['email']}!{Colors.RESET}")
                    return user['user_id']
                else:
                    print(f"{Colors.RED}✗ User ID not found. Please try again.{Colors.RESET}")
            else:
                print(f"{Colors.RED}✗ Invalid User ID.{Colors.RESET}")
        
        elif choice == '2':
            email = input(f"{Colors.YELLOW}Enter email for new account:{Colors.RESET} ").strip()
            if email:
                user_id = create_user(conn, email)
                if user_id:
                    print(f"{Colors.GREEN}✓ Account created! Your User ID is: {user_id}{Colors.RESET}")
                    print(f"{Colors.CYAN}Remember this ID for future logins.{Colors.RESET}")
                    return user_id
        else:
            print(f"{Colors.RED}✗ Invalid choice.{Colors.RESET}")


def main():
    """Main application loop."""
    clear_screen()
    print(f"""
{Colors.CYAN}
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
          Welcome to {Colors.BOLD}MOUSIKI{Colors.RESET}{Colors.CYAN}  
          Your Personal Music Discovery App
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
{Colors.RESET}""")
    
    conn = connect_db()
    if not conn:
        print(f"{Colors.RED}Could not connect to database. Exiting.{Colors.RESET}")
        return
    
    print(f"{Colors.GREEN}✓ Connected to Mousiki database{Colors.RESET}")
    
    # Simple access control - get current user
    current_user_id = get_current_user(conn)
    print(f"\n{Colors.CYAN}{'─'*50}")
    print(f"  Logged in as User ID: {current_user_id}")
    print(f"{'─'*50}{Colors.RESET}")
    
    while True:
        show_menu()
        choice = input(f"\n{Colors.YELLOW}Enter choice:{Colors.RESET} ").strip()
        
        if choice == '1':
            # View all users
            read_users(conn)
        
        elif choice == '2':
            # UPDATE user
            print(f"\n{Colors.CYAN}{'─'*40}")
            print(f"  UPDATE USER")
            print(f"{'─'*40}{Colors.RESET}")
            read_users(conn)
            user_id = input(f"{Colors.YELLOW}Enter user ID to update:{Colors.RESET} ").strip()
            new_email = input(f"{Colors.YELLOW}New email:{Colors.RESET} ").strip()
            if user_id.isdigit() and new_email:
                update_user(conn, int(user_id), new_email)
            else:
                print(f"{Colors.RED}Invalid input.{Colors.RESET}")
        
        elif choice == '3':
            # DELETE user
            print(f"\n{Colors.CYAN}{'─'*40}")
            print(f"  DELETE USER")
            print(f"{'─'*40}{Colors.RESET}")
            read_users(conn)
            user_id = input(f"{Colors.YELLOW}Enter user ID to delete:{Colors.RESET} ").strip()
            if user_id.isdigit():
                confirm = input(f"{Colors.RED}Delete user {user_id}? (y/n):{Colors.RESET} ").strip().lower()
                if confirm == 'y':
                    delete_user(conn, int(user_id))
            else:
                print(f"{Colors.RED}Invalid user ID.{Colors.RESET}")
        
        elif choice == '4':
            # Create playlist
            print(f"\n{Colors.CYAN}{'─'*40}")
            print(f"  CREATE PLAYLIST")
            print(f"{'─'*40}{Colors.RESET}")
            playlist_name = input(f"{Colors.YELLOW}Playlist name:{Colors.RESET} ").strip()
            if playlist_name:
                create_playlist(conn, current_user_id, playlist_name)
            else:
                print(f"{Colors.RED}Playlist name is required.{Colors.RESET}")
        
        elif choice == '5':
            # View my playlists
            view_my_playlists(conn, current_user_id)
        
        elif choice == '6':
            # Add track to playlist
            print(f"\n{Colors.CYAN}{'─'*40}")
            print(f"  ADD TRACK TO PLAYLIST")
            print(f"{'─'*40}{Colors.RESET}")
            playlists = view_my_playlists(conn, current_user_id)
            if playlists:
                playlist_id = input(f"{Colors.YELLOW}Enter playlist ID:{Colors.RESET} ").strip()
                track_id = input(f"{Colors.YELLOW}Enter track ID:{Colors.RESET} ").strip()
                if playlist_id.isdigit() and track_id.isdigit():
                    add_track_to_playlist(conn, int(playlist_id), int(track_id))
                else:
                    print(f"{Colors.RED}Invalid input.{Colors.RESET}")
        
        elif choice == '7':
            # Search tracks
            print(f"\n{Colors.CYAN}{'─'*40}")
            print(f"  SEARCH TRACKS")
            print(f"{'─'*40}{Colors.RESET}")
            genres = get_all_genres(conn)
            print(f"{Colors.YELLOW}Popular genres:{Colors.RESET} {', '.join(genres[:10])}...")
            genre = input(f"{Colors.YELLOW}Enter genre:{Colors.RESET} ").strip().lower()
            search_tracks_by_genre(conn, genre)
        
        elif choice == '8':
            # Get recommendations
            print(f"\n{Colors.CYAN}{'─'*40}")
            print(f"  GET RECOMMENDATIONS")
            print(f"{'─'*40}{Colors.RESET}")
            genre = input(f"{Colors.YELLOW}Enter your favorite genre:{Colors.RESET} ").strip().lower()
            tracks = get_recommendations(conn, genre, 10)
            if tracks:
                print(f"\n{Colors.CYAN}{'─'*60}")
                print(f"  RECOMMENDED {genre.upper()} TRACKS FOR YOU")
                print(f"{'─'*60}{Colors.RESET}")
                for i, t in enumerate(tracks, 1):
                    album = t['album'] or 'Unknown Album'
                    print(f"\n  {Colors.BOLD}{i:2}.{Colors.RESET} {Colors.GREEN}{t['title']}{Colors.RESET} {Colors.YELLOW}(ID: {t.get('track_id', 'N/A')}){Colors.RESET}")
                    print(f"      {Colors.YELLOW}Artist:{Colors.RESET} {t['artist']}")
                    print(f"      {Colors.YELLOW}Album:{Colors.RESET} {album}")
                print(f"\n{Colors.CYAN}{'─'*60}{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}No recommendations found for that genre.{Colors.RESET}")
        
        elif choice == '9':
            # Rate a track
            print(f"\n{Colors.CYAN}{'─'*40}")
            print(f"  RATE A TRACK")
            print(f"{'─'*40}{Colors.RESET}")
            track_id = input(f"{Colors.YELLOW}Enter track ID:{Colors.RESET} ").strip()
            rating = input(f"{Colors.YELLOW}Rating (1-5 stars):{Colors.RESET} ").strip()
            if track_id.isdigit() and rating.isdigit():
                rating_int = int(rating)
                if 1 <= rating_int <= 5:
                    rate_track(conn, current_user_id, int(track_id), rating_int)
                else:
                    print(f"{Colors.RED}Rating must be between 1 and 5.{Colors.RESET}")
            else:
                print(f"{Colors.RED}Invalid input.{Colors.RESET}")
        
        elif choice == '10':
            # View genres
            genres = get_all_genres(conn)
            print(f"\n{Colors.CYAN}{'─'*50}")
            print(f"  ALL GENRES ({len(genres)})")
            print(f"{'─'*50}{Colors.RESET}")
            # Display in 3 columns
            for i in range(0, len(genres), 3):
                row = genres[i:i+3]
                print("  " + "  ".join(f"{Colors.YELLOW}{g:<20}{Colors.RESET}" for g in row))
            print(f"{Colors.CYAN}{'─'*50}{Colors.RESET}")
        
        elif choice == '11':
            # Top Artists analytics
            get_top_artists(conn, 10)
        
        elif choice == '0':
            print(f"\n{Colors.CYAN}Thanks for using Mousiki! Goodbye!{Colors.RESET}\n")
            break
        
        else:
            print(f"{Colors.RED}Invalid choice.{Colors.RESET}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        clear_screen()
    
    conn.close()


if __name__ == "__main__":
    main()
