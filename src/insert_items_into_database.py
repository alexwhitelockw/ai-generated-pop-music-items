from datetime import datetime
import json
import logging
from pathlib import Path
import re
import sqlite3


logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

if __name__ == "__main__":
    db_path = Path("basic-app/data/database/music_questions.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pop_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_wording TEXT NOT NULL,
            options TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            explanation TEXT NOT NULL,
            type TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            load_date TEXT
        );
    """)
    
    json_path = Path("data/pop_questions/pop_questions.json")
    with open(json_path, "r", encoding="utf-8") as f:
        pop_questions = json.load(f)
        logging.info("Pop Questions loaded.")
    
    for pop_question_str in pop_questions:
        try:
            pop_question = json.loads(pop_question_str)
            if "error" not in pop_question.keys():
                cursor.execute(
                    """
                    INSERT INTO pop_questions
                    (question_wording, options, correct_answer, explanation, type, difficulty, load_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, 
                    (
                        pop_question.get("question"),
                        re.sub(r"[A-D]\.\s|[A-D]\)\s", "", json.dumps(pop_question.get("options"))),
                        pop_question.get("answer"),
                        pop_question.get("explanation"),
                        pop_question.get("type"),
                        pop_question.get("difficulty"),
                        datetime.now().strftime("%Y-%m-%d %H:%M:%OS")
                    )
                )
                logging.info(f"Inserted Question: {pop_question.get('question')[:50]}.")
        except (json.JSONDecodeError, KeyError) as e:
            logging.error(f"Failed to parse question: {pop_question_str}. Error: {e}")
        
    conn.commit()
    logging.info(f"Successfully inserted {len(pop_questions)} questions.")
