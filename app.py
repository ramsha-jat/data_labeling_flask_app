from bson import ObjectId
from flask import g
from flask import Flask, render_template, request, redirect, url_for
from flask_login import login_required, current_user, login_user, logout_user, LoginManager, UserMixin, \
    user_loaded_from_request
from pymongo import MongoClient
import pandas as pd

# Connect to MongoDB
client = MongoClient("mongodb+srv://ramshabscsf19:sMzCIIY97F52CflR@cluster0.1txdpcy.mongodb.net/",1687)
db = client["rimsha"]
users = db["users"]
data = db["data"]
app = Flask(__name__)
app.secret_key = "qwertyuiopasdfghjklzxcvbnm"

login_manager = LoginManager()
login_manager.init_app(app)


# Create a User model
class User(UserMixin):
    def __init__(self, id, name, email, password):
        self.id = id
        self.name = name
        self.email = email
        self.password = password


# Login route
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        print(email)
        print(password)

        # Get the user from the database
        user = users.find_one({"email": email})

        # Check if the user exists and the password is correct
        if user and user["password"] == password:
            # Log the user in
            login_user(User(user["_id"], user['name'], user['email'], user['password']), remember=True)

            # Redirect the user to the home page
            return redirect("/home")

        # If the user does not exist or the password is incorrect, show an error message
        return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")


@app.route("/logup", methods=["GET", "POST"])
def logup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        # Check if the user exists
        users_count = users.count_documents({"email": email})
        if users_count > 0:
            return render_template("logup.html", error="The email already exists")

        # Create a new user
        user = {
            "name": name,
            "email": email,
            "password": password
        }

        # Save the user to the database
        users.insert_one(user)

        # Log the user in
        user_login = User(user["_id"], user["name"])

        login_user(user_login, remember=True)

        # Redirect the user to the home page
        return redirect("/home")
    else:
        return render_template("logup.html")


@app.route("/home", methods=["GET", "POST"])
@login_required
def dashboard():
    if request.method == "POST":
        input_type = request.form.get("type")
        input_sentiment = request.form.get("sentiment")
        print(input_type)
        print(input_sentiment)

    # total number of records in the dataset 'data'
    total_records = data.count_documents({})

    # CommandCursor object
    random_record = data.aggregate([{"$sample": {"size": 1}}])
    random_record = random_record.next()
    print(random_record)
    return render_template("index.html", total_records=total_records, name=current_user.name, email=current_user.email,
                           record=random_record)


@app.route("/save", methods=["POST"])
@login_required
def save():
    id = request.form.get("id")
    text = request.form.get("text")
    input_type = request.form.get("type")
    input_sentiment = request.form.get("sentiment")
    user_name: str = current_user.name
    user_name = user_name.lower().replace(" ", "_")
    # create a new collection for each user
    user_collection = db[user_name]
    # insert the record into the user's collection
    user_collection.insert_one({
        "_id": ObjectId(id),
        "text": text,
        "type": input_type,
        "sentiment": input_sentiment
    })
    # delete the record from the main collection
    data.delete_one({"_id": ObjectId(id)})

    # redirect to the dashboard
    return redirect("/home")


@user_loaded_from_request.connect
def user_loaded_from_request(self, user=None):
    g.login_via_request = True


# User loader
@login_manager.user_loader
def load_user(user_id):
    # user_id converted from string to ObjectId
    user_id = ObjectId(user_id)
    user = users.find_one({"_id": user_id})

    print(user_id, "user_id")
    print(user, "user")

    if not user:
        return None
    return User(user['_id'], user["name"], user['email'], user["password"])


# logout route
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
