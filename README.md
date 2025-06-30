# Mini SQL Compiler

A Python-based Mini SQL Compiler with a modular backend and an interactive web-based frontend. Designed to simulate core compiler phases, this project offers real-time visualization of lexical, syntactic, and semantic processing of SQL-like input.

## 🧠 Features

- Full web-based compiler simulation
- Four-phase visualization:
  - **Lexical Analysis (Tokens)**
  - **Parsing (Syntax Tree)**
  - **Semantic Checks**
  - **Parse Tree Visualization** using [Mermaid.js](https://mermaid.js.org)
- Flask-powered backend with modular Python files
- Real-time results in browser
- Minimal, lightweight, and educational

## 🌐 Web Interface Overview

The frontend consists of four main panels that reflect different phases of the compiler:

| Section        | Description                      |
|----------------|----------------------------------|
| Token Panel    | Displays the list of tokens      |
| Parse Panel    | Shows syntax parsing structure   |
| Semantic Panel | Displays semantic processing     |
| Tree Panel     | Renders parse tree using Mermaid |

## 📂 Project Structure

Mini_SQL_Compiler/
│
├── backend/
│ ├── create_db.py
│ ├── database.py
│ ├── insert_data.py
│ ├── parse_tree.py
│ ├── project1.sqbpro
│ ├── reset.py
│ ├── server.py # Flask server entry point
│ └── tokens.py
│
├── frontend/
│ ├── index.html
│ ├── style.css
│ └── script.js

shell
Copy
Edit

## 🚀 Getting Started

### 🔹 Prerequisites

- Python 3
- Flask
- Mermaid.js (already embedded or served via CDN)

### 🔹 How to Run the Project

```bash
cd backend
python server.py

Then open your browser and go to:

http://localhost:5000
You can now enter SQL-like queries and watch each compiler phase come to life.

🧑‍💻 Author
Ritesh (RIRI@BUNNY)
GitHub: @Ritesh-1939

📜 License
This project is open-source and available under the MIT License.