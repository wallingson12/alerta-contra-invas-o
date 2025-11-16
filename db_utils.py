import sqlite3
import hashlib
import os

DB_PATH = "users.db"

# ------------------ FUNÇÕES ------------------

def create_db():
    """Cria o banco de dados e a tabela de usuários."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

    # Cria usuário padrão se não existir
    if not user_exists("wallingson"):
        add_user("wallingson", "senha")

def hash_password(password, salt=None):
    """Gera hash da senha usando SHA256 + salt."""
    if salt is None:
        salt = os.urandom(16).hex()
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256', password.encode(), salt.encode(), 100_000
    ).hex()
    return pwd_hash, salt

def add_user(username, password):
    """Adiciona um usuário novo com senha hashed."""
    pwd_hash, salt = hash_password(password)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
            (username, pwd_hash, salt)
        )
    except sqlite3.IntegrityError:
        pass  # Usuário já existe
    conn.commit()
    conn.close()

def user_exists(username):
    """Retorna True se o usuário existir no DB."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ?", (username,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

def validate_user(username, password):
    """Valida login comparando hash da senha."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT password_hash, salt FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        stored_hash, salt = row
        pwd_hash, _ = hash_password(password, salt)
        return pwd_hash == stored_hash
    return False

# ------------------ EXECUÇÃO ------------------

if __name__ == "__main__":
    create_db()
    print("Banco de dados inicializado e usuário padrão criado, se necessário.")
