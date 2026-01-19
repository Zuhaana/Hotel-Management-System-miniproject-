import mysql.connector

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="hotel_db"
    )

    print("✅ Connected successfully")

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")

    rows = cursor.fetchall()
    for row in rows:
        print(row)

    conn.close()

except mysql.connector.Error as err:
    print("❌ Error:", err)
