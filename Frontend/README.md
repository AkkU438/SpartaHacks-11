# FinFancy Frontend

A subscription and budget tracking dashboard.

## Pages

- `index.html` - Landing page
- `login.html` - User login
- `signup.html` - User registration
- `admin.html` - Dashboard (requires authentication)

## Features

- Budget tracking with progress bar
- Upcoming subscriptions list
- Daily spending/transactions view
- Monthly spending chart by category
- Savings goals management
- Mock Plaid bank connection

## Usage

The frontend is served by the FastAPI backend as static files. Start the backend server:

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 5000
```

Then open http://localhost:5000 in your browser.
