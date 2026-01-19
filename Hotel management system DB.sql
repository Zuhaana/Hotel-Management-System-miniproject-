CREATE DATABASE hotel_db;
USE hotel_db;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    username VARCHAR(50) UNIQUE,
    password VARCHAR(50),
    role ENUM('admin','guest')
);

DESCRIBE users;
INSERT INTO users (name, username, password, role) VALUES ('Manager', 'admin', 'admin123', 'admin');
SELECT * FROM users;

CREATE TABLE IF NOT EXISTS rooms (
    room_id INT AUTO_INCREMENT PRIMARY KEY,
    room_number INT UNIQUE,
    room_type VARCHAR(30),
    price_per_day INT,
    available BOOLEAN
);

DESCRIBE rooms;
select * from rooms;
SELECT room_number, room_type, price_per_day, available FROM rooms;
SELECT * FROM rooms WHERE available = 1;


CREATE TABLE IF NOT EXISTS bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    room_number INT,
    check_in DATE,
    check_out DATE,
    booking_time DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (room_number) REFERENCES rooms(room_number)
);

DESCRIBE bookings;

CREATE TABLE IF NOT EXISTS food_menu (
    food_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    price INT
);

INSERT INTO food_menu (name, price) VALUES ('Pasta', 200),('Burger', 150),('Fried Rice', 180),('Coffee', 80),('Juice', 100),('Biriyani', 350),('Veg Soup', 220);
SELECT * FROM food_menu;

CREATE TABLE IF NOT EXISTS food_orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT,
    food_id INT,
    order_time DATETIME,
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id),
    FOREIGN KEY (food_id) REFERENCES food_menu(food_id)
);

CREATE TABLE IF NOT EXISTS parking_spots (
    spot_id INT AUTO_INCREMENT PRIMARY KEY,
    spot_number INT UNIQUE,
    price_per_day INT,
    available BOOLEAN
);

ALTER TABLE bookings
ADD COLUMN parking_id INT NULL,
ADD FOREIGN KEY (parking_id) REFERENCES parking_spots(spot_id);











