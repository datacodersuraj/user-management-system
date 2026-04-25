import re
import bcrypt
from db import get_connection

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(),bcrypt.gensalt()).decode()

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def is_strong_password(password: str) -> bool:
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

def create_user(username: str, password: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            return False, "Username already exists"
        
        hashed = hash_password(password)
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed))
        conn.commit()
        return True, None
    except Exception as e:
        return False, str(e)
    finally:
        cur.close()
        conn.close()

def get_user(username: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, password FROM users WHERE username = %s", (username,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def update_user(old_username: str, new_username: str, new_password: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        if new_username != old_username:
            cur.execute("SELECT id FROM users WHERE username = %s", (new_username,))
            if cur.fetchone():
                return False, "new_username_exists"
            
        hashed = hash_password(new_password)
        cur.execute("UPDATE users SET username=%s, password=%s WHERE username=%s", (new_username, hashed, old_username))
        conn.commit()
        return True, None
    except Exception as e:
        return False, str(e)
    finally:
        cur.close()
        conn.close()

def delete_user(username: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE username=%s", (username,))
    conn.commit()
    cur.close()
    conn.close()            