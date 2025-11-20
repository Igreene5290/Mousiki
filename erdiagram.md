erDiagram

    USER ||--|| USER_PROFILE : "has"
    USER ||--o{ SESSION : "creates"
    USER ||--o{ PLAYLIST : "owns"

    ARTIST ||--o{ ALBUM : "has"
    ARTIST ||--o{ TRACK : "performs"

    ALBUM ||--o{ TRACK : "contains"

    GENRE ||--o{ TRACK_GENRE : ""
    TRACK ||--o{ TRACK_GENRE : ""

    PLAYLIST ||--o{ PLAYLIST_TRACK : "has"
    TRACK ||--o{ PLAYLIST_TRACK : "included in"

    USER {
        int user_id PK
        varchar email
        varchar password_hash
        datetime created_at
    }

    USER_PROFILE {
        int user_id PK, FK
        varchar display_name
        varchar zip_code
        varchar age_group
    }

    SESSION {
        int session_id PK
        int user_id FK
        varchar token
        datetime created_at
        datetime expires_at
    }

    ARTIST {
        int artist_id PK
        varchar name
    }

    ALBUM {
        int album_id PK
        varchar title
        int artist_id FK
        int release_year
    }

    GENRE {
        int genre_id PK
        varchar name
    }

    TRACK {
        int track_id PK
        varchar title
        int artist_id FK
        int album_id FK
        int popularity
    }

    TRACK_GENRE {
        int track_id PK, FK
        int genre_id PK, FK
    }

    PLAYLIST {
        int playlist_id PK
        int user_id FK
        varchar name
        datetime created_at
    }

    PLAYLIST_TRACK {
        int playlist_id PK, FK
        int track_id PK, FK
        datetime added_at
    }
