DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS expense;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE expense (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id INTEGER NOT NULL,
    date_entered DATE DEFAULT CURRENT_DATE,
    payee TEXT NOT NULL,
    category TEXT NOT NULL,
    sub_category TEXT NOT NULL,
    owner TEXT NOT NULL,
    amount FLOAT,
    FOREIGN KEY (owner_id) REFERENCES user (id)
);

CREATE TABLE tracker (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_entered DATE DEFAULT CURRENT_DATE,
    item TEXT NOT NULL,
    category TEXT NOT NULL,
    date_ended DATE
);