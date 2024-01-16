import mysql.connector
from datetime import datetime
import bcrypt

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Yagna@321",
    database="Bank"
)
cursor = db.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255) UNIQUE NOT NULL, password_hash VARCHAR(255) NOT NULL)")
cursor.execute("CREATE TABLE IF NOT EXISTS accounts (account_id INT AUTO_INCREMENT PRIMARY KEY, user_id INT, name VARCHAR(255), balance DECIMAL(10, 2) DEFAULT 0, FOREIGN KEY (user_id) REFERENCES users(user_id))")
cursor.execute("CREATE TABLE IF NOT EXISTS transactions (transaction_id INT AUTO_INCREMENT PRIMARY KEY, account_id INT, transaction_type VARCHAR(10), amount DECIMAL(10, 2), transaction_date DATETIME, FOREIGN KEY (account_id) REFERENCES accounts(account_id))")

def create_account(user_id, name):
    cursor.execute("INSERT INTO accounts (user_id, name, balance) VALUES (%s, %s, 0)", (user_id, name))
    db.commit()
    return cursor.lastrowid

def register_user(username, password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, hashed_password))
    db.commit()
    return cursor.lastrowid

def check_login(username, password):
    cursor.execute("SELECT user_id, password_hash FROM users WHERE username = %s", (username,))
    result = cursor.fetchone()
    if result:
        user_id, hashed_password = result
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
            return user_id
    return None

def is_user_logged_in():
    return user_id is not None

def deposit(account_id, amount):
    cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_id = %s", (amount, account_id))
    db.commit()
    record_transaction(account_id, "Deposit", amount)

def withdraw(account_id, amount):
    cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_id = %s", (amount, account_id))
    db.commit()
    record_transaction(account_id, "Withdrawal", amount)

def check_balance(account_id):
    cursor.execute("SELECT balance FROM accounts WHERE account_id = %s", (account_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return None

def record_transaction(account_id, transaction_type, amount):
    cursor.execute("INSERT INTO transactions (account_id, transaction_type, amount, transaction_date) VALUES (%s, %s, %s, %s)", (account_id, transaction_type, amount, datetime.now()))
    db.commit()

def transaction_history(account_id):
    cursor.execute("SELECT transaction_id, transaction_type, amount, transaction_date FROM transactions WHERE account_id = %s", (account_id,))
    result = cursor.fetchall()
    for row in result:
        print(f"Transaction ID: {row[0]}, Type: {row[1]}, Amount: {row[2]}, Date: {row[3]}")

def transfer(sender_account_id, receiver_account_id, amount):
    withdraw(sender_account_id, amount)
    deposit(receiver_account_id, amount)

# Main Program
user_id = None  # Initialize user_id outside the loop

while True:
    print("\nBank Menu:")
    print("1. Register")
    print("2. Login")
    print("3. Create Account")
    print("4. Deposit")
    print("5. Withdrawal")
    print("6. Check Balance")
    print("7. Transaction History")
    print("8. Transfer")
    print("9. Exit")

    choice = input("Enter your choice (1-9): ")

    if choice == '1':
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        register_user(username, password)
        print(f"Registration successful!")

    elif choice == '2':
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        user_id = check_login(username, password)
        if user_id is not None:
            print(f"Login successful! Welcome, {username} (User ID: {user_id})")
        else:
            print("Invalid username or password. Please try again.")

    elif choice == '3':
        if is_user_logged_in():
            name = input("Enter your name: ")
            account_id = create_account(user_id, name)
            print(f"Account created successfully! Account ID: {account_id}")
        else:
            print("Please login or register first.")

    elif choice == '4':
        if is_user_logged_in():
            account_id = input("Enter Account ID: ")
            amount = float(input("Enter Deposit Amount: "))
            deposit(int(account_id), amount)
            print("Deposit successful!")
        else:
            print("Please login or register first.")

    elif choice == '5':
        if is_user_logged_in():
            account_id = input("Enter Account ID: ")
            amount = float(input("Enter Withdrawal Amount: "))
            withdraw(int(account_id), amount)
            print("Withdrawal successful!")
        else:
            print("Please login or register first.")

    elif choice == '6':
        if is_user_logged_in():
            account_id = input("Enter Account ID: ")
            balance = check_balance(int(account_id))
            if balance is not None:
                print(f"Account Balance: {balance}")
            else:
                print("Account not found.")
        else:
            print("Please login or register first.")

    elif choice == '7':
        if is_user_logged_in():
            account_id = input("Enter Account ID: ")
            print("\nTransaction History:")
            transaction_history(int(account_id))
        else:
            print("Please login or register first.")

    elif choice == '8':
        if is_user_logged_in():
            sender_account_id = input("Enter Sender Account ID: ")
            receiver_account_id = input("Enter Receiver Account ID: ")
            amount = float(input("Enter Transfer Amount: "))
            transfer(int(sender_account_id), int(receiver_account_id), amount)
            print("Transfer successful!")
        else:
            print("Please login or register first.")

    elif choice == '9':
        print("Exiting Bank System. Goodbye!")
        break

    else:
        print("Invalid choice. Please enter a number between 1 and 9.")

db.close()
