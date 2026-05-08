import os
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash

DB_PATH = os.environ.get('DATABASE_URL', 'database.db')


def _table_columns(conn, table_name):
    cursor = conn.execute(f"PRAGMA table_info({table_name})")
    rows = cursor.fetchall()
    if rows and isinstance(rows[0], sqlite3.Row):
        return [row['name'] for row in rows]
    return [row[1] for row in rows]


def get_db():
    if os.path.dirname(DB_PATH):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    if os.path.dirname(DB_PATH):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Create tables with proper schema
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0,
        created_at TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS properties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        price REAL,
        location TEXT,
        bedrooms INTEGER,
        bathrooms INTEGER,
        area_sqft INTEGER,
        property_type TEXT,
        status TEXT,
        image_filename TEXT,
        created_at TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS enquiries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        property_id INTEGER,
        name TEXT,
        email TEXT,
        message TEXT,
        property TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        property_id INTEGER
    )
    ''')

    conn.commit()

    existing_tables = [row[0] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]

    # Handle legacy columns and migrations
    if 'users' in existing_tables:
        columns = _table_columns(conn, 'users')
        if 'password_hash' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN password_hash TEXT')
        if 'is_admin' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0')
        if 'created_at' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN created_at TEXT')
        if 'password' in columns:
            rows = cursor.execute('SELECT id, password FROM users WHERE password IS NOT NULL').fetchall()
            for row in rows:
                hashed = generate_password_hash(row['password'])
                cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (hashed, row['id']))

    if 'properties' in existing_tables:
        columns = _table_columns(conn, 'properties')
        alter_columns = {
            'description': 'TEXT',
            'bedrooms': 'INTEGER',
            'bathrooms': 'INTEGER',
            'area_sqft': 'INTEGER',
            'property_type': 'TEXT',
            'status': 'TEXT',
            'image_filename': 'TEXT',
            'created_at': 'TEXT'
        }
        for name, col_type in alter_columns.items():
            if name not in columns:
                cursor.execute(f'ALTER TABLE properties ADD COLUMN {name} {col_type}')
        if 'image' in columns and 'image_filename' in columns:
            cursor.execute('UPDATE properties SET image_filename = image WHERE image_filename IS NULL OR image_filename = ""')

    if 'enquiries' in existing_tables:
        columns = _table_columns(conn, 'enquiries')
        if 'user_id' not in columns:
            cursor.execute('ALTER TABLE enquiries ADD COLUMN user_id INTEGER')
        if 'property_id' not in columns:
            cursor.execute('ALTER TABLE enquiries ADD COLUMN property_id INTEGER')
        if 'name' not in columns:
            cursor.execute('ALTER TABLE enquiries ADD COLUMN name TEXT')
        if 'email' not in columns:
            cursor.execute('ALTER TABLE enquiries ADD COLUMN email TEXT')
        if 'message' not in columns:
            cursor.execute('ALTER TABLE enquiries ADD COLUMN message TEXT')
        if 'property' not in columns:
            cursor.execute('ALTER TABLE enquiries ADD COLUMN property TEXT')
        if 'created_at' not in columns:
            cursor.execute('ALTER TABLE enquiries ADD COLUMN created_at TEXT')

    if 'favorites' not in existing_tables:
        cursor.execute('''
        CREATE TABLE favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            property_id INTEGER
        )
        ''')

    # Seed admin account if not exists
    admin_exists = cursor.execute('SELECT id FROM users WHERE is_admin = 1').fetchone()
    if not admin_exists:
        cursor.execute(
            'INSERT OR IGNORE INTO users (username, email, password_hash, is_admin, created_at) VALUES (?, ?, ?, 1, ?)',
            ('admin', 'admin@gmail.com', generate_password_hash('1234'), datetime.now().isoformat())
        )

    conn.commit()
    conn.close()
