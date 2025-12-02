# Household Service Management System

A role-based service booking platform built with **Flask** and **SQLAlchemy**.  
Supports Customers, Professionals, and Admins with secure authentication, service search & booking, professional approval, ratings, and profile management. Frontend uses Jinja2 templates with HTML, CSS and Bootstrap.

## Features
- Multi-role system: Customer / Professional / Admin dashboards
- Secure authentication, session & role-based access control
- Service search, booking, and order flow
- Professional signup & approval workflow
- Ratings and reviews for professionals
- Responsive UI using Bootstrap + Jinja2 templates
- Backend: Flask + SQLAlchemy (SQLite/Postgres compatible)

## Tech stack
- Python, Flask, SQLAlchemy
- HTML, CSS, Bootstrap, Jinja2
- (Optional) PostgreSQL / MySQL for production

## Quick start (local)
1. Create & activate virtual environment:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux / Mac
   source venv/bin/activate
