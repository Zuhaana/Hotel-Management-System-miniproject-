import mysql.connector

def login_guest(username, password):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="hotel_db"
        )

        cursor = conn.cursor()

        query = """
        SELECT user_id, name, role
        FROM users
        WHERE username = %s AND password = %s
        """

        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        conn.close()

        if user:
            print("✅ Login successful!")
            print("User ID:", user[0])
            print("Name:", user[1])
            print("Role:", user[2])
        else:
            print("❌ Invalid username or password")

    except mysql.connector.Error as err:
        print("❌ Error:", err)


# ---- TESTING PART ----
username = input("Enter username: ")
password = input("Enter password: ")

login_guest(username, password)
