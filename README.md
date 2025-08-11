# 🚌 Simple Bus Booking System (Python Tkinter)

A GUI-based **Bus Booking System** built using **Python Tkinter** during our **2nd year of academics** as part of a **24-hour workshop challenge**.  
The project includes **user authentication**, **ticket booking**, **payment simulation**, and **admin panel** with database connectivity.

---

## 👨‍💻 Team Members
- **Chella Muthu S**
- **Raja Shameer RB**
- **Santhosh P**
- **Sundareswaran S**

---

## ✨ Features
- **User Authentication** – Sign Up & Login system.
- **Bus Ticket Booking GUI** – Select route, date, time, and passenger count.
- **Database Integration** – Store users and bus details in SQL Server.
- **Dynamic Ticket Pricing** – Auto calculation based on route & passengers.
- **Payment Simulation** – Credit/Debit card and QR code options.
- **Admin Panel** – Manage users and add bus details.
- **Booking Confirmation** – Generate unique ticket ID after payment.

---

## 🛠 Tech Stack
- **Python** – Tkinter, PIL, tkcalendar
- **Database** – SQL Server (via pyodbc)
- **Other Libraries** – random, datetime

---

## 📂 Project Structure
bookingfinal.py # Main application file

qr_code.png # QR code image for payment (must be in same directory)

README.md # Project documentation


---

## ⚙️ Installation & Setup

1. **Clone the Repository**
   
2. git clone https://github.com/santhoshh-maax/bus-booking-GUI.git
   cd bus-booking-GUI


Install Dependencies

pip install pillow tkcalendar pyodbc

Set Up Database

Create a SQL Server database.

Update the connection details in bookingfinal.py inside the db_connect() function.

Run the application once to auto-create required tables.

Run the Application

python bookingfinal.py

📌 Usage

Sign Up for a new account.

Login with your credentials.

Select:

From & To location

Date & Departure Time

Number of Passengers

Confirm Booking and proceed to Payment.

Receive a unique Ticket ID after successful payment.

## This project is for educational purposes as part of a workshop challenge.
