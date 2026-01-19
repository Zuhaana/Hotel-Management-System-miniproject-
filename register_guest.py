import mysql.connector

def register_guest(name, username, password):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="hotel_db"
        )

        cursor = conn.cursor()

        query = """
        INSERT INTO users (name, username, password, role)
        VALUES (%s, %s, %s, 'guest')
        """

        cursor.execute(query, (name, username, password))
        conn.commit()

        print("✅ Guest registered successfully!")

        conn.close()

    except mysql.connector.Error as err:
        print("❌ Error:", err)


# ---- TESTING PART ----
name = input("Enter guest name: ")
username = input("Create username: ")
password = input("Create password: ")

register_guest(name, username, password)
