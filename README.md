# AI SQL AGENT

AI agent that lets you to talk to your database using natural language. All locally.

## Install

Make sure you have [`uv` installed](https://docs.astral.sh/uv/getting-started/installation/).

Clone the repository:

```bash
git clone [https://github.com/neelimagoogly/STREAMING-LANGCHAIN-SQL-AGENT.git](https://github.com/neelimagoogly/STREAMING-LANGCHAIN-SQL-AGENT.git) .
cd querymancer
```

Install Python:

```bash
uv python install 3.12.8
```

Create and activate a virtual environment:

```bash
uv venv
source .venv/bin/activate
```

Install dependencies:

```bash
uv sync
```

Install package in editable mode:

```bash
uv pip install -e .
```

Install pre-commit hooks:

```bash
uv run pre-commit install
```

### Create SQLite database

You can use any SQLlite database. This project comes with a sample script that can create one for you:

```sh
bin/create-database
```
or
```python
python data/create-database.py
```

This should create a file called `ecommerce.sqlite` in the `data` directory. Here's a diagram of the database schema:

![SQLite database schema](.github/db-schema.png)

### API Keys

Querymancer now uses cloud-based LLM services for inference. You'll need API keys to use these services:

**Groq API** - Get your API key from https://console.groq.com/keys


Copy the `.env.example` file to `.env` and add your API keys inside:

```bash
cp .env.example .env
```

Your `.env` file should contain:
```
GROQ_API_KEY=your_groq_api_key_here
```

Look into the [`config.py`](querymancer/config.py) file to set your preferred model.

## Run the Streamlit app

```bash
streamlit run app.py
```

