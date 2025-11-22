# StockMaster - Setup Instructions

## Prerequisites
- Python 3.10 or higher
- Git

## Setup Steps

### 1. Clone the Repository
```bash
git clone https://github.com/NevanNunes/StockMaster.git
cd StockMaster
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations
```bash
python manage.py migrate
```

### 5. Create Superuser
```bash
python manage.py createsuperuser
# Or use the pre-created one:
# Username: admin
# Password: admin123
```

### 6. Load Seed Data
```bash
python manage.py seed_data
```

### 7. Run Development Server
```bash
python manage.py runserver
```

### 8. Access the Application
- **Frontend**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **API Root**: http://127.0.0.1:8000/api/inventory/

## For Hackathon Team

### Backend Dev 1 (Advanced Features)
```bash
git checkout feature/advanced-features
pip install reportlab  # For PDF generation
```

### Backend Dev 2 (Auth & Security)
```bash
git checkout -b feature/auth
# Work on authentication features
```

### Frontend Dev (UI/UX)
```bash
git checkout -b feature/ui
# Work on templates and static files
```

## Common Commands

```bash
# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Run tests
python manage.py test

# Create superuser
python manage.py createsuperuser

# Collect static files (for production)
python manage.py collectstatic
```

## Troubleshooting

### "No module named 'django'"
```bash
pip install -r requirements.txt
```

### "Port already in use"
```bash
python manage.py runserver 8001
```

### Database locked
```bash
# Stop the server and restart
```
