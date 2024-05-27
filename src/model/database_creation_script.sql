CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    description TEXT,
    merchant_id INTEGER,
    reconciled BOOLEAN NOT NULL,
    date TEXT,
    statement_id INTEGER,
    receipt_path TEXT,
    lat FLOAT,
    long FLOAT,
    account_id NOT NULL,
    transfer_trans_id INTEGER,
    FOREIGN KEY (merchant_id) REFERENCES merchants (id),
    FOREIGN KEY (statement_id) REFERENCES statements (id),
    FOREIGN KEY (account_id) REFERENCES accounts (id),
    FOREIGN KEY (transfer_trans_id) REFERENCES transactions (id)
);

CREATE TABLE amounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    amount FLOAT NOT NULL,
    transaction_id INTEGER NOT NULL,
    description TEXT,
    FOREIGN KEY (transaction_id) REFERENCES transactions (id)
);

CREATE TABLE accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name TEXT NOT NULL,
    amount_index INTEGER,
    description_index INTEGER,
    date_index INTEGER
);

CREATE TABLE statements (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    date TEXT NOT NULL,
    path TEXT,
    account_id INTEGER NOT NULL,
    FOREIGN KEY (account_id) REFERENCES accounts (id)
);

CREATE TABLE merchants (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name TEXT NOT NULL,
    online BOOLEAN NOT NULL,
    rule TEXT
);

CREATE TABLE locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    description TEXT,
    merchant_id INTEGER NOT NULL,
    lat FLOAT NOT NULL,
    long FLOAT NOT NULL,
    FOREIGN KEY (merchant_id) REFERENCES merchants (id)
);

CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name TEXT NOT NULL,
    occasional BOOLEAN NOT NULL
);

CREATE TABLE amount_tags (
    amount_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    FOREIGN KEY (amount_id) REFERENCES amounts (id),
    FOREIGN KEY (tag_id) REFERENCES tags (id)
);

CREATE TABLE mer_tag_defaults (
    merchant_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    FOREIGN KEY (merchant_id) REFERENCES  merchants (id),
    FOREIGN KEY (tag_id) REFERENCES tags (id)
)