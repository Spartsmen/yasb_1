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
update users set role = (select role_name from roles where id = 2) where user_id = 768988037;
