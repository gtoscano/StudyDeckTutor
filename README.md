# 🎓 StudyDeckTutor

An **interactive LLM-powered study system** that helps students learn through **active recall**, not passive memorization.

Professors or catechists can create **question decks** in simple YAML files, and students answer them interactively.  
The app provides **instant feedback**, **adaptive hints**, and **performance tracking** — powered by either **Ollama (Qwen)** or **OpenAI models**.

---

## 🧠 Overview

| Feature | Description |
|----------|-------------|
| 💬 Interactive Learning | Students answer one question at a time; the system evaluates and provides feedback. |
| 🧩 Instructor Control | Professors define decks with accepted answers, rubrics, and hints. |
| 🔒 Privacy | Option to run entirely **locally** via Ollama (no data leaves the computer). |
| ☁️ Cloud Option | Use OpenAI’s API for scalable classroom or online setups. |
| 📊 Progress Tracking | Counts correct / wrong answers per session. |
| 🪶 Lightweight | Built with **Streamlit**, runs with one command. |

---

## 🏗️ Repository Structure

```

StudyDeckTutor/
├── app.py                # Streamlit app using Ollama (Qwen)
├── app_openai.py         # Streamlit app using OpenAI API
├── decks/
│   ├── sample_deck.yaml
│   ├── python_basics.yaml
│   ├── catechism_basics.yaml
│   └── precalculus_basics.yaml
├── README.md
├── Pipfile
└── Pipfile.lock

````

---

## ⚙️ Installation (with Pipenv)

### 1. Clone the repository

```bash
git clone https://github.com/gtoscano/StudyDeckTutor.git
cd StudyDeckTutor
````

### 2. Create and activate the environment

```bash
pipenv install
pipenv shell
```

### 3. Install required packages

The required packages will be in the `Pipfile`, but typically include:

```bash
pipenv install streamlit pyyaml openai ollama
```

---

## 🚀 Running the App

### **Option A — Local (Ollama + Qwen)**

Use this when you want full **privacy** and **offline capability**.

1. Install [Ollama](https://ollama.com/download)
2. Start the Ollama service:

   ```bash
   ollama serve
   ```
3. Pull the Qwen model (choose size depending on your GPU):

   ```bash
   ollama pull qwen2.5:3b
   ```
4. Run the app:

   ```bash
   streamlit run app.py
   ```

App will open automatically at:
➡️ **[http://localhost:8501](http://localhost:8501)**

---

### **Option B — Cloud (OpenAI API)**

Use this for **fast and scalable** deployments with OpenAI models.

1. Export your API key:

   ```bash
   export OPENAI_API_KEY="sk-your-key-here"
   ```
2. Run the OpenAI version:

   ```bash
   streamlit run app_openai.py
   ```

💡 You can change the model in the sidebar (e.g. `gpt-4o-mini` or `gpt-4-turbo`).

---

## 🧩 Deck Format (YAML)

Create question decks in the `decks/` directory.
Each file contains metadata and a list of short-answer questions.

Example:

```yaml
meta:
  title: "Intro to Python — Basics"
  description: "Core Python concepts for beginners"
  policy:
    max_attempts: 3
    reveal_answer_on_failout: false

questions:
  - id: q1
    prompt: "What keyword defines a function in Python?"
    acceptable_answers: ["def"]
    hint: "It appears at the start of a function definition."
    rubric: |
      Accept 'def' as the correct keyword. Ignore capitalization differences.
```

---

## 🧭 App Logic

1. Displays one question at a time.
2. If answer is correct → ✅ move on.
3. If incorrect → 💡 show a **hint** (no solution).
4. After 3 failed attempts → mark ❌ wrong and continue.
5. Shows progress and final score at the end.

---

## 🧱 Example Use Cases

| Context               | Use                                                          |
| --------------------- | ------------------------------------------------------------ |
| 🎓 University courses | Professors create subject-specific decks for study practice. |
| ⛪ Faith formation     | Catechists use decks for catechism review.                   |
| 🧮 STEM learning      | Math, programming, or science concept drills.                |
| 📚 Self-learning      | Students build their own decks for exam prep.                |

---

## 🧰 Environment Variables

| Variable                  | Description                                              |
| ------------------------- | -------------------------------------------------------- |
| `OPENAI_API_KEY`          | Required for the OpenAI version (`app_openai.py`)        |
| `STUDY_TUTOR_MODEL`       | Default model name (e.g., `qwen2.5:7b` or `gpt-4o-mini`) |
| `STUDY_TUTOR_CTX`         | Context window for model (default 8192)                  |
| `STUDY_TUTOR_TEMPERATURE` | Model creativity (default 0.2)                           |

---

## 🧮 Example Run (Ollama)

```bash
(StudyDeckTutor) $ ollama serve &
(StudyDeckTutor) $ streamlit run app.py
```

```
📚 Study Deck Tutor
Question 1 of 15
> What keyword defines a function in Python?

✅ Correct! ✨
✅ Correct: 1   ❌ Wrong: 0   Remaining: 14
```

---

## ☁️ Deployment Tips

* Deploy on [Streamlit Cloud](https://streamlit.io/cloud) or [Hugging Face Spaces](https://huggingface.co/spaces)
* For on-premises use, wrap with **Docker**:

  ```bash
  docker build -t studydecktutor .
  docker run -p 8501:8501 studydecktutor
  ```
* Or use **Gunicorn/Nginx** for internal university servers.

---

## 🕊️ Educational Philosophy

> “Faith and reason are like two wings on which the human spirit rises to the contemplation of truth.”
> — *Pope John Paul II, Fides et Ratio*

StudyDeckTutor encourages **ethical**, **active**, and **reflective** learning —
where AI supports understanding, not shortcuts.

---

## 📜 License

MIT License © 2025 [Gregorio Toscano](https://github.com/gtoscano)

---

## 🤝 Contributing

Pull requests are welcome!
If you have new deck ideas (Python, Pre-Calculus, Catechism, World History),
please contribute by adding YAML files under `decks/` and submitting a PR.

---

## 🌍 Acknowledgments

* [Streamlit](https://streamlit.io/) — for the UI framework
* [Ollama](https://ollama.com/) — for local LLM integration
* [OpenAI](https://openai.com/) — for cloud LLM support
* Inspired by the mission of **The Catholic University of America** to form intellect and character through innovation guided by faith and reason.

