import json
from difflib import get_close_matches
from typing import List, Optional


def load_knowledge_base(file_path: str) -> dict:
    """Load the knowledge base from a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Error: Unable to load {file_path}. Starting with an empty knowledge base.")
        return {"questions": []}


def save_knowledge_base(file_path: str, data: dict):
    """Save the knowledge base to a JSON file."""
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)


def find_best_match(user_question: str, questions: List[str]) -> Optional[str]:
    """Find the closest matching question from the knowledge base."""
    user_question = user_question.lower()
    normalized_questions = [q.lower() for q in questions]
    matches = get_close_matches(user_question, normalized_questions, n=1, cutoff=0.7)
    return questions[normalized_questions.index(matches[0])] if matches else None


def get_answer_for_question(question: str, knowledge_base: dict) -> Optional[str]:
    """Retrieve the answer for a given question from the knowledge base."""
    for q in knowledge_base['questions']:
        if q['question'] == question:
            return q['answer']
    return None


def teach_bot(user_input: str, knowledge_base: dict):
    """Teach the bot a new answer for a given user question."""
    while True:
        new_answer = input('Type the answer or "skip" to skip: ').strip()
        if new_answer.lower() == 'skip':
            print("Bot: Skipping this question.")
            break
        elif new_answer:
            knowledge_base['questions'].append({'question': user_input, 'answer': new_answer})
            print(f"Bot: Thank you! I've learned that the answer to '{user_input}' is '{new_answer}'.")
            break
        else:
            print("Bot: The answer cannot be empty. Please provide a valid response or type 'skip'.")


def chat_bot():
    """Main chatbot loop."""
    knowledge_base = load_knowledge_base('knowledge_base.json')
    try:
        while True:
            user_input = input('You: ').strip()
            if not user_input:
                print("Bot: Please type something.")
                continue
            if user_input.lower() == 'quit':
                break
            best_match = find_best_match(user_input, [q['question'] for q in knowledge_base['questions']])
            if best_match:
                answer = get_answer_for_question(best_match, knowledge_base)
                print(f'Bot: {answer}')
            else:
                print("Bot: I don't know the answer. Can you please teach me?")
                teach_bot(user_input, knowledge_base)
    finally:
        save_knowledge_base('knowledge_base.json', knowledge_base)
        print("Bot: Knowledge base saved. Goodbye!")


if __name__ == '__main__':
    chat_bot()
