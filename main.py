from flask import Flask, request, jsonify, render_template
import json
from difflib import get_close_matches
from typing import List, Optional

app = Flask(__name__)


# Load the knowledge base
def load_knowledge_base(file_path: str) -> dict:
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"questions": []}


# Save the knowledge base
def save_knowledge_base(file_path: str, data: dict):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)


# Find the best match for a question
def find_best_match(user_question: str, questions: List[str]) -> Optional[str]:
    user_question = user_question.lower()
    normalized_questions = [q.lower() for q in questions]
    matches = get_close_matches(user_question, normalized_questions, n=1, cutoff=0.95)
    return questions[normalized_questions.index(matches[0])] if matches else None


# Retrieve the answer for a question
def get_answer_for_question(question: str, knowledge_base: dict) -> Optional[str]:
    for q in knowledge_base['questions']:
        if q['question'] == question:
            return q['answer']
    return None


# Chatbot logic
knowledge_base = load_knowledge_base('knowledge_base.json')


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.json.get('message', '').strip()
    if not user_input:
        return jsonify({"response": "Please type something!"})

    best_match = find_best_match(user_input, [q['question'] for q in knowledge_base['questions']])
    if best_match:
        answer = get_answer_for_question(best_match, knowledge_base)
        return jsonify({"response": answer})
    else:
        return jsonify({"response": "I don't know the answer to that. Please teach me!"})


@app.route('/teach_bot', methods=['POST'])
def teach_bot():
    data = request.json
    question = data.get('question', '').strip()
    answer = data.get('answer', '').strip()

    if not question or not answer:
        return jsonify({"response": "Question and answer cannot be empty!"})

    knowledge_base['questions'].append({'question': question, 'answer': answer})
    save_knowledge_base('knowledge_base.json', knowledge_base)
    return jsonify({"response": f"Thank you! I've learned that the answer to '{question}' is '{answer}'."})


if __name__ == '__main__':
    app.run(debug=True)
