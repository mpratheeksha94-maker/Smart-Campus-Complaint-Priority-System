from database import get_db_connection
from werkzeug.security import generate_password_hash

name = input("Enter admin name: ")
email = input("Enter admin email: ")
password = input("Enter admin password: ")

hashed_password = generate_password_hash(password)

connection = get_db_connection()
cursor = connection.cursor()

query = """
INSERT INTO users (name, email, password, role)
VALUES (%s, %s, %s, 'admin')
"""

cursor.execute(query, (name, email, hashed_password))

connection.commit()

cursor.close()
connection.close()

print("Admin account created successfully!")