CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fullname TEXT NOT NULL CHECK(length(trim(fullname)) > 0),
    username TEXT NOT NULL UNIQUE CHECK(length(trim(username)) > 0),
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    theme TEXT DEFAULT 'dark',
    profile_image TEXT DEFAULT 'default-profile.jpg',
    email_notifications INTEGER DEFAULT 1,
    private_profile INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE communities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE CHECK(length(trim(name)) > 0) UNIQUE,
    description TEXT NOT NULL CHECK(length(trim(description)) > 0),
    cover_image TEXT,
    category TEXT NOT NULL CHECK (
        category IN (
            'Programming',
            'Mathematics',
            'Business',
            'Science',
            'Language',
            'Design',
            'Other'
        )
    ),
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE community_members (
    user_id INTEGER NOT NULL,
    community_id INTEGER NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, community_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (community_id) REFERENCES communities(id) ON DELETE CASCADE
);

CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    community_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    tag TEXT NOT NULL CHECK (
        tag IN (
            'Question',
            'Discussion',
            'Resource',
            'Project',
            'Notes'
        )
    ),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (community_id) REFERENCES communities(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL CHECK(length(trim(content)) > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE post_likes (
    user_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(user_id, post_id),
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(post_id) REFERENCES posts(id) ON DELETE CASCADE
);

CREATE INDEX idx_posts_community
ON posts(community_id);

CREATE INDEX idx_posts_user
ON posts(user_id);

CREATE INDEX idx_comments_post
ON comments(post_id);

CREATE INDEX idx_comments_user
ON comments(user_id);

CREATE INDEX idx_members_community
ON community_members(community_id);

CREATE INDEX idx_members_user
ON community_members(user_id);

CREATE INDEX idx_postlikes_post
ON post_likes(post_id);

CREATE INDEX idx_postlikes_user
ON post_likes(user_id);