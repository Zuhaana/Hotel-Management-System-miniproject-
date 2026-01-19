import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="hotel_db"
    )

def db_add_room(number, room_type, price):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO rooms (room_number, room_type, price_per_day, available)
    VALUES (%s, %s, %s, 1)
    """

    cursor.execute(query, (number, room_type, price))
    conn.commit()
    conn.close()

def db_get_all_rooms():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT room_number, room_type, price_per_day, available
        FROM rooms
    """)

    rooms = cursor.fetchall()
    conn.close()
    return rooms


def db_get_available_rooms():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT room_number, room_type, price_per_day
        FROM rooms
        WHERE available = 1
    """)

    rooms = cursor.fetchall()
    conn.close()
    return rooms

def db_book_room(user_id, room_number, check_in, check_out, parking_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO bookings (user_id, room_number, check_in, check_out, booking_time, parking_id)
        VALUES (%s, %s, %s, %s, NOW(), %s)
    """, (user_id, room_number, check_in, check_out, parking_id))

    booking_id = cursor.lastrowid

    cursor.execute("""
        UPDATE rooms SET available = 0
        WHERE room_number = %s
    """, (room_number,))

    if parking_id:
        cursor.execute("""
            UPDATE parking_spots SET available = 0
            WHERE spot_id = %s
        """, (parking_id,))

    conn.commit()
    conn.close()

    return booking_id


def db_cancel_booking(room_number):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM bookings WHERE room_number = %s
    """, (room_number,))

    cursor.execute("""
        UPDATE rooms SET available = 1
        WHERE room_number = %s
    """, (room_number,))

    conn.commit()
    conn.close()


def db_get_guest_bookings(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT b.room_number, r.room_type, r.price_per_day,
               b.check_in, b.check_out
        FROM bookings b
        JOIN rooms r ON b.room_number = r.room_number
        WHERE b.user_id = %s
    """, (user_id,))

    bookings = cursor.fetchall()
    conn.close()
    return bookings

def db_get_food_menu():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT food_id, name, price FROM food_menu")
    menu = cursor.fetchall()

    conn.close()
    return menu


def db_add_food_order(booking_id, food_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO food_orders (booking_id, food_id, order_time)
        VALUES (%s, %s, NOW())
    """, (booking_id, food_id))

    conn.commit()
    conn.close()

def db_add_parking_spot(spot_number, price):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO parking_spots (spot_number, price_per_day, available)
        VALUES (%s, %s, 1)
    """, (spot_number, price))

    conn.commit()
    conn.close()


def db_get_available_parking():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT spot_id, spot_number, price_per_day
        FROM parking_spots
        WHERE available = 1
    """)

    spots = cursor.fetchall()
    conn.close()
    return spots


def db_mark_parking_booked(spot_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE parking_spots SET available = 0
        WHERE spot_id = %s
    """, (spot_id,))

    conn.commit()
    conn.close()


def db_mark_parking_available(spot_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE parking_spots SET available = 1
        WHERE spot_id = %s
    """, (spot_id,))

    conn.commit()
    conn.close()

def db_admin_report():
    conn = get_connection()
    cursor = conn.cursor()

    # Rooms count
    cursor.execute("SELECT COUNT(*) FROM rooms")
    total_rooms = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM rooms WHERE available = 0")
    booked_rooms = cursor.fetchone()[0]

    # Bookings count
    cursor.execute("SELECT COUNT(*) FROM bookings")
    total_bookings = cursor.fetchone()[0]

    # Room revenue
    cursor.execute("""
        SELECT IFNULL(SUM(
            DATEDIFF(check_out, check_in) * r.price_per_day
        ), 0)
        FROM bookings b
        JOIN rooms r ON b.room_number = r.room_number
    """)
    room_revenue = cursor.fetchone()[0]

    # Food revenue
    cursor.execute("""
        SELECT IFNULL(SUM(f.price), 0)
        FROM food_orders fo
        JOIN food_menu f ON fo.food_id = f.food_id
    """)
    food_revenue = cursor.fetchone()[0]

    # Parking revenue
    cursor.execute("""
        SELECT IFNULL(SUM(
            DATEDIFF(b.check_out, b.check_in) * p.price_per_day
        ), 0)
        FROM bookings b
        JOIN parking_spots p ON b.parking_id = p.spot_id
    """)
    parking_revenue = cursor.fetchone()[0]

    conn.close()

    return {
        "total_rooms": total_rooms,
        "booked_rooms": booked_rooms,
        "available_rooms": total_rooms - booked_rooms,
        "total_bookings": total_bookings,
        "room_revenue": room_revenue,
        "food_revenue": food_revenue,
        "parking_revenue": parking_revenue,
        "total_revenue": room_revenue + food_revenue + parking_revenue
    }

from datetime import date, datetime

class FoodItem:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def __str__(self):
        return f"{self.name} - ₹{self.price}"

class ParkingSpot:
    def __init__(self, spot_number, price_per_day):
        self.spot_number = spot_number
        self.price_per_day = price_per_day
        self.available = True

    def mark_booked(self):
        self.available = False

    def mark_available(self):
        self.available = True

    def __str__(self):
        status = "Available" if self.available else "Booked"
        return f"Parking Spot {self.spot_number} | ₹{self.price_per_day}/day | {status}"

class Room:
    def __init__(self, number, room_type, price):
        self.number = number
        self.room_type = room_type
        self.price = price
        self.available = True

    def mark_booked(self):
        self.available = False

    def mark_available(self):
        self.available = True

    def __str__(self):
        status = "Available" if self.available else "Booked"
        return f"Room {self.number} | {self.room_type} | ₹{self.price}/day | {status}"

class Booking:
    def __init__(self, guest, room, check_in, check_out, parking=None):
        self.guest = guest
        self.room = room
        self.check_in = check_in
        self.check_out = check_out
        self.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.food_orders = []
        self.parking = parking

    def total_days(self):
        return (self.check_out - self.check_in).days

    def total_room_cost(self):
        return self.total_days() * self.room.price

    def total_food_cost(self):
        return sum(item.price for item in self.food_orders)

    def total_parking_cost(self):
        return self.total_days() * self.parking.price_per_day if self.parking else 0

    def total_cost(self):
        return self.total_room_cost() + self.total_food_cost() + self.total_parking_cost()

    def add_food_item(self, item):
        self.food_orders.append(item)

    def __str__(self):
        food_summary = ', '.join(item.name for item in self.food_orders) if self.food_orders else 'No food ordered'
        parking_info = f"With Parking Spot {self.parking.spot_number}" if self.parking else "No parking"
        return (f"Booking for {self.guest.name} | Room {self.room.number} | {parking_info} | "
                f"{self.check_in} to {self.check_out} | Total: ₹{self.total_cost()} | Food: {food_summary}")

class User:
    def __init__(self, name, username, password):
        self.name = name
        self.username = username
        self.password = password

class Guest(User):
    def __init__(self, name, username, password):
        super().__init__(name, username, password)
        self.bookings = []

    def book_room(self, hotel, room_number, check_in, check_out, with_parking):
        room = hotel.find_room(room_number)
        if room and room.available:
            parking = None
            if with_parking:
                parking = hotel.find_available_parking()
                if not parking:
                    print("\n No parking spots available.")
                    return
                parking.mark_booked()
            booking = Booking(self, room, check_in, check_out, parking)
            room.mark_booked()
            self.bookings.append(booking)
            hotel.bookings.append(booking)
            print("\n Booking successful!")
            print(booking)
        else:
            print("\n Room not available or doesn’t exist.")

    def cancel_booking(self, hotel, room_number):
        for b in self.bookings:
            if b.room.number == room_number:
                b.room.mark_available()
                if b.parking:
                    b.parking.mark_available()
                hotel.bookings.remove(b)
                self.bookings.remove(b)
                print("\n Booking cancelled successfully.")
                return
        print("\n No booking found for that room number.")

    def view_bookings(self):
        if not self.bookings:
            print("\nNo bookings yet.")
        else:
            print(f"\n--- Bookings for {self.name} ---")
            for b in self.bookings:
                print(b)

class Admin(User):
    def __init__(self, name, username, password):
        super().__init__(name, username, password)

    def add_room(self, hotel, number, room_type, price):
        if hotel.find_room(number):
            print("\n Room already exists.")
        else:
            hotel.rooms.append(Room(number, room_type, price))
            print(f"\n Room {number} added successfully.")

    def add_parking_spot(self, hotel, spot_number, price_per_day):
        if hotel.find_parking_spot(spot_number):
            print("\n Parking spot already exists.")
        else:
            hotel.parking_spots.append(ParkingSpot(spot_number, price_per_day))
            print(f"\n Parking Spot {spot_number} added successfully.")

    def view_all_rooms(self, hotel):
        print("\n--- All Rooms ---")
        if not hotel.rooms:
            print("No rooms available.")
        else:
            for room in hotel.rooms:
                print(room)

    def view_all_bookings(self, hotel):
        print("\n--- All Bookings ---")
        if not hotel.bookings:
            print("No bookings yet.")
        else:
            for b in hotel.bookings:
                print(b)

    def view_all_parking(self, hotel):
        print("\n--- All Parking Spots ---")
        if not hotel.parking_spots:
            print("No parking spots added yet.")
        else:
            for p in hotel.parking_spots:
                print(p)

    def generate_report(self, hotel):
        total_revenue = sum(b.total_cost() for b in hotel.bookings)
        total_rooms = len(hotel.rooms)
        booked_rooms = sum(not r.available for r in hotel.rooms)
        total_parking = len(hotel.parking_spots)
        booked_parking = sum(not p.available for p in hotel.parking_spots)
        print("\n--- Hotel Report ---")
        print(f"Total Rooms: {total_rooms}")
        print(f"Booked Rooms: {booked_rooms}")
        print(f"Available Rooms: {total_rooms - booked_rooms}")
        print(f"Total Parking Spots: {total_parking}")
        print(f"Booked Parking Spots: {booked_parking}")
        print(f"Total Revenue: ₹{total_revenue}")

    def view_feedbacks(self, hotel):
        print("\n--- Guest Feedbacks ---")
        if not hotel.feedbacks:
            print("No feedbacks yet.")
        else:
            for f in hotel.feedbacks:
                print(f)

class Hotel:
    def __init__(self, name):
        self.name = name
        self.rooms = []
        self.bookings = []
        self.menu = []
        self.parking_spots = []
        self.feedbacks = [] 

    def add_food_item(self, name, price):
        self.menu.append(FoodItem(name, price))

    def show_menu(self):
        print("\n--- Food Menu ---")
        for i, item in enumerate(self.menu, start=1):
            print(f"{i}. {item}")

    def find_room(self, number):
        for room in self.rooms:
            if room.number == number:
                return room
        return None

    def show_available_rooms(self):
        print("\n--- Available Rooms ---")
        available = [r for r in self.rooms if r.available]
        if not available:
            print("No rooms available right now.")
        else:
            for room in available:
                print(room)

    def find_parking_spot(self, spot_number):
        for spot in self.parking_spots:
            if spot.spot_number == spot_number:
                return spot
        return None

    def find_available_parking(self):
        for spot in self.parking_spots:
            if spot.available:
                return spot
        return None

    def show_available_parking(self):
        print("\n--- Available Parking Spots ---")
        available = [p for p in self.parking_spots if p.available]
        if not available:
            print("No parking spots available right now.")
        else:
            for p in available:
                print(p)

    def add_feedback(self, guest_name, feedback_text):
         self.feedbacks.append(f"{guest_name}: {feedback_text}")

def db_login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT user_id, name, role
    FROM users
    WHERE username=%s AND password=%s
    """

    cursor.execute(query, (username, password))
    user = cursor.fetchone()

    conn.close()
    return user


def main():
    hotel = Hotel("Grand Palace")

    admin_user = Admin("Manager", "Zuhaana", "Zuhaana123")
    guests = []

    hotel.add_food_item("Pasta", 200)
    hotel.add_food_item("Burger", 150)
    hotel.add_food_item("Fried Rice", 180)
    hotel.add_food_item("Coffee", 80)
    hotel.add_food_item("Juice", 100)
    hotel.add_food_item("Biriyani",350)
    hotel.add_food_item("Veg Soup",220)

    while True:
        print("\n===== HOTEL MANAGEMENT SYSTEM =====")
        print("1. Admin Login")
        print("2. Guest Login / Register")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            username = input("Enter admin username: ")
            password = input("Enter admin password: ")
            if username == admin_user.username and password == admin_user.password:
                print(f"\n Welcome Admin {admin_user.name}")
                while True:
                    print("\n--- Admin Menu ---")
                    print("1. Add Room")
                    print("2. View All Rooms")
                    print("3. Add Parking Spot")
                    print("4. View All Parking Spots")
                    print("5. View All Bookings")
                    print("6. Generate Report")
                    print("7. View Guest Feedbacks")
                    print("8. Logout")
                    ch = input("Enter your choice: ")

                    if ch == '1':
                        number = int(input("Enter room number: "))
                        room_type = input("Enter room type: ")
                        price = int(input("Enter price per day: "))
                        db_add_room(number, room_type, price)
                        print(f"\n Room {number} added successfully (saved in DB).")

                    elif ch == '2':
                        print("\n--- All Rooms ---")
                        rooms = db_get_all_rooms()
                        if not rooms:
                            print("No rooms available.")
                        else:
                            for r in rooms:
                                status = "Available" if r[3] else "Booked"
                                print(f"Room {r[0]} | {r[1]} | ₹{r[2]}/day | {status}")


                    elif ch == '3':
                        spot_number = int(input("Enter parking spot ID: "))
                        price = int(input("Enter parking price per day: "))
                        admin_user.add_parking_spot(hotel, spot_number, price)

                    elif ch == '4':
                        admin_user.view_all_parking(hotel)

                    elif ch == '5':
                        admin_user.view_all_bookings(hotel)

                    elif ch == '6':
                        report = db_admin_report()

                        print("\n--- HOTEL REPORT ---")
                        print(f"Total Rooms: {report['total_rooms']}")
                        print(f"Booked Rooms: {report['booked_rooms']}")
                        print(f"Available Rooms: {report['available_rooms']}")
                        print(f"Total Bookings: {report['total_bookings']}")
                        print(f"Room Revenue: ₹{report['room_revenue']}")
                        print(f"Food Revenue: ₹{report['food_revenue']}")
                        print(f"Parking Revenue: ₹{report['parking_revenue']}")
                        print(f"TOTAL REVENUE: ₹{report['total_revenue']}")

                    elif ch == '7':
                        admin_user.view_feedbacks(hotel)

                    elif ch == '8':
                        print("\nLogged out from Admin account.")
                        break
                    else:
                        print("Invalid choice!")

            else:
                print("\n Invalid admin credentials!")

        elif choice == '2':
            print("\n1. Login")
            print("2. Register")
            sub = input("Enter your choice: ")

            if sub == '1':
                username = input("Enter username: ")
                password = input("Enter password: ")

                user = db_login_user(username, password)

                if user and user[2] == 'guest':
                    guest_id, name, role = user
                    logged_guest = Guest(name, username, password)
                    logged_guest.user_id = guest_id
                    print(f"\n Welcome, {name}")
                    guest_menu(hotel, logged_guest)
                else:
                    print("\n Invalid credentials or not a guest account.")


            elif sub == '2':
                name = input("Enter your name: ")
                username = input("Create username: ")
                password = input("Create password: ")
                guests.append(Guest(name, username, password))
                print("\n Registration successful! You can now log in.")

            else:
                print("Invalid choice!")

        elif choice == '3':
            print("\nThank you for using the system. Goodbye!")
            break

        else:
            print("Invalid choice, please try again!")

def guest_menu(hotel, guest):
    while True:
        print(f"\n--- Guest Menu ({guest.name}) ---")
        print("1. View Available Rooms")
        print("2. Book Room")
        print("3. Cancel Booking")
        print("4. View My Bookings")
        print("5. Order Food")
        print("6. Give Feedback")
        print("7. Logout")
        ch = input("Enter your choice: ")

        if ch == '1':
            print("\n--- Available Rooms ---")
            rooms = db_get_available_rooms()
            print("DEBUG rooms fetched from DB:", rooms)

            if not rooms:
                print("No rooms available right now.")
            else:
                for r in rooms:
                    print(f"Room {r[0]} | {r[1]} | ₹{r[2]}/day")

        elif ch == '2':
            print("\n--- Available Rooms ---")
            rooms = db_get_available_rooms()
            if not rooms:
                print("No rooms available right now.")
            else:
                for r in rooms:
                    print(f"Room {r[0]} | {r[1]} | ₹{r[2]}/day")

            hotel.show_available_parking()
            parking_id = None
            with_parking = input("Do you want parking? (y/n): ").lower() == 'y'

            if with_parking:
                spots = db_get_available_parking()
                if not spots:
                    print("No parking spots available.")
                else:
                    print("\nAvailable Parking:")
                    for s in spots:
                        print(f"{s[0]} - Spot {s[1]} (₹{s[2]}/day)")
                    parking_id = int(input("Enter parking ID: "))

            room_number = int(input("Enter room number to book: "))
            check_in = input("Enter check-in date (YYYY-MM-DD): ")
            check_out = input("Enter check-out date (YYYY-MM-DD): ")
            with_parking = input("Do you want parking? (y/n): ").lower() == 'y'
            try:
                check_in_date = date.fromisoformat(check_in)
                check_out_date = date.fromisoformat(check_out)
                if check_out_date <= check_in_date:
                    print("\n Check-out must be after check-in.")
                else:
                    try:
                        booking_id = db_book_room(
                            guest.user_id,
                            room_number,
                            check_in_date,
                            check_out_date,
                             parking_id
                        )

                        guest.current_booking_id = booking_id
                        print("\n Booking successful!")

                    except:
                        print("\n Room not available or booking failed.")

            except ValueError:
                print("\n Invalid date format.")

        elif ch == '3':
            room_number = int(input("Enter room number to cancel: "))
            db_cancel_booking(room_number)
            print("\n Booking cancelled successfully.")


        elif ch == '4':
            bookings = db_get_guest_bookings(guest.user_id)
            print(f"\n--- Bookings for {guest.name} ---")

            if not bookings:
                print("No bookings yet.")
            else:
                for b in bookings:
                    print(
                        f"Room {b[0]} | {b[1]} | ₹{b[2]}/day | {b[3]} to {b[4]}"
                    )

        elif ch == '5':
            menu = db_get_food_menu()

            print("\n--- Food Menu ---")
            for item in menu:
                print(f"{item[0]}. {item[1]} - ₹{item[2]}")

            if not hasattr(guest, 'current_booking_id'):
                print("\n You need an active booking to order food.")
            else:
                choice = input("Enter food ID to order (or 'done'): ")

                while choice.lower() != 'done':
                    db_add_food_order(guest.current_booking_id, int(choice))
                    print("Food item added.")
                    choice = input("Enter food ID to order (or 'done'): ")

        elif ch == '6':
            feedback_text = input("Enter your feedback: ")
            hotel.add_feedback(guest.name, feedback_text)
            print("\n Thank you for your feedback!")            

        elif ch == '7':
            print(f"\nLogged out from {guest.name}'s account.")
            break

        else:
            print("Invalid choice!")

main()

