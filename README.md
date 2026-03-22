# Finance
Web app simulating real-time stock trading. Designed to showcase strong backend logic, secure user authentication, and API data integration—key skills for database management and backend development roles.

# 📈 Financial Portfolio Management Platform

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)]()
[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)]()
[![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)]()

## 📝 Overview
This project is a full-stack web application that simulates real-time stock trading and portfolio management. Built as the capstone for CS50, this platform demonstrates robust backend logic, relational database architecture, and secure user session handling. 

Users can register for an account, look up real-time stock quotes via external API integration, "buy" and "sell" shares using a simulated cash balance, and track their complete transaction history.

## ⚙️ Core Technologies
* **Backend:** Python, Flask
* **Database:** SQLite (Normalized tables for Users and Transactions)
* **Frontend:** HTML5, CSS3, Bootstrap (Jinja2 Templating)
* **Deployment:** Gunicorn, Render
* **Security:** `werkzeug.security` for password hashing, secure session management

## 🚀 Technical Highlights
* **RESTful API Integration:** Engineered the backend to asynchronously fetch and parse JSON data from the CS50 finance API to provide real-time market pricing.
* **Relational Database Design:** Architected a SQLite database to maintain ACID compliance across user ledgers and transaction histories. Complex SQL queries (utilizing `GROUP BY` and `HAVING` clauses) are used to dynamically calculate the user's current portfolio holdings.
* **Authentication & Security:** Implemented secure user registration and login routes. User passwords are encrypted using strong hashing algorithms before database insertion to ensure data protection.
* **Dynamic Routing:** Utilized Flask to handle complex GET and POST requests, managing dynamic URL routing and seamless data passing between the backend Python logic and frontend Jinja templates.

## 💻 Local Installation

To run this project locally on your machine:

1. Clone the repository:
   >
   git clone [https://github.com/](https://github.com/)[Your-GitHub-Username]/cs50-finance.git
Navigate to the project directory:
>
cd cs50-finance
Install the required dependencies:
>
pip install -r requirements.txt
Initialize the database and run the Flask application:
>
flask run

👨‍💻 Author
Alik Ghosh 
Mail- user.alikghosh@gmail.com
