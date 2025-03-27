# 📅 Office Hours Scheduling System

This is a Flask-based web application that allows students to book and cancel appointments with professors during their office hours.

## 🚀 Features

- Student and professor login system
- Booking and canceling appointments
- Dynamic appointment availability per professor
- Waitlisting students when a time slot is full
- Stack-based log of canceled appointments
- Session-based login system
- SQLite database for users and appointments

## 🧠 Data Structures Used

This app uses custom-built data structures to manage appointment logic:

- **Linked List**: to store active appointments for each professor.
- **Queue (FIFO)**: to manage a waitlist of students.
- **Stack (LIFO)**: to track canceled appointments for possible restoration or review.

## 🗂 Technologies

- Python 3
- Flask
- SQLite
- HTML/CSS
- Gunicorn (for production deployment)
- Git & GitHub


