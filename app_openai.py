import json
import os
from dataclasses import dataclass
from typing import List, Dict, Any

import streamlit as st
import yaml
import ollama

from openai import OpenAI

client = OpenAI()

# --------------- Config ---------------
DEFAULT_MODEL = "gpt-4o-mini"   # fast + accurate for grading
TEMPERATURE = float(os.getenv("STUDY_TUTOR_TEMPERATURE", "0.2"))
MAX_CTX = int(os.getenv("STUDY_TUTOR_CTX", "8192"))

# --------------- Types ---------------
@dataclass
class Question:
    id: str
    prompt: str
    acceptable_answers: List[str]
    rubric: str
    hint: str

@dataclass
class Deck:
    title: str
    description: str
    policy: Dict[str, Any]
    questions: List[Question]

# --------------- Utilities ---------------
def load_deck(path: str) -> Deck:
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    meta = raw.get("meta", {})
    questions = [
        Question(
            id=q.get("id"),
            prompt=q.get("prompt"),
            acceptable_answers=q.get("acceptable_answers", []),
            rubric=q.get("rubric", ""),
            hint=q.get("hint", "Consider the key concept and its standard term."),
        )
        for q in raw.get("questions", [])
    ]
    return Deck(
        title=meta.get("title", "Untitled Deck"),
        description=meta.get("description", ""),
        policy=meta.get("policy", {"max_attempts": 3, "reveal_answer_on_failout": False}),
        questions=questions,
    )

EVAL_SYSTEM_PROMPT = (
    """
You are an exacting but supportive grader. You will receive:
1) A question (prompt)
2) An array of acceptable answers (strings)
3) A rubric (text guidance)
4) A student's answer (free text)

Decide if the student's answer is correct. Use the acceptable answers and rubric.
- Be tolerant of small variations, case, punctuation, and minor whitespace.
- If the answer is clearly equivalent or a commonly accepted synonym, mark it correct.
- If in doubt, lean conservative and mark incorrect.
- Provide a brief, actionable hint without revealing the full answer.

Output strictly as JSON in **one line** with this schema:
{"correct": true|false, "hint": "<short advice, no solution>"}
    """
)



def llm_grade(model: str, question: Question, student_answer: str) -> Dict[str, Any]:
    """Ask ChatGPT to grade the response and return JSON."""
    system_prompt = EVAL_SYSTEM_PROMPT
    user_message = json.dumps({
        "prompt": question.prompt,
        "acceptable_answers": question.acceptable_answers,
        "rubric": question.rubric,
        "student_answer": student_answer,
    }, ensure_ascii=False)

    try:
        response = client.chat.completions.create(
            model=model,  # e.g. "gpt-4o-mini" or "gpt-4-turbo"
            temperature=0.2,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )

        text = response.choices[0].message.content.strip()
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1:
            text = text[start:end+1]
        data = json.loads(text)

        return {
            "correct": bool(data.get("correct", False)),
            "hint": str(data.get("hint", "Reflect on the core concept.")),
        }
    except Exception as e:
        return {"correct": False, "hint": "Revisit the main idea and key terms."}


# --------------- Streamlit App ---------------
st.set_page_config(page_title="Study Deck Tutor", page_icon="📚", layout="centered")
st.title("📚 Study Deck Tutor")

with st.sidebar:
    st.header("⚙️ Settings")
    model_name = st.text_input("Model name", value="gpt-4o-mini")
    deck_path = st.text_input("Deck path", value="decks/current_deck.yaml")
    if st.button("Load deck"):
        st.session_state.clear()
        st.session_state["deck_path"] = deck_path
        st.session_state["model_name"] = model_name

# Load deck once
if "deck" not in st.session_state:
    deck_path = st.session_state.get("deck_path", "decks/current_deck.yaml")
    st.session_state["model_name"] = st.session_state.get("model_name", DEFAULT_MODEL)
    deck = load_deck(deck_path)
    st.session_state["deck"] = deck
    st.session_state["idx"] = 0
    st.session_state["attempts"] = 0
    st.session_state["correct"] = 0
    st.session_state["wrong"] = 0
    st.session_state["last_hint"] = ""

# Short alias
D: Deck = st.session_state["deck"]

st.subheader(D.title)
st.caption(D.description)

# Progress bar
total = len(D.questions)
current = st.session_state["idx"]
st.progress(0 if total == 0 else current / total)

if total == 0:
    st.warning("This deck has no questions.")
    st.stop()

# If finished, show summary
if current >= total:
    st.success("All questions attempted.")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("✅ Correct", st.session_state["correct"])
    with col2:
        st.metric("❌ Wrong", st.session_state["wrong"])

    if st.button("Restart deck"):
        st.session_state["idx"] = 0
        st.session_state["attempts"] = 0
        st.session_state["correct"] = 0
        st.session_state["wrong"] = 0
        st.session_state["last_hint"] = ""
    st.stop()

# Active question
q: Question = D.questions[current]
max_attempts = int(D.policy.get("max_attempts", 3))

st.markdown(f"### Question {current + 1} of {total}")
st.write(q.prompt)

answer = st.text_area("Your answer:", key=f"ans_{q.id}")
colA, colB = st.columns([1, 1])

with colA:
    submit = st.button("Submit answer", type="primary")
with colB:
    skip = st.button("Skip question")

if skip:
    st.session_state["wrong"] += 1
    st.session_state["idx"] += 1
    st.session_state["attempts"] = 0
    st.session_state["last_hint"] = ""
    st.rerun()

# Handle submission
if submit:
    if not answer.strip():
        st.info("Please enter an answer.")
        st.stop()

    # Exact fast-path: accept if perfect match (case/whitespace tolerant)
    normalized = answer.strip().lower()
    if any(normalized == a.strip().lower() for a in q.acceptable_answers):
        st.success("Correct! ✨")
        st.session_state["correct"] += 1
        st.session_state["idx"] += 1
        st.session_state["attempts"] = 0
        st.session_state["last_hint"] = ""
        st.rerun()

    # Otherwise ask the LLM grader
    with st.spinner("Grading with Qwen…"):
        result = llm_grade(st.session_state["model_name"], q, answer)

    if result.get("correct"):
        st.success("Correct! ✨")
        st.session_state["correct"] += 1
        st.session_state["idx"] += 1
        st.session_state["attempts"] = 0
        st.session_state["last_hint"] = ""
        st.rerun()
    else:
        st.session_state["attempts"] += 1
        st.session_state["last_hint"] = result.get("hint", "Review the core idea.")

        if st.session_state["attempts"] >= max_attempts:
            st.error("Max attempts reached. Marked as wrong.")
            st.session_state["wrong"] += 1
            st.session_state["idx"] += 1
            st.session_state["attempts"] = 0
            st.session_state["last_hint"] = ""
            st.rerun()
        else:
            st.warning("Not quite. Try again with this advice:")
            st.info(st.session_state["last_hint"])

# Footer: live score
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("✅ Correct", st.session_state["correct"])
with col2:
    st.metric("❌ Wrong", st.session_state["wrong"])
with col3:
    st.metric("Remaining", total - (st.session_state["idx"]))
