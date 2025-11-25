# Campus Notice Scraper

Pure Python scraping engine for campus announcements.

## Prerequisites

- Python 3.10+
- Docker & Docker Compose
- [Poetry](https://python-poetry.org/docs/#installation) (Optional, but recommended)

## Setup

### 1. Database
Start the PostgreSQL database using Docker Compose:

```bash
docker-compose up -d
```

### 2. Environment Variables
Copy the example environment file:

```bash
cp .env.example .env
```

### 3. Install Dependencies

**Using Poetry (Recommended):**
```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

**Using pip:**
```bash
pip install -r requirements.txt
```

## Running the Application

**Using Poetry:**
```bash
poetry run uvicorn app.main:app --reload
```

**Using standard python:**
```bash
uvicorn app.main:app --reload
```

## API Usage

- **Health Check**: `GET /health`
- **Trigger Scrape**: `POST /api/v1/origins/{origin_id}/scrape`
- **Date Range Scrape**: `POST /api/v1/origins/{origin_id}/scrape-range`
  ```json
  {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  }
  ```
