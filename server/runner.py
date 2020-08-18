from flask import render_template, request, redirect, url_for, session, escape, Flask, jsonify
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bson import regex, ObjectId
from random import randint
import json
import pathlib
import hashlib
import requests
import random
import os
from datetime import datetime
from flask_pymongo import PyMongo
import re
import smtplib
import math
import smtplib
from werkzeug.utils import secure_filename
from fastai.vision import *
# import cv2
import numpy as np
import base64
from PIL import Image
from io import BytesIO
from math import radians, cos, sin, asin, sqrt
import herepy
import ast
from os.path import join, dirname, realpath


port = 5000
# host = "192.168.43.95"
host = "0.0.0.0"

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb+srv://ramsuthar305:mitsor@cluster0.4ol8l.mongodb.net/mitsor?retryWrites=true&w=majority"

mongo = PyMongo(app)

app.config['uploads'] = join(dirname(realpath(__file__)), "uploads")
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = '5234124584324'

headers = {'Authorization': 'Basic cm9vdDo2NjIyNDQ2Ng==',
           'Content-Type': 'application/json'}


UPLOAD_FOLDER = "../static/uploads/"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


@app.route('/api/register', methods=['POST'])
def api_register():
    if request.method == 'POST':
        data = request.get_data()
        data = json.loads(data)
        user_email = data["user_email"]
        check_if_exist = mongo.db.grievance_users.find_one(
            {"user_email": user_email})
        if check_if_exist:
            return jsonify({"status": 'failed', "message": "User already exist!"})
        else:
            result = mongo.db.grievance_users.insert_one(data)
            return jsonify({"status": 'success', "message": "registered successfully!"})


@app.route('/api/login', methods=['POST'])
def api_login():
    if request.method == 'POST':
        if 'logged_in' in session:
            return jsonify({"status": 'user is already logged.'})
        else:
            data = request.get_data()
            data = json.loads(data)
            user_name = data['user_email']
            user_password = data['user_password']
            loginuser = mongo.db.grievance_users.find_one({"$and": [{"$or": [{"user_email": user_name}, {
                "user_phone": user_name}]}, {"user_password": user_password}]})
            if loginuser['user_type'] == 'general':
                del loginuser["user_password"]
                del loginuser["_id"]
                session['username'] = loginuser["user_email"]
                session['logged_in'] = True
                return jsonify({"data": loginuser, "status": "user logged in succesffully"})
            elif loginuser['user_type'] == 'admin':
                return jsonify({"status": 'failed', "message": "Restricted login"})
            else:
                return jsonify({"status": 'failed', "message": "invalid Credential!"})


@app.route('/api/logout', methods=['GET'])
def api_logout():
    del session['logged_in']
    del session['username']
    return jsonify({"status": "user logged out in succesffully"})


@app.route("/login", methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            loginuser = mongo.db.grievance_users.find_one({"$and": [{"$or": [{"user_email": username}, {
                "user_phone": username}]}, {"user_password": password}]})
            
            if loginuser['user_type'] == 'admin':
                print('\n\ntrue:')
                session['admin_area'] = loginuser['user_area']
                session['admin_login'] = True
                grievance_all = list(mongo.db.grievance.find(
                    {'assigned_authority': loginuser['user_area']}))
                return redirect('/index')
            else:
                CONTEXT_msg = 'Entered Username and password do not match. Please Retry!'
                return render_template("loginpage.html", CONTEXT_msg=CONTEXT_msg)
        except Exception as e:
            print(e)
            return render_template('loginpage.html')
        grievance_all = list(mongo.db.grievance.find(
            {'assigned_authority': session['admin_area']}))
        return render_template('problems.html', all=[grievance_all, session['admin_area']])
    else:
        CONTEXT_msg = ''
        return render_template("loginpage.html", CONTEXT_msg=CONTEXT_msg)


@app.route('/logout')
def logout():
    del session['logged_in']
    del session['username']
    return redirect('/login')


@app.route('/upload')
def upload():
    return render_template('add.html')


@app.route('/hello/<send_mail>', methods=['GET', 'POST'])
def predict(send_mail="no"):
    send_mail_to = None
    grievance_all = list(mongo.db.grievance.find({"grievance_type": "unpredicted"}))

    for i in grievance_all:
        if 'grievance_type' not in i or i['grievance_type'] == "unpredicted":
            filename = str(i['grievance_id'][:5])

            pathh = i['image_link']
            
            path = Path('')
            
            classes = ['garbage', 'pothole', 'sewage']
            
            data = ImageDataBunch.single_from_classes(path, classes, ds_tfms=get_transforms(), size=240).normalize(imagenet_stats)
            
            learn = cnn_learner(data, models.resnet101, metrics=error_rate)
            
            learn.load('phase1')
            
            img = open_image(pathh)
            pred_class, pred_idx, outputs = learn.predict(img)
            print(str(pred_class))
            
            if(str(pred_class) == "sewage"):
                send_mail_to = "kunjshah45@gmail.com"
            if(str(pred_class) == "garbage"):
                send_mail_to = "kunjshah46@gmail.com"
            if(str(pred_class) == "pothole"):
                send_mail_to = "ramsuthar305@gmail.com"
            all1 = mongo.db.grievance.find_one_and_update({'grievance_id': i["grievance_id"]}, {
                '$set': {"grievance_type": str(pred_class)}})

            if send_mail == "yes":

                sendMail(send_mail_to, "New Grievance Received",
                         "Your department has received a grievance. Please check your portel for details.")
            return "smd"


def distance(lat1, lat2, lon1, lon2):
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2

    c = 2 * asin(sqrt(a))

    r = 6371

    return(c * r)

@app.route('/api/history/<email>', methods=['GET'])
def history(email):
    grievance_all = list(mongo.db.grievance.find({"user_id": email}))

    for i in grievance_all:
        if 'area' not in i or i['area'] == "unpredicted":
            longitude = float(i['longitude'])
            latitude = float(i['latitude'])
            res = getLocationDetails(latitude, longitude)
            update_location = mongo.db.grievance.find_one_and_update(
                {'grievance_id': i["grievance_id"]}, {'$set': {"area": res}})
        del i["_id"]
        i["id"] = i["grievance_id"]

        i["image_link"] = "http://"+ host+":5000" +i["image_link"][1:]
    
    print(grievance_all)
    
    return jsonify({"status": 'success', "data": grievance_all})


@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    if request.method == 'POST':
        data = request.get_data()
        data = json.loads(data)

        im = Image.open(BytesIO(base64.b64decode(data['image_link'])))
        image_link='./static/uploads/'+str(datetime.now())+str(data['grievance_id'])+'.jpeg'
        im.save(image_link, 'JPEG')
        
        data["image_link"] = image_link

        data["assigned_authority"] = "null"
        data["assigned_date"] = str(datetime.now())
        data["status"] = "unsolved"
        data["timestamp"] = str(datetime.now())
        data["area"] = "unpredicted"

        mongo.db.grievance.insert_one(data)

        predict()

        return jsonify({"status": 'success', "message": "registered successfully!"})


@app.route('/records')
def records():
    all = list(mongo.db.grievance.find())
    return render_template('table.html', all=all)


@app.route('/reports')
def reports():
    grievance_all = list(mongo.db.grievance.find())

    pothole = [0] * 12
    sewage = [0] * 12  # Total grievance reported
    garbage = [0] * 12

    totalpothole = totalsewage = totalgarbage = 0   # Grievances reported

    solved = [0] * 12   # Solved vs Pending
    unsolved = [0] * 12

    for i in grievance_all:
        if(i["grievance_type"] == "sewage"):
            # pothole.append(i["grievance_type"])
            date, time = i["assigned_date"].split(" ")
            year, month, day = date.split("-")
            sewage[int(month)-1] += 1
            totalsewage += 1

            if(i["status"] == "unsolved"):
                unsolved[int(month)-1] += 1
            else:
                solved[int(month)-1] += 1

        if(i["grievance_type"] == "pothole"):
            # pothole.append(i["grievance_type"])
            date, time = i["assigned_date"].split(" ")
            year, month, day = date.split("-")
            pothole[int(month)-1] += 1
            totalpothole += 1

            if(i["status"] == "unsolved"):
                unsolved[int(month)-1] += 1
            else:
                solved[int(month)-1] += 1
        if(i["grievance_type"] == "garbage"):
            # pothole.append(i["grievance_type"])
            date, time = i["assigned_date"].split(" ")
            year, month, day = date.split("-")
            garbage[int(month)-1] += 1
            totalgarbage += 1

            if(i["status"] == "unsolved"):
                unsolved[int(month)-1] += 1
            else:
                solved[int(month)-1] += 1

    return render_template('admin.html', garbage=garbage, seewage=sewage, pothole=pothole, solved=solved, unsolved=unsolved, totalsewage=totalsewage, totalgarbage=totalgarbage, totalpothole=totalpothole)


def getLocationDetails(latitude, longitude):
    latitude = float(latitude)
    longitude = float(longitude)

    gp = herepy.GeocoderReverseApi(
        '7xcRjOXj4yGyENeYkpSvqlXE4Ahyx3TReJHGN71yQ80')
    response = gp.retrieve_addresses([latitude, longitude])
    response = str(response)
    response = ast.literal_eval(response)
    response = response["items"][0]["address"]["label"]

    return response


@app.route('/bar')
def bar():
    pincode = [11, 12, 11, 13, 15, 11, 16, 17]
    tmp = set(pincode)
    count = []
    for i in tmp:
        count.append(pincode.count(i))
    tick_label = ['one', 'two', 'three', 'four', 'five', 'six']

    pincode = list(tmp)
    
    plt.bar(pincode, count, tick_label=tick_label,
            width=0.8, color=['red', 'green'])
    plt.xlabel('Problems')
    plt.ylabel('Area')
    plt.title('Pincode')
    # plt.savefig('/graphs'+str(datetime.now())+'.png')
    return 'hii'


@app.route("/index")
def index():
    grievance_all = list(mongo.db.grievance.find())

    for i in grievance_all:
        print(i["area"])
        if i['area'] == "unpredicted":
            
            longitude = float(i['longitude'])
            latitude = float(i['latitude'])
            res = getLocationDetails(latitude, longitude)
            
            ass_array = {"virar": [19.4564, 72.7925],
                         "panvel": [18.9894, 73.1175],
                         "ghatkopar": [19.0858, 72.9090],
                         "dahisar": [19.2494, 72.8596],
                         "mira road ": [19.2871, 72.8688]}
            list_distance = {}
            for x in ass_array:
                list_distance[x] = distance(
                    latitude, ass_array[x][0], longitude, ass_array[x][1])
            
            distance_min = min(list_distance, key=list_distance.get)
            update_authority = mongo.db.grievance.find_one_and_update(
                {'grievance_id': i["grievance_id"]}, {'$set': {"assigned_authority": distance_min}})
            update_location = mongo.db.grievance.find_one_and_update(
                {'grievance_id': i["grievance_id"]}, {'$set': {"area": res}})

    return render_template('problems.html', all=grievance_all)


@app.route('/solve/<id1>')
def solve(id1):
    mongo.db.grievance.find_one_and_update(
        {'grievance_id': id1}, {'$set': {'status': 'solved'}})
    return redirect('/index')


@app.route("/userspecific/<id>")
def userspecific(id):
    grievance_all = list(mongo.db.grievance.find({"user_id": id}))

    for i in grievance_all:
        if 'area' not in i or i['area'] == "unpredicted":
            longitude = float(i['longitude'])
            latitude = float(i['latitude'])
            res = getLocationDetails(latitude, longitude)
            update_location = mongo.db.grievance.find_one_and_update(
                {'grievance_id': i["grievance_id"]}, {'$set': {"area": res}})

    return render_template('problems.html', all=grievance_all)


@app.route("/virar")
def virar():
    grievance_all = list(mongo.db.grievance.find(
        {"assigned_authority": "virar"}))

    for i in grievance_all:
        if 'area' not in i or i['area'] == "unpredicted":
            longitude = float(i['longitude'])
            latitude = float(i['latitude'])
            res = getLocationDetails(latitude, longitude)
            update_location = mongo.db.grievance.find_one_and_update(
                {'grievance_id': i["grievance_id"]}, {'$set': {"area": res}})
            update_location = mongo.db.grievance.find_one_and_update(
                {'grievance_id': i["grievance_id"]}, {'$set': {"assigned_authority": 'virar'}})

            grievance_all = list(mongo.db.grievance.find(
                {"assigned_authority": "virar"}))
    return render_template('problems.html', all=grievance_all)


@app.route("/panvel")
def panvel():
    grievance_all = list(mongo.db.grievance.find(
        {"assigned_authority": "panvel"}))

    for i in grievance_all:
        if 'area' not in i or i['area'] == "unpredicted":
            longitude = float(i['longitude'])
            latitude = float(i['latitude'])
            res = getLocationDetails(latitude, longitude)
            update_location = mongo.db.grievance.find_one_and_update(
                {'grievance_id': i["grievance_id"]}, {'$set': {"area": res}})
            update_location = mongo.db.grievance.find_one_and_update(
                {'grievance_id': i["grievance_id"]}, {'$set': {"assigned_authority": 'panvel'}})

            grievance_all = list(mongo.db.grievance.find(
                {"assigned_authority": "panvel"}))
    return render_template('problems.html', all=grievance_all)


@app.route("/ghatkopar")
def ghatkopar():
    grievance_all = list(mongo.db.grievance.find(
        {"assigned_authority": "ghatkopar"}))

    for i in grievance_all:
        if 'area' not in i or i['area'] == "unpredicted":
            longitude = float(i['longitude'])
            latitude = float(i['latitude'])
            res = getLocationDetails(latitude, longitude)
            update_location = mongo.db.grievance.find_one_and_update(
                {'grievance_id': i["grievance_id"]}, {'$set': {"area": res}})
            update_location = mongo.db.grievance.find_one_and_update(
                {'grievance_id': i["grievance_id"]}, {'$set': {"assigned_authority": 'ghatkopar'}})

            grievance_all = list(mongo.db.grievance.find(
                {"assigned_authority": "ghatkopar"}))
    return render_template('problems.html', all=grievance_all)


@app.route("/dahisar")
def dahisar():
    grievance_all = list(mongo.db.grievance.find(
        {"assigned_authority": "dahisar"}))

    for i in grievance_all:
        if 'area' not in i or i['area'] == "unpredicted":
            longitude = float(i['longitude'])
            latitude = float(i['latitude'])
            res = getLocationDetails(latitude, longitude)
            update_location = mongo.db.grievance.find_one_and_update(
                {'grievance_id': i["grievance_id"]}, {'$set': {"area": res}})
            update_location = mongo.db.grievance.find_one_and_update(
                {'grievance_id': i["grievance_id"]}, {'$set': {"assigned_authority": 'dahisar'}})

            grievance_all = list(mongo.db.grievance.find(
                {"assigned_authority": "dahisar"}))
    return render_template('problems.html', all=grievance_all)


@app.route("/mira road")
def miraroad():
    grievance_all = list(mongo.db.grievance.find(
        {"assigned_authority": "mira road"}))

    for i in grievance_all:
        if 'area' not in i or i['area'] == "unpredicted":
            longitude = float(i['longitude'])
            latitude = float(i['latitude'])
            res = getLocationDetails(latitude, longitude)
            update_location = mongo.db.grievance.find_one_and_update(
                {'grievance_id': i["grievance_id"]}, {'$set': {"area": res}})

            grievance_all = list(mongo.db.grievance.find(
                {"assigned_authority": "mira road"}))
    return render_template('problems.html', all=grievance_all)


@app.route("/sewage")
def sewage():
    grievance_all = list(mongo.db.grievance.find({"grievance_type": "sewage"}))

    for i in grievance_all:
        if 'area' not in i or i['area'] == "unpredicted":
            longitude = float(i['longitude'])
            latitude = float(i['latitude'])
            res = getLocationDetails(latitude, longitude)
            update_location = mongo.db.grievance.find_one_and_update(
                {'grievance_id': i["grievance_id"]}, {'$set': {"area": res}})

            grievance_all = list(mongo.db.grievance.find(
                {"grievance_type": "sewage"}))
    return render_template('problems.html', all=grievance_all)


@app.route("/garbage")
def garbage():
    grievance_all = list(mongo.db.grievance.find(
        {"grievance_type": "garbage"}))
    for i in grievance_all:
        if 'area' not in i or i['area'] == "unpredicted":
            longitude = float(i['longitude'])
            latitude = float(i['latitude'])
            res = getLocationDetails(latitude, longitude)
            update_location = mongo.db.grievance.find_one_and_update(
                {'grievance_id': i["grievance_id"]}, {'$set': {"area": res}})

            grievance_all = list(mongo.db.grievance.find(
                {"grievance_type": "garbage"}))
    return render_template('problems.html', all=grievance_all)


@app.route("/potholes")
def potholes():
    grievance_all = list(mongo.db.grievance.find(
        {"grievance_type": "pothole"}))

    for i in grievance_all:
        if 'area' not in i or i['area'] == "unpredicted":
            longitude = float(i['longitude'])
            latitude = float(i['latitude'])
            res = getLocationDetails(latitude, longitude)
            update_location = mongo.db.grievance.find_one_and_update(
                {'grievance_id': i["grievance_id"]}, {'$set': {"area": res}})

            grievance_all = list(mongo.db.grievance.find(
                {"grievance_type": "potholes"}))
    return render_template('problems.html', all=grievance_all)


def sendMail(to, subject, body):
    gmail_user = 'lcinfinitie@gmail.com'
    gmail_password = '8149379515r'

    sent_from = gmail_user
    to = "singroleketan@gmail.com"
    subject = subject
    body = body

    email_text = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (sent_from, to, subject, body)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, to, email_text)
        server.close()

        print('Email sent!')
        return 'Email sent!'
    except Exception as e:
        print('Something went wrong...'+str(e))
        return 'Email not sent!'


if __name__ == '__main__':
    app.run(host=host, port=port, debug=True)
