# Calorie Tracker

A Django web app for tracking daily calorie and macronutrient intake.

## Stack
Python, Django, SQLite

## Features
- Custom user model with automatic calorie/macro goal calculation
- Full CRUD for Eaters, Products, Meals, Meal Entries
- Search, pagination, meal duplication

## Setup
```bash
python manage.py migrate
python manage.py loaddata tracker/fixtures/products_fixture.json
python manage.py runserver
```