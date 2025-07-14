from config import Config
from dotenv import load_dotenv
from flask import Flask, session, redirect, render_template, request, url_for
import json
from pathlib import Path
import sqlite3

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

@app.route("/")
def get_quiz_questions():
    db_path = Path("data/database/music_questions.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    random_questions = cursor.execute("""
        SELECT id, question_wording, options, correct_answer, explanation, type, difficulty, load_date
        FROM pop_questions
        ORDER BY RANDOM()
        LIMIT 10;""").fetchall()
    conn.close()
    
    questions = [dict(row) for row in random_questions]
    session["questions"] = questions
    session["answers"] = {}
    
    return redirect(url_for("quiz_question", qid=0))


@app.route("/quiz/<int:qid>", methods=["GET", "POST"])
def quiz_question(qid):
    questions = session.get("questions")
    answers = session.get("answers", {})
    
    if questions is None or qid >= len(questions):
        return redirect(url_for("results"))
    
    if request.method == "POST":
        selected = request.form.get("answer")
        if selected:
            answers[str(qid)] = selected
            session["answers"] = answers
            return redirect(url_for("quiz_question", qid=qid + 1))
    
    question = questions[qid]
    options = json.loads(question["options"])
    
    return render_template("quiz_question.html", qid=qid, question=question, options=options)

@app.route("/results")
def results():
    questions = session.get("questions", [])
    answers = session.get("answers", {})
    
    correct_answer_mapping = {
        "A": 0,
        "B": 1,
        "C": 2,
        "D": 3
    }
    
    score = 0
    
    for i, question in enumerate(questions):
        correct_answer = question.get("correct_answer")
        correct_answer_index = correct_answer_mapping.get(correct_answer)
        correct_answer_label = eval(question.get("options"))[correct_answer_index]
        
        if answers.get(str(i)) == correct_answer_label:
            score += 1
        
    return render_template("results.html", score=score, total=len(questions))