import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "nexus_suite.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Chatbot History table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chatbot_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 2. Game Leaderboard table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS game_leaderboard (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_name TEXT NOT NULL,
        score INTEGER NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 3. Image History table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS image_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prompt TEXT NOT NULL,
        style TEXT NOT NULL,
        model TEXT NOT NULL,
        seed INTEGER NOT NULL,
        image_base64 TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 4. CV Profiles table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cv_saved (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        profile_name TEXT UNIQUE NOT NULL,
        cv_json TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()

# Chat helpers
def save_chat_message(session_id, role, content):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chatbot_history (session_id, role, content) VALUES (?, ?, ?)",
        (session_id, role, content)
    )
    conn.commit()
    conn.close()

def get_chat_history(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, content FROM chatbot_history WHERE session_id = ? ORDER BY id ASC",
        (session_id,)
    )
    history = [{"role": row["role"], "content": row["content"]} for row in cursor.fetchall()]
    conn.close()
    return history

def get_chat_sessions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT session_id FROM chatbot_history ORDER BY timestamp DESC")
    sessions = [row["session_id"] for row in cursor.fetchall()]
    conn.close()
    return sessions

def clear_chat_history(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chatbot_history WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()

# Leaderboard helpers
def save_score(player_name, score):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO game_leaderboard (player_name, score) VALUES (?, ?)",
        (player_name, score)
    )
    conn.commit()
    conn.close()

def get_leaderboard(limit=10):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT player_name, score, timestamp FROM game_leaderboard ORDER BY score DESC, timestamp ASC LIMIT ?",
        (limit,)
    )
    leaderboard = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return leaderboard

# Image history helpers
def save_image_generation(prompt, style, model, seed, image_base64):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO image_history (prompt, style, model, seed, image_base64) VALUES (?, ?, ?, ?, ?)",
        (prompt, style, model, seed, image_base64)
    )
    conn.commit()
    conn.close()

def get_image_generations(limit=24):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, prompt, style, model, seed, image_base64, timestamp FROM image_history ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    generations = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return generations

def delete_image_generation(image_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM image_history WHERE id = ?", (image_id,))
    conn.commit()
    conn.close()

# CV profiles helpers
def save_cv_profile(profile_name, cv_data_dict):
    conn = get_connection()
    cursor = conn.cursor()
    cv_json = json.dumps(cv_data_dict)
    cursor.execute(
        "INSERT OR REPLACE INTO cv_saved (profile_name, cv_json) VALUES (?, ?)",
        (profile_name, cv_json)
    )
    conn.commit()
    conn.close()

def get_cv_profiles():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT profile_name FROM cv_saved ORDER BY timestamp DESC")
    profiles = [row["profile_name"] for row in cursor.fetchall()]
    conn.close()
    return profiles

def get_cv_profile_data(profile_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT cv_json FROM cv_saved WHERE profile_name = ?", (profile_name,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row["cv_json"])
    return None

def delete_cv_profile(profile_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cv_saved WHERE profile_name = ?", (profile_name,))
    conn.commit()
    conn.close()
