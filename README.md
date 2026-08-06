# Calorie Tracker
A Django web app for tracking daily calorie and macronutrient intake.

## Features
- Custom user model with automatic calorie/macro goal calculation
- Full CRUD for Eaters, Products, Meals, Meal Entries
- Search, pagination, meal duplication

## Stack
Python, Django, PostgreSQL, Render

## Deployment
```
Live demo: https://calorietracker-n77d.onrender.com

Test credentials:
- Username: user
- Password: user12345
```

## Installation
```
git clone https://github.com/soberhigher/Calorie-Tracker.git
git checkout -b develop
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```

## Setup
```
cp .env.sample .env
python manage.py migrate
python manage.py createsuperuser
python manage.py loaddata tracker/fixtures/products_fixture.json
python manage.py runserver
```