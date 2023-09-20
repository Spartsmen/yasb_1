CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        username TEXT,
        FOREIGN KEY(role_id) REFERENCES roles(id);



CREATE TABLE IF NOT EXISTS roles (
     id INTEGER PRIMARY KEY AUTOINCREMENT,
     role_name TEXT UNIQUE;

CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role_name TEXT UNIQUE;


INSERT OR IGNORE INTO roles (role_name) VALUES ('client');
INSERT OR IGNORE INTO roles (role_name) VALUES ('admin');
INSERT OR IGNORE INTO roles (role_name) VALUES ('support');

CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        telegram_id INTEGER UNIQUE);

CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER UNIQUE,
        client_id INTEGER,
        helper_id INTEGER);

CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id INTEGER,
        text TEXT);

INSERT OR IGNORE INTO chats (username, telegram_id) VALUES ('support',-4050412601);
INSERT OR IGNORE INTO chats (username, telegram_id) VALUES ('client',-4063636151);


