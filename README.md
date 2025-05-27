# Research Assistant Flask Application

A Flask-based web application that uses Language Model (LM) agents to research and gather information from various online sources.

## Features

- LM-powered research tools
- Support for multiple data sources:
  - Web pages
  - Blog posts
  - News articles
  - PDF documents
  - Case studies
  - Video content
- PostgreSQL database integration
- Factory pattern architecture
- Blueprint-based routing

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```
FLASK_APP=app
FLASK_ENV=development
DATABASE_URL=postgresql://username:password@localhost:5432/dbname
```

4. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

5. Run the application:
```bash
flask run
```

## Project Structure

```
research_assistant/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   ├── models/
│   ├── blueprints/
│   ├── services/
│   └── utils/
├── tests/
├── migrations/
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## Testing

Run tests using pytest:
```bash
pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 