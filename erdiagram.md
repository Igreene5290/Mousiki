```mermaid
erDiagram
    %% User & Authentication
    user {
        INT user_id PK
        VARCHAR email UK
        VARCHAR password_hash
        DATETIME created_at
    }

    user_profile {
        INT user_id PK,FK
        VARCHAR display_name
        VARCHAR zip_code
        VARCHAR age_group
    }

    session {
        INT session_id PK
        INT user_id FK
        VARCHAR token UK
        DATETIME created_at
        DATETIME expires_at
    }

    %% Music Core
    artist {
        INT artist_id PK
        VARCHAR name
    }

    album {
        INT album_id PK
        VARCHAR title
        INT artist_id FK
        INT release_year
    }

    genre {
        INT genre_id PK
        VARCHAR name UK
    }

    track {
        INT track_id PK
        VARCHAR title
        INT artist_id FK
        INT album_id FK
        INT popularity
    }

    track_genre {
        INT track_id PK,FK
        INT genre_id PK,FK
    }

    track_features {
        INT track_id PK,FK
        DECIMAL energy
        DECIMAL danceability
        DECIMAL acousticness
        DECIMAL valence
    }

    %% Playlists
    playlist {
        INT playlist_id PK
        INT user_id FK
        VARCHAR name
        DATETIME created_at
    }

    playlist_track {
        INT playlist_id PK,FK
        INT track_id PK,FK
        DATETIME added_at
    }

    %% User Preferences
    user_genre_preference {
        INT user_id PK,FK
        INT genre_id PK,FK
    }

    user_preferences {
        INT user_id PK,FK
        DECIMAL energy
        DECIMAL danceability
        DECIMAL acousticness
        DECIMAL valence
        VARCHAR popularity_pref
    }

    %% User Interactions
    user_rating {
        INT user_id PK,FK
        INT track_id PK,FK
        INT rating
    }

    user_like {
        INT user_id PK,FK
        INT track_id PK,FK
    }

    user_recommendation {
        INT user_id PK,FK
        INT track_id PK,FK
        DECIMAL score
    }

    %% Charts & Data Sources
    chart {
        INT track_id PK,FK
        INT chart_position
        DATE chart_date PK
    }

    data_source {
        INT source_id PK
        VARCHAR source_name
        DATE import_date
    }

    track_source_link {
        INT track_id PK,FK
        INT source_id PK,FK
    }

    %% Activity Log
    user_activity {
        INT activity_id PK
        INT user_id FK
        VARCHAR activity_type
        DATETIME activity_date
    }

    %% Relationships
    user ||--o| user_profile : "has"
    user ||--o{ session : "has"
    user ||--o{ playlist : "creates"
    user ||--o{ user_genre_preference : "prefers"
    user ||--o| user_preferences : "has"
    user ||--o{ user_rating : "rates"
    user ||--o{ user_like : "likes"
    user ||--o{ user_recommendation : "receives"
    user ||--o{ user_activity : "logs"

    artist ||--o{ album : "releases"
    artist ||--o{ track : "performs"

    album ||--o{ track : "contains"

    track ||--o{ track_genre : "has"
    genre ||--o{ track_genre : "categorizes"

    track ||--o| track_features : "has"
    track ||--o{ playlist_track : "in"
    track ||--o{ user_rating : "rated"
    track ||--o{ user_like : "liked"
    track ||--o{ user_recommendation : "recommended"
    track ||--o{ chart : "charted"
    track ||--o{ track_source_link : "from"

    playlist ||--o{ playlist_track : "contains"

    genre ||--o{ user_genre_preference : "preferred"

    data_source ||--o{ track_source_link : "provides"
