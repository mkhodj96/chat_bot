# ideaShop ChatBot

## 🛒 Overview

The **ideaShop ChatBot** is a digital assistant for Aidea Shop, an art gallery and online store featuring paintings, crafts, photography, and sculptures. This chatbot helps customers and the sales team quickly find information about artworks, artists, and shop offerings using natural language processing and vector-based search. The project demonstrates best practices for building intelligent assistant systems with Python, FastAPI, OpenAI (Azure), ChromaDB, and modern data pipelines.

---
## 🖼️ Screenshots

_Example ChatBot in Action:_

![Chatbot Screenshot](./screenshots.png)  
*ChatBot answering questions about shop products.*

---

## 📦 Technologies Used

- **Backend:** Python, FastAPI, ChromaDB, OpenAI API (Azure), Pandas
- **Frontend:** HTML, JavaScript (optionally React or Vue)
- **Dev Tools:** Poetry, Docker

---

## 📚 Contents

Repository structure:

- `chat_bot/` – Backend chatbot code and API logic
- `chat_bot_preprocessing/` – Data preprocessing and vector DB scripts
- `tests/` – Test suites for chatbot and preprocessing
- `Dockerfile` – For containerized deployment
- `pyproject.toml`, `poetry.lock` – Dependency management
- `.gitignore`, `LICENSE`, `README.md` – Meta files

---

## ⚙️ Setup

### Requirements

- Python 3.9+
- [Poetry](https://python-poetry.org/) for dependency management
- (Optional) Docker
- This project uses Azure OpenAI Service for language and embedding models.

### Install dependencies

```sh
poetry install
```

## 🚀 Usage
Preprocess data and build the vector database:
```sh
poetry run python chat_bot_preprocessing
```
Start the chatbot server:
```sh
poetry run uvicorn chat_bot.main:app --reload
```
Access the chatbot UI at http://localhost:8000

## 🧩 Example Queries
- "Show me available paintings under €500."
- "Who is the artist of 'Imaginary Artwork 3'?"
- "Are there any ceramic sculptures available?"
- "Can you tell me more about the wooden crafts collection?"

## 🌱 Future Development & Contributions
We welcome contributions and ideas to help improve the ideaShop ChatBot! Here are some planned features and areas where you can contribute:
- User Personalization: Each user's conversations should be personalized and securely associated with their account.
- Conversation Summaries & Titles:Every conversation session in the history log should automatically generate a meaningful title and a concise summary for easier reference.
Contributions, ideas, and bug reports are welcome!
Open an issue or submit a pull request.

## 📜 License
This project is licensed under the MIT License.
See the LICENSE file for details.

## 📬 Contact
For questions or support, reach out via GitHub Issues
or contact mkhodj96.





