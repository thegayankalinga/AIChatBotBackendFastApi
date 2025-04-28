import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def get_learned_response(question):
    conn = sqlite3.connect('knowledge_base.db')
    c = conn.cursor()
    c.execute("SELECT answer FROM learned_responses WHERE question=?", (question,))
    response = c.fetchone()
    conn.close()
    if response:
        return response[0]
    return None

def learn_response(question, answer):
    conn = sqlite3.connect('knowledge_base.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO learned_responses VALUES (?, ?)", (question, answer))
    conn.commit()
    conn.close()