# Mpendulo Khoza
# Group 2

import hmac
import sqlite3

from flask import Flask, request, jsonify
from flask_jwt import *
from flask_cors import CORS
from flask_mail import Mail, Message


class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password
def fetch_users():
    with sqlite3.connect('dealership.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        customers = cursor.fetchall()

        new_data = []

        for data in customers:
            # print(data)
            new_data.append(User(data[0], data[5], data[4]))
    return new_data


users = fetch_users()
username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}

def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


class Items(object):
    def __init__(self, product_id, name, price, description, product_type):
        self.id = product_id
        self.name = name
        self.price = price
        self.description = description
        self.type = product_type


def init_users_table():
    conn = sqlite3.connect('dealership.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "firstname TEXT NOT NULL,"
                 "lastname TEXT NOT NULL,"
                 "contact INT NOT NULL,"
                 "password TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "email TEXT NOT NULL)")
    print("user table created successfully")
    conn.close()



def init_vehicle_dealership_table():
    with sqlite3.connect("dealership.db") as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS Car_dealership (id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "name TEXT NOT NULL,"
                     "brand INTEGER NOT NULL,"
                     "price TXT NOT NULL,"
                     "type INT NOT NULL,"
                     "year INTEGER NOT NULL,"
                     "logo TXT NOT NULL,"
                     "image_url TXT NOT NULL)")
        print("products table created successfully")


def fetch_products():
    with sqlite3.connect("dealership.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Car_dealership")
        items = cursor.fetchall()

        new_item = []

        for data in items:
            # print(data)
            new_item.append(Items(data[0], data[1], data[2], data[3], data[4]))
        return new_item


init_users_table()
init_vehicle_dealership_table()

products = fetch_products()


vehicle_table = {p.name: p for p in products}
vehicle_id_table = {p.id: p for p in products}


app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'mpendulokhozamk2@gmail.com'
app.config['MAIL_PASSWORD'] = 'LloydSibanda11'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
CORS(app)
jwt = JWT(app, authenticate, identity)

@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity


@app.route('/user-registration', methods=["POST"])
def user_registration():
    response = {}

    if request.method == "POST":

        first_name = request.form['firstname']
        last_name = request.form['lastname']
        address = request.form['contact']
        email = request.form['username']
        username = request.form['password']
        password = request.form['email']

        with sqlite3.connect('dealership.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users("
                           "firstname,"
                           "lastname,"
                           "contact,"
                           "username,"
                           "password,"
                           "email) VALUES(?, ?, ?, ?, ?, ?)",
                           (first_name, last_name, address, email, username, password))
            conn.commit()
            response["message"] = "Registration updated  Successfully "
            response["status_code"] = 200
            mail = Mail(app)
            message = Message('Message', sender='mpendulokhozamk2@gmail.com', recipients=['mpendulokhozamk2@gmail.com'])
            message.body = "Registration Successful"
            mail.send(message)
        return response


@app.route('/user-profile/<int:user_id>')
def view_profile(user_id):
    response = {}

    with sqlite3.connect("dealership.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id=" + str(user_id))

        response["status_code"] = 200
        response["description"] = "Profile fetched Successfully"
        response["data"] = cursor.fetchone()

    return jsonify(response)


@app.route('/create-dealership', methods=["POST"])
def create_dealership():
    response = {}

    if request.method == "POST":
        name = request.form['name']
        brand = request.form['brand']
        price = request.form['price']
        car_type = request.form['type']
        year = request.form['year']
        logo = request.form['logo_url']
        image = request.form['image_url']

        with sqlite3.connect("dealership.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Car_dealership("
                           "name,"
                           "brand,"
                           "price,"
                           "type,"
                           "year,"
                           "logo,"
                           "image_url) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (name, brand, price, car_type, year, logo, image))
            conn.commit()
            response["status_code"] = 201
            response["description"] = "Vehicle created successfully"
        return response


@app.route('/show-Vehicle')
def show_vehicle():
    response = {}

    with sqlite3.connect("dealership.db") as conn:
        cursor = conn.cursor()
        cursor.row_factory = sqlite3.Row
        cursor.execute("SELECT * FROM Car_dealership")
        deals = cursor.fetchall()
        deal_acc = []

        for i in deals:
            deal_acc.append({x: i[x] for x in i.keys()})
        response["status_code"] = 200
        response["data"] = tuple(deal_acc)
        response["description"] = "Displaying Vehicles Successfully"
    return jsonify(response)


@app.route('/delete-car/<int:vehicle_id>')
def remove_vehicle(vehicle_id):
    response = {}
    with sqlite3.connect("dealership.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Car_dealership WHERE id=" + str(vehicle_id))
        conn.commit()
        response['status_code'] = 200
        response['message'] = "Vehicle deleted Successfully"

    return response


@app.route('/edit-car/<int:vehicle_id>/', methods=["PUT"])
def edit_car(vehicle_id):
    response = {}
    if request.method == "PUT":
        with sqlite3.connect("dealership.db") as conn:
            incoming_data = dict(request.json)

            put_data = {}
            if incoming_data.get("name") is not None:
                put_data["name"] = incoming_data.get("name")
                with sqlite3.connect("dealership.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE Car_dealership SET name=? WHERE id=?", (put_data["name"], vehicle_id))
                    conn.commit()
                    response['message'] = "Updating successful"
                    response['status_code'] = 200
                return response

            if incoming_data.get("brand") is not None:
                put_data["brand"] = incoming_data.get("brand")
                with sqlite3.connect("dealership.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE Car_dealership SET brand=? WHERE id=?", (put_data["brand"], vehicle_id))
                    conn.commit()
                    response['message'] = "Updating  successfully"
                    response['status_code'] = 200

            if incoming_data.get('year') is not None:
                put_data['year'] = incoming_data.get('year')
                with sqlite3.connect('dealership.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute('UPDATE Car_dealership SET year=? WHERE id=?', (put_data['year'], vehicle_id))
                    conn.commit()
                    response['message'] = "Updating Successfully"
                return response


if __name__ == '__main__':
    app.run(debug=True)
