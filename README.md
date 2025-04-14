# Django Q&A Forum

A simple Question & Answer forum built with Django that allows users to register, post questions, answer others, like answers, and receive notifications.

## 🚀 Features

- User registration & authentication
- Post, search, and filter questions by tags
- Post and like answers
- Notifications for activity on questions/answers
- Paginated questions, answers, and notifications
- Django messages for feedback

## 🛠️ Tech Stack

- Python 3.x
- Django
- SQLite (can be switched to PostgreSQL)

# 🛠️ Project Setup Instructions

Follow these steps to set up and run the Django Q&A Forum project on your local machine.

---

## 📦 Prerequisites

- Python 3.8 or above
- pip (Python package manager)
- Virtual environment (recommended)
- Git (for cloning repo)
- SQLite (default, or PostgreSQL if configured)

---

## 🧑‍💻 Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/dhilippan28/QandA.git
```

### 2. Activating virtualenvironment

```bash
cd QandA
python -m venv env
source env/bin/activate     # On Windows: env\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Development Server

```bash
python run.py
```
