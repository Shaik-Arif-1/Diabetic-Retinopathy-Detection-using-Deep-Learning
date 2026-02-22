from flask import Flask,render_template,redirect,request,url_for, send_file, session, Response, jsonify
import mysql.connector, joblib, random, string, base64, pickle
import pandas as pd
import numpy as np
import os
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'diabetic' 

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    port="3307",
    database='diabetic'
)

mycursor = mydb.cursor()

def executionquery(query,values):
    mycursor.execute(query,values)
    mydb.commit()
    return

def retrivequery1(query,values):
    mycursor.execute(query,values)
    data = mycursor.fetchall()
    return data

def retrivequery2(query):
    mycursor.execute(query)
    data = mycursor.fetchall()
    return data


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        c_password = request.form['c_password']

        if password == c_password:
            query = "SELECT email FROM users"
            email_data = retrivequery2(query)
            email_data_list = []
            for i in email_data:
                email_data_list.append(i[0])

            if email not in email_data_list:
                query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
                values = (name, email, password)
                executionquery(query, values)

                return render_template('login.html', message="Successfully Registered!")
            return render_template('register.html', message="This email ID is already exists!")
        return render_template('register.html', message="Conform password is not match!")
    return render_template('register.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        
        query = "SELECT email FROM users"
        email_data = retrivequery2(query)
        email_data_list = []
        for i in email_data:
            email_data_list.append(i[0])

        if email in email_data_list:
            query = "SELECT * FROM users WHERE email = %s"
            values = (email,)
            password__data = retrivequery1(query, values)

            if password == password__data[0][3]:
                session["user_id"] = password__data[0][0]
                session["user_email"] = email
                session["user_name"] = password__data[0][1]

                return redirect("/home")
            return render_template('login.html', message= "Invalid Password!!")
        return render_template('login.html', message= "This email ID does not exist!")
    return render_template('login.html')


@app.route('/home')
def home():
    return render_template('home.html')




@app.route('/prediction', methods = ["GET", "POST"])
def prediction():
    if request.method == "POST":
        myfile = request.files["img"]
        fn = myfile.filename
        mypath = os.path.join('static/images/saved_images', fn)
        myfile.save(mypath)

        # Classes for prediction
        Classes = ['Mild', 'Moderate', 'No_DR', 'Proliferate_DR', 'Severe']

        # Load model
        model = load_model(r'Models\Mobilenet.h5', compile=False)

        # Image Preprocessing
        x1 = image.load_img(mypath, target_size=(256, 256))
        x1 = image.img_to_array(x1)
        x1 = np.expand_dims(x1, axis=0)
        x1 /= 255

        # Prediction
        result = model.predict(x1)
        b = np.argmax(result)
        prediction = Classes[b]

        # Get user details and timestamp
        user_name = session["user_name"]
        user_email = session["user_email"]
        date = datetime.today().date()
        time = datetime.now().time()

        # SQL Insert Query
        query = "INSERT INTO predictions (user_name, user_email, image, prediction, date, time) VALUES (%s, %s, %s, %s, %s, %s)"
        values = (user_name, user_email, mypath, prediction, date, time)
        executionquery(query, values)
    
        return render_template('prediction.html', result=prediction, path=mypath)
    return render_template('prediction.html')



@app.route('/history')
def history():
    query = "SELECT * FROM predictions WHERE user_email = %s"
    values = (session["user_email"],)
    data = retrivequery1(query, values)
    return render_template('history.html', data = data)




if __name__ == '__main__':
    app.run(debug = True)