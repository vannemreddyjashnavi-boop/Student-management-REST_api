# Student Management REST API

A Python REST API built using Flask and SQLite for managing student records.

## Technologies Used

- Python
- Flask
- SQLite
- REST API
- JSON

## Features

- Create student records
- View all students
- View individual student
- Update student details
- Delete student records
- API key authentication
- Input validation
- SQLite database integration

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /students | Get all students |
| GET | /students/<id> | Get a student |
| POST | /students | Create a student |
| PUT | /students/<id> | Update a student |
| DELETE | /students/<id> | Delete a student |

## Installation

```bash
pip install -r requirements.txt
