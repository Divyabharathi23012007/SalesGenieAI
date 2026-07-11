# SalesGenie AI

**AI Sales Assistant & Lead Intelligence Platform**

SalesGenie AI automates lead analysis, prospect research, and AI-generated company insights so sales teams can spend less time on research and more time closing deals. Built as an internship project across a 4-milestone, 6-module roadmap.

## Implementation

| Module | Description |
|---|---|
| 1 — Lead Management & Prospect Database | Create, view, update, delete leads. Track lead lifecycle stage. 
| 2 — Lead Intelligence & Company Analysis | AI-generated business needs, opportunities, industry analysis, and qualification score per lead (via Groq). 
| 3 — AI Outreach Generation | Personalized cold email generation. 
| 4 — Lead Scoring & Recommendation Engine | Conversion likelihood prediction, next-best-action. 
| 5 — Conversation Intelligence & CRM Integration | Sales interaction logging is built; CRM sync and call summarization not started. 
| 6 — Dashboard & Sales Analytics |  Basic lead metrics dashboard built; full pipeline/revenue analytics not started. 

## Tech stack

- **Backend:** FastAPI
- **Database:** PostgreSQL + SQLAlchemy (2.0 style)
- **Frontend:** Streamlit
- **AI:** Groq (`llama-3.3-70b-versatile`)

## Project structure

```
salesgenie/
├── database/
│   ├── connection.py      
│   └── models.py          
├── modules/
│   ├── module1_leads.py           
│   └── module2_intelligence.py    
│   └── module3_outreach.py 
│   └── module4_scoring.py 
│   └── module5_conversation.py 
│   └── module6_dashboard.py 
├── main.py                 # FastAPI app entry point
├── app.py                  # Streamlit frontend
├── requirements.txt
├── .env.example             # Copy to .env and fill in your own values

```

## Setup

### 1. Clone and install dependencies
```bash
git clone <this-repo-url>
cd salesgenie
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
```

### 2. Set up PostgreSQL
Create an empty database named `salesgenie` (e.g. via pgAdmin4). Tables are
created automatically on first run — no manual schema setup needed.

### 3. Configure environment variables
Copy `.env.example` to `.env` and fill in your own values:
```
DATABASE_HOST=localhost
DATABASE_PORT=5432 
DATABASE_NAME=salesgenie
DATABASE_USER=postgres
DATABASE_PASSWORD=your_own_password

GROQ_API_KEY=your_groq_api_key   # free at console.groq.com/keys
```

> ⚠️ Never commit your real `.env` file. Each teammate uses their own local
> database and keys. `.env` is already in `.gitignore`.

### 4. Run it
Two terminals, both from the project root:

```bash
# Terminal 1 — backend
uvicorn main:app --reload
```
Visit `http://127.0.0.1:8000/docs` to explore/test the API directly.

```bash
# Terminal 2 — frontend
streamlit run app.py
```
Opens the dashboard at `http://localhost:8501`.

## API endpoints

# Module 1 and Module 2

| Method | Endpoint | Description |
|---|---|---|
| POST | `/leads` | Create a lead |
| GET | `/leads` | List leads |
| GET | `/leads/{id}` | Get a single lead |
| PUT | `/leads/{id}` | Update a lead |
| DELETE | `/leads/{id}` | Delete a lead |
| POST | `/leads/{id}/interactions` | Log a sales interaction |
| GET | `/leads/{id}/interactions` | Get interaction history |
| POST | `/leads/{id}/analyze` | Run AI analysis on a lead (Module 2) |
| GET | `/leads/{id}/insights` | Get AI-generated insights for a lead |

## Team B - Infosys Springboard Internship

| Member | Module |
|---|---|
| _Gilagalla Karthik_ | Module 1 — Lead Management |
| _Guna Shekar Naidu Khandapu_ | Module 2 — Lead Intelligence 
| _ _ | Module 3 — AI Outreach Generation |
| _Jagadeesh_ | Module 4 — Lead Scoring & Recommendation Engine |
| _Divya Bharathi I_ | Module 5 — Conversation Intelligence & CRM Integration |
| _Gopika Rajendiran_ | Module 6 — Dashboard & Sales Analytics |

## Roadmap

See [`AI_Sales_Intelligence_Platform.pdf`](./AI_Sales_Intelligence_Platform.pdf) in this repo for the full project statement, milestone breakdown, and
architecture/database design.
