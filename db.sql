-- User/Auth Tables

CREATE TABLE user (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_profile (
    user_id INT PRIMARY KEY,
    display_name VARCHAR(255),
    zip_code VARCHAR(10),
    age_group VARCHAR(20),
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

CREATE TABLE session (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token VARCHAR(255) NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

-- Music Tables

CREATE TABLE artist (
    artist_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE album (
    album_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    artist_id INT,
    release_year INT,
    FOREIGN KEY (artist_id) REFERENCES artist(artist_id)
);

CREATE TABLE genre (
    genre_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE track (
    track_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    artist_id INT,
    album_id INT,
    popularity INT DEFAULT 0,
    FOREIGN KEY (artist_id) REFERENCES artist(artist_id),
    FOREIGN KEY (album_id) REFERENCES album(album_id)
);

CREATE TABLE track_genre (
    track_id INT,
    genre_id INT,
    PRIMARY KEY (track_id, genre_id),
    FOREIGN KEY (track_id) REFERENCES track(track_id),
    FOREIGN KEY (genre_id) REFERENCES genre(genre_id)
);

-- Playlist Tables

CREATE TABLE playlist (
    playlist_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

CREATE TABLE playlist_track (
    playlist_id INT,
    track_id INT,
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (playlist_id, track_id),
    FOREIGN KEY (playlist_id) REFERENCES playlist(playlist_id),
    FOREIGN KEY (track_id) REFERENCES track(track_id)
);
