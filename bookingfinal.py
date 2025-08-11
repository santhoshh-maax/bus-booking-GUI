import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import random
import pyodbc
from datetime import datetime

# Global variable for the main application root window
main_app_root = None

# Database connection
def db_connect():
    try:
        conn = pyodbc.connect(
            'Driver={SQL Server};'
            'Server=your server ip;'
            'Database=database name;'
            'UID=id;'
            'PWD=password'
        )
        return conn
    except Exception as e:
        messagebox.showerror("Database Connection Error", str(e))
        return None

# Create necessary tables if they don't exist
def create_tables():
    conn = db_connect()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""    
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Users' AND xtype='U')
            BEGIN
                CREATE TABLE Users (
                    ID INT PRIMARY KEY IDENTITY(1,1),
                    Name NVARCHAR(50),
                    Age INT,
                    Sex NVARCHAR(10),
                    DOB DATE,
                    Email NVARCHAR(50) NOT NULL UNIQUE,
                    Phone NVARCHAR(15),
                    Username NVARCHAR(50) NOT NULL UNIQUE,
                    Password NVARCHAR(255) NOT NULL,
                    Approved BIT DEFAULT 0
                )
            END
        """)
        # Also ensure BusDetails table exists for ticket price lookup
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='BusDetails' AND xtype='U')
            BEGIN
                CREATE TABLE BusDetails (
                    ID INT PRIMARY KEY IDENTITY(1,1),
                    [From] NVARCHAR(50),
                    [To] NVARCHAR(50),
                    TicketPrice DECIMAL(10, 2)
                )
            END
        """)
        conn.commit()
        conn.close()

# Bus ticket booking functions
districts = ["Chennai", "Coimbatore", "Madurai", "Bangalore", "Salem", "Trichy"]

def create_connection():
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=your server ip;DATABASE=your database;UID=id;PWD=password')
    return conn

def get_ticket_price(from_location, to_location):
    conn = create_connection()
    cursor = conn.cursor()
    query = "SELECT TicketPrice FROM BusDetails WHERE [From] = ? AND [To] = ?"
    cursor.execute(query, (from_location, to_location))
    price = cursor.fetchone()
    conn.close()
    return price[0] if price else None

def submit_booking(booking_window_toplevel, main_app_root_param):
    from_value = from_combobox.get()
    dest_value = dest_combobox.get()
    date_value = date_entry.get()
    depart_value = f"{time_combobox.get()} {ampm_combobox.get()}"
    num_passengers = passengers_combobox.get()

    if not all([from_value, dest_value, date_value, depart_value, num_passengers]):
        messagebox.showerror("Error", "Please fill in all fields.")
        return

    # Get ticket price from database
    ticket_price = get_ticket_price(from_value, dest_value)
    if ticket_price is None:
        messagebox.showerror("Error", "No ticket price found for this route.")
        return

    # Calculate total cost
    total_cost = ticket_price * int(num_passengers)

    booking_window_toplevel.destroy()  # Destroy the booking window

    confirmation_window(from_value, dest_value, date_value, depart_value, num_passengers, total_cost, main_app_root_param)

def confirmation_window(from_value, dest_value, date_value, depart_value, num_passengers, total_cost, main_app_root_param):
    conf_window = tk.Toplevel(main_app_root_param)
    conf_window.title("Booking Confirmation")
    conf_window.geometry("400x300")
    conf_window.configure(bg='lightblue')
    details = f"""
    Booking Confirmation
    From: {from_value}
    Destination: {dest_value}
    Date: {date_value}
    Departure: {depart_value}
    Passengers: {num_passengers}
    Total Cost: ₹{total_cost}
    """
    label = tk.Label(conf_window, text=details, font=("Open Sans", 14), bg='lightblue', padx=10, pady=10)
    label.pack(pady=20)

    # Helper function to manage the transition
    def proceed_to_payment_and_close():
        payment_page(conf_window, main_app_root_param)
        # Delay the destruction of conf_window slightly
        conf_window.after(100, conf_window.destroy) # Delay by 100 milliseconds

    payment_button = tk.Button(conf_window, text="Proceed to Payment", 
                               command=proceed_to_payment_and_close, 
                               width=20, font=("Open Sans", 12, "bold"), bg="Dark Blue", fg="White")
    payment_button.pack(pady=10)

def payment_page(conf_window_to_destroy, main_app_root_param): 
    # Destroy the confirmation window FIRST, before creating the new payment window
    # This ensures the old window is gone before the new one tries to appear.
    conf_window_to_destroy.destroy() 
    
    pay_window = tk.Toplevel(main_app_root_param) # Parent to the main app root
    pay_window.title("Payment Options")
    pay_window.geometry("400x400")
    pay_window.configure(bg='lightblue')
    payment_label = tk.Label(pay_window, text="Select Payment Method", font=("Open Sans", 16, "bold"), bg='lightblue')
    payment_label.pack(pady=20)
    card_button = tk.Button(pay_window, text="Credit/Debit Card", command=lambda: card_payment(pay_window, main_app_root_param), width=20, font=("Open Sans", 12, "bold"), bg="Dark Blue", fg="White")
    card_button.pack(pady=10)
    qr_button = tk.Button(pay_window, text="QR Code Payment", command=lambda: qr_payment(pay_window, main_app_root_param), width=20, font=("Open Sans", 12, "bold"), bg="Dark Blue", fg="White")
    qr_button.pack(pady=10)
    # Explicitly bring the new payment window to the front
    pay_window.lift()
    pay_window.attributes('-topmost', True) # Make it topmost temporarily
    pay_window.after_idle(pay_window.attributes, '-topmost', False) # Remove topmost after it's displayed

def card_payment(pay_window, main_app_root_param):
    pay_window.destroy()  # Close the payment window
    
    card_window = tk.Toplevel(main_app_root_param) # Parent to the main app root
    card_window.title("Credit/Debit Card Payment")
    card_window.geometry("400x300")
    card_window.configure(bg='lightblue')

    card_label = tk.Label(card_window, text="Card Number:", bg='lightblue', font=("Open Sans", 12))
    card_label.pack(pady=10)
    card_entry = tk.Entry(card_window, width=30)
    card_entry.pack(pady=5)

    cvv_label = tk.Label(card_window, text="CVV:", bg='lightblue', font=("Open Sans", 12))
    cvv_label.pack(pady=10)
    cvv_entry = tk.Entry(card_window, width=5, show="*") # Added show="*" for CVV
    cvv_entry.pack(pady=5)

    done_button = tk.Button(card_window, text="Done", command=lambda: generate_ticket(card_window, main_app_root_param), width=15, font=("Open Sans", 12, "bold"), bg="Dark Blue", fg="White")
    done_button.pack(pady=20)

def qr_payment(pay_window, main_app_root_param):
    pay_window.destroy()  # Close the payment window
    
    qr_window = tk.Toplevel(main_app_root_param) # Parent to the main app root
    qr_window.title("QR Code Payment")
    qr_window.geometry("400x300")
    qr_window.configure(bg='lightblue')

    qr_label = tk.Label(qr_window, text="Scan the QR Code:", bg='lightblue', font=("Open Sans", 14))
    qr_label.pack(pady=20)

    # Placeholder for QR Code image
    try:
        qr_image = Image.open('qr_code.png')  # Make sure the image file exists and is named qr_code.png
        qr_image = qr_image.resize((150, 150))
        qr_photo = ImageTk.PhotoImage(qr_image)
        qr_label_image = tk.Label(qr_window, image=qr_photo, bg='lightblue')
        qr_label_image.image = qr_photo  # Keep a reference
        qr_label_image.pack(pady=10)
    except FileNotFoundError:
        messagebox.showerror("Error", "QR code image 'qr_code.png' not found. Please place it in the same directory.")
        qr_label_image = tk.Label(qr_window, text="QR Code Image Missing", bg='lightblue', font=("Open Sans", 12))
        qr_label_image.pack(pady=10)


    done_button = tk.Button(qr_window, text="Done", command=lambda: generate_ticket(qr_window, main_app_root_param), width=15, font=("Open Sans", 12, "bold"), bg="Dark Blue", fg="White")
    done_button.pack(pady=20)

def generate_ticket(window_to_destroy, main_app_root_param):
    window_to_destroy.destroy() # Close the payment method window
    ticket_id = random.randint(100000, 999999)  # Generate a 6-digit ticket ID
    ticket_window = tk.Toplevel(main_app_root_param) # Parent to the main app root
    ticket_window.title("Payment Confirmation")
    ticket_window.geometry("400x200")
    ticket_window.configure(bg='lightblue')

    ticket_label = tk.Label(ticket_window, text=f"Payment Successful!\nYour Ticket ID: {ticket_id}", font=("Open Sans", 14), bg='lightblue')
    ticket_label.pack(pady=20)

    close_button = tk.Button(ticket_window, text="Close", command=ticket_window.destroy, width=15, font=("Open Sans", 12, "bold"), bg="Dark Blue", fg="White")
    close_button.pack(pady=10)

# User Authentication Functions
def open_login():
    global entry_username, entry_password
    login_window = tk.Toplevel(main_app_root) # Parent to the main app root
    login_window.title("Login")
    login_window.geometry("400x300")
    login_window.configure(bg='lightblue')

    tk.Label(login_window, text="Login", bg='lightblue', font=("Open Sans", 20, "bold")).pack(pady=10)

    tk.Label(login_window, text="Username", bg='lightblue').pack(pady=5)
    entry_username = tk.Entry(login_window)
    entry_username.pack(pady=5)

    tk.Label(login_window, text="Password", bg='lightblue').pack(pady=5)
    entry_password = tk.Entry(login_window, show="*")
    entry_password.pack(pady=5)

    tk.Button(login_window, text="Login", command=lambda: user_login(login_window)).pack(pady=20)

def user_login(login_window_toplevel):
    username = entry_username.get()
    password = entry_password.get()

    if username == "admin" and password == "admin123":  # Check for admin credentials
        login_window_toplevel.destroy() # Close login window
        open_admin_panel()
        return

    conn = db_connect()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE Username = ? AND Password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            messagebox.showinfo("Login Successful", f"Welcome, {user[1]}!")
            login_window_toplevel.destroy() # Close login window
            open_booking_window(main_app_root) # Pass the main app root
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

def open_signup():
    signup_window = tk.Toplevel(main_app_root) # Parent to the main app root
    signup_window.title("Sign Up")
    signup_window.geometry("400x500")
    signup_window.configure(bg='lightblue')

    tk.Label(signup_window, text="Sign Up", bg='lightblue', font=("Open Sans", 20, "bold")).pack(pady=10)

    tk.Label(signup_window, text="Name", bg='lightblue').pack(pady=5)
    entry_name = tk.Entry(signup_window)
    entry_name.pack(pady=5)

    tk.Label(signup_window, text="Age", bg='lightblue').pack(pady=5)
    entry_age = tk.Entry(signup_window)
    entry_age.pack(pady=5)

    tk.Label(signup_window, text="Sex", bg='lightblue').pack(pady=5)
    entry_sex = tk.Entry(signup_window)
    entry_sex.pack(pady=5)

    tk.Label(signup_window, text="Date of Birth", bg='lightblue').pack(pady=5)
    dob_entry = DateEntry(signup_window, width=12, background='darkblue', foreground='white', borderwidth=2)
    dob_entry.pack(pady=5)

    tk.Label(signup_window, text="Email", bg='lightblue').pack(pady=5)
    entry_email = tk.Entry(signup_window)
    entry_email.pack(pady=5)

    tk.Label(signup_window, text="Phone", bg='lightblue').pack(pady=5)
    entry_phone = tk.Entry(signup_window)
    entry_phone.pack(pady=5)

    tk.Label(signup_window, text="Username", bg='lightblue').pack(pady=5)
    entry_username = tk.Entry(signup_window)
    entry_username.pack(pady=5)

    tk.Label(signup_window, text="Password", bg='lightblue').pack(pady=5)
    entry_password = tk.Entry(signup_window, show="*")
    entry_password.pack(pady=5)

    tk.Button(signup_window, text="Sign Up", command=lambda: submit_signup(signup_window, entry_name.get(), entry_age.get(), entry_sex.get(), dob_entry.get(), entry_email.get(), entry_phone.get(), entry_username.get(), entry_password.get())).pack(pady=20)

def submit_signup(signup_window_toplevel, name, age, sex, dob, email, phone, username, password):
    conn = db_connect()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO Users (Name, Age, Sex, DOB, Email, Phone, Username, Password) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                           (name, age, sex, dob, email, phone, username, password))
            conn.commit()
            messagebox.showinfo("Success", "Registration successful! You can now log in.")
            signup_window_toplevel.destroy() # Close signup window after successful registration
        except Exception as e:
            messagebox.showerror("Registration Error", str(e))
        finally:
            conn.close()

# Admin Functions
def open_admin_panel():
    admin_window = tk.Toplevel(main_app_root) # Parent to the main app root
    admin_window.title("Admin Panel")
    admin_window.geometry("400x400")
    admin_window.configure(bg='lightblue')

    tk.Label(admin_window, text="Admin Panel", bg='lightblue', font=("Open Sans", 20, "bold")).pack(pady=10)

    view_users_button = tk.Button(admin_window, text="View Users", command=view_users, width=20)
    view_users_button.pack(pady=10)

    add_bus_button = tk.Button(admin_window, text="Add Bus Details", command=add_bus_details, width=20)
    add_bus_button.pack(pady=10)

def view_users():
    users_window = tk.Toplevel(main_app_root) # Parent to the main app root
    users_window.title("User List")
    users_window.geometry("700x400") # Increased width to better display columns

    tree = ttk.Treeview(users_window, columns=("Name", "Age", "Sex", "Email", "Phone", "Username", "Approved"), show='headings')
    tree.heading("Name", text="Name")
    tree.heading("Age", text="Age")
    tree.heading("Sex", text="Sex")
    tree.heading("Email", text="Email")
    tree.heading("Phone", text="Phone")
    tree.heading("Username", text="Username")
    tree.heading("Approved", text="Approved")

    # Set column widths
    tree.column("Name", width=100)
    tree.column("Age", width=50)
    tree.column("Sex", width=50)
    tree.column("Email", width=150)
    tree.column("Phone", width=100)
    tree.column("Username", width=100)
    tree.column("Approved", width=80)


    conn = db_connect()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT Name, Age, Sex, Email, Phone, Username, Approved FROM Users") # Select specific columns
        for row in cursor.fetchall():
            tree.insert("", "end", values=row)
        conn.close()

    tree.pack(expand=True, fill='both')

def add_bus_details():
    add_bus_window = tk.Toplevel(main_app_root) # Parent to the main app root
    add_bus_window.title("Add Bus Details")
    add_bus_window.geometry("400x400")
    add_bus_window.configure(bg='lightblue')

    tk.Label(add_bus_window, text="Bus Details", bg='lightblue', font=("Open Sans", 20, "bold")).pack(pady=10)

    tk.Label(add_bus_window, text="From", bg='lightblue').pack(pady=5)
    entry_from = tk.Entry(add_bus_window)
    entry_from.pack(pady=5)

    tk.Label(add_bus_window, text="To", bg='lightblue').pack(pady=5)
    entry_to = tk.Entry(add_bus_window)
    entry_to.pack(pady=5)

    tk.Label(add_bus_window, text="Ticket Price", bg='lightblue').pack(pady=5)
    entry_price = tk.Entry(add_bus_window)
    entry_price.pack(pady=5)

    tk.Button(add_bus_window, text="Add Bus", command=lambda: insert_bus_details(add_bus_window, entry_from.get(), entry_to.get(), entry_price.get())).pack(pady=20)

def insert_bus_details(add_bus_window_toplevel, from_location, to_location, ticket_price):
    conn = db_connect()
    if conn:
        cursor = conn.cursor()
        try:
            # Validate ticket_price is a number
            try:
                price = float(ticket_price)
            except ValueError:
                messagebox.showerror("Error", "Ticket Price must be a number.")
                return

            cursor.execute("INSERT INTO BusDetails ([From], [To], TicketPrice) VALUES (?, ?, ?)", (from_location, to_location, price))
            conn.commit()
            messagebox.showinfo("Success", "Bus details added successfully!")
            add_bus_window_toplevel.destroy() # Close window after adding
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()

# Main application
def main():
    global main_app_root
    create_tables()
    main_app_root = tk.Tk()
    main_app_root.title("Bus Booking System")
    main_app_root.geometry("400x400")
    main_app_root.configure(bg='lightblue')

    tk.Label(main_app_root, text="Welcome to Bus Booking System", bg='lightblue', font=("Open Sans", 20, "bold")).pack(pady=20)

    login_button = tk.Button(main_app_root, text="Login", command=open_login, width=20)
    login_button.pack(pady=10)

    signup_button = tk.Button(main_app_root, text="Sign Up", command=open_signup, width=20)
    signup_button.pack(pady=10)

    main_app_root.mainloop()

# Booking Window
def open_booking_window(main_app_root_param):
    booking_window = tk.Toplevel(main_app_root_param) # Parent to the main app root
    booking_window.title("Bus Booking")
    booking_window.geometry("500x500")
    booking_window.configure(bg='lightblue')

    tk.Label(booking_window, text="Book Your Ticket", bg='lightblue', font=("Open Sans", 20, "bold")).pack(pady=10)

    tk.Label(booking_window, text="From", bg='lightblue').pack(pady=5)
    global from_combobox
    from_combobox = ttk.Combobox(booking_window, values=districts, state="readonly") # Added readonly state
    from_combobox.pack(pady=5)

    tk.Label(booking_window, text="To", bg='lightblue').pack(pady=5)
    global dest_combobox
    dest_combobox = ttk.Combobox(booking_window, values=districts, state="readonly") # Added readonly state
    dest_combobox.pack(pady=5)

    tk.Label(booking_window, text="Date", bg='lightblue').pack(pady=5)
    global date_entry
    date_entry = DateEntry(booking_window, width=12, background='darkblue', foreground='white', borderwidth=2)
    date_entry.pack(pady=5)

    tk.Label(booking_window, text="Departure Time", bg='lightblue').pack(pady=5)
    global time_combobox
    time_combobox = ttk.Combobox(booking_window, values=["12:00", "1:00", "2:00", "3:00", "4:00", "5:00", "6:00", "7:00", "8:00", "9:00", "10:00", "11:00"], state="readonly") # Added readonly state
    time_combobox.pack(pady=5)

    global ampm_combobox
    ampm_combobox = ttk.Combobox(booking_window, values=["AM", "PM"], state="readonly") # Added readonly state
    ampm_combobox.pack(pady=5)

    tk.Label(booking_window, text="Number of Passengers", bg='lightblue').pack(pady=5)
    global passengers_combobox
    passengers_combobox = ttk.Combobox(booking_window, values=["1", "2", "3", "4", "5"], state="readonly") # Added readonly state
    passengers_combobox.pack(pady=5)

    book_button = tk.Button(booking_window, text="Book Now", command=lambda: submit_booking(booking_window, main_app_root_param), width=20)
    book_button.pack(pady=20)

# Run the application
if __name__ == "__main__":
    main()
