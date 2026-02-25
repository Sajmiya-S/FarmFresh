# FarmFresh

A simple and user-friendly **Django E-commerce / Mini Store** project designed to showcase a basic shopping platform.

This application allows users to browse products, add items to cart, and place orders — ideal for learning web development with Python and Django.

## 📌 Features

- Browse product listings with images and descriptions
- Add products to cart
- User authentication (login/register)
- Simple payment integration
- Media upload support
- Django backend with static and template files
- Uses SQLite for data storage

## 📂 Tech Stack

| Technology | Description |
|------------|-------------|
| Python     | Programming language |
| Django     | Web framework |
| HTML/CSS   | Frontend markup and styling |
| SQLite     | Default database |
| Git & GitHub | Version control and repo hosting |

## 🚀 Installation (Local Setup)

1. **Clone the repository**
   ```bash
   git clone https://github.com/Sajmiya-S/FarmFresh.git
2. **Navigate to the project folder**
    ```bash
    cd FarmFresh
3. **Create a virtual environment**
    ```bash
    python -m venv venv
4. **Activate the environment**
    ```bash(Windows)
    venv\Scripts\activate
    ```bash(MacOS/Linux)
    source venv/bin/activate
5. **Install dependencies**
    ```bash
    pip install -r requirements.txt
6. **Apply migrations**
    ```bash
    python manage.py migrate
7. **Create a superuser (optional)**
    ```bash
    python manage.py createsuperuser
8. **Run the development server**
    ```bash
    python manage.py runserver
9. **Open in browser**
    http://localhost:8000/

## 📂 Project Structure

FarmFresh/
│
├── app_name/
├── templates/
├── static/
├── media/
├── manage.py
├── requirements.txt
└── db.sqlite3

## 📖 Learning Purpose

This project is built for learning Django fundamentals including:
-Models
-Views
-Templates
-Authentication
-Cart functionality
-Payment integration
-Media handling