from flask import Flask, jsonify, redirect, url_for, request, render_template, session
from flask_dropzone import Dropzone
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class

import os

###################################################################################################################################################
####DATA BASE######################################################################################################################################
###################################################################################################################################################
# import sqlite3
# import csv

# conn = sqlite3.connect('fruits.sqlite')
# cur = conn.cursor()

# cur.execute('DROP TABLE IF EXISTS fruit_nutrients')
# cur.execute('''
# CREATE TABLE "fruit_nutrients"(
#     "food_name" TEXT,
#     "food_type" TEXT,
#     "food_description" TEXT,
#     "energy" REAL,
#     "water" REAL,
#     "sugar" REAL,
#     "vitamin_C" REAL,
#     "calcium" REAL,
#     "carbohydrate" REAL,
#     "protein" REAL,
#     "sodium" REAL,
#     "vitamin_E" REAL,
#     "cooper" REAL,
#     "iron" REAL,
#     "magnesium" REAL,
#     "phosphorus" REAL,
#     "potassium" REAL,
#     "zinc" REAL,
#     "total_fat" REAL,
#     "saturated_fat" REAL,
#     "fiber_total_dietary" REAL
# )
# ''')

# with open("./static/Final_Fruits_Veggies_NoHeader.csv", 'r') as csv_file:
#     for row in csv_file:
#         # print(len(row.split(",")))
#         cur.execute("INSERT INTO fruit_nutrients VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", row.split(","))
#         conn.commit()
# conn.close()

# def queryValue(fruitName):
#     conn = sqlite3.connect('fruits.sqlite')
#     cur = conn.cursor()
#     queryValue = cur.execute(f"SELECT * FROM fruit_nutrients WHERE food_name=?", (fruitName,)).fetchall()
#     # print('INSIDE THE FUNTIONC ###############################################')
#     # for dato in queryValue[0]:
#     #     print(dato)
#     # print('INSIDE THE FUNTIONC ###############################################')
#     labels = ["food_name", "food_type", "food_description", "energy", "water", "sugar", "vitamin_C", "calcium", "carbohydrate","protein", "sodium","vitamin_E", "cooper", "iron", "magnesium", "phosphorus", "potassium","zinc","total_fat", "saturated_fat", "fiber_total_dietary"]
#     returned ={}
#     # for i in range(len(queryValue[0])):
#     #     returned.append(f'{queryValue[0][i]}')

#     for i in range(len(queryValue[0])):
#         returned[f'{labels[i]}'] = queryValue[0][i]
#     # print('INSIDE THE FUNTIONC ###############################################')
#     # print(returnedDict)
#     return returned

# queryValue('banana')

###################################################################################################################################################
###MODEL PREDICTION################################################################################################################################
###################################################################################################################################################

import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk, Image
import numpy
import tensorflow as tf
from tensorflow import keras

#load the trained model to classify the images
from keras.models import load_model

model = load_model('fruits_tensorflow-100-New10-360.h5')

#dictionary to label all the dataset classes.
classes = { 
    0:'apple',
    1:'banana',
    2:'blueberry',
    3:'fig',
    4:'lemon',
    5:'orange',
    6:'peach',
    7:'persimmon',
    8:'tomato',
    9:'watermelon'
}

def classify(file_path):
    img = keras.preprocessing.image.load_img(
        file_path, target_size=(180, 180))
    img_array = keras.preprocessing.image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0) # Create a batch

    predictions = model.predict_classes(img_array)[0]
    sign = classes[predictions]
    return sign



###################################################################################################################################################
###FLASK APP#######################################################################################################################################
###################################################################################################################################################



app = Flask(__name__)
dropzone = Dropzone(app)

app.config['SECRET_KEY'] = 'supersecretkey'


# Dropzone settings
# app.config['DROPZONE_UPLOAD_MULTIPLE'] = True
app.config['DROPZONE_ALLOWED_FILE_CUSTOM'] = True
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = 'image/*'
app.config['DROPZONE_REDIRECT_VIEW'] = 'results'
# Uploads settings
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd() + '/uploads'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # set maximum file size, default is 16MB



@app.route("/", methods = ["GET", "POST"])
def index():

    sessionArguments = ['file_urls', 'prediction', 'prediction_data']
    # sessionArguments = [ "file_urls","food_name", "food_type", "food_description", "energy", "water", "sugar", "vitamin_C", "calcium", "carbohydrate","protein", "sodium","vitamin_E", "cooper", "iron", "magnesium", "phosphorus", "potassium","zinc","total_fat", "saturated_fat", "fiber_total_dietary"]
    
    
    for argument in sessionArguments:
        if argument not in session:
            session[argument] = []

    auxContainer = {'file_urls':[], 'prediction':[], 'prediction_data':[]}
    for key in sessionArguments:
        auxContainer[key] = session[key]

    # handle image upload from Dropzone
    if request.method == "POST":
        file_obj = request.files
        for f in file_obj:
            file = request.files.get(f)
            # resultContainer = {'file_urls':[], 'prediction':[], 'prediction_data':[]}
            # save the file with to our photos folder
            filename = photos.save(file, name=file.filename)
            # print("RESULT NEW*********************************************")
            path_image = f'./uploads/{filename}'
            # print(path_image)
            # print("RESULT NEW*********************************************")
            resultPrediction = classify(path_image)
            # print("RESULT NEW*********************************************")
            # print(resultPrediction)
            # print("RESULT NEW*********************************************")
################################################################################################################################
            # #Query data for prediction from Final_Fruits_Veggies_NoHeader
            # predictionData = queryValue(resultPrediction)

            # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            # for key in predictionData.items():
            #     # session[f'{key[0]}'] = key[1]
            #     print(key[0], key[1])

            # # append image urls

            # for key in sessionArguments:
            #     auxContainer[key].append()

            auxContainer['file_urls'].append(photos.url(filename))
            auxContainer['prediction'].append(resultPrediction)
            # auxContainer['prediction_data'].append(predictionData)

            # print(file.filename)
        
        session['file_urls'] = auxContainer['file_urls']
        session['prediction'] = auxContainer['prediction']
        # session['prediction_data'] = auxContainer['prediction_data']

        # print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        # print(session['prediction_data'][0].keys())

        return "uploading..."

    # return dropzone template on GET request  
    return render_template('index.html')

@app.route('/results')
def results():
    # redirect to home if no images to display
    if "file_urls" not in session or session['file_urls'] == []:
        return redirect(url_for('index'))
        
    # set the file_urls and remove the session variable
    file_urls = session['file_urls']
    session.pop('file_urls', None)
    prediction = session['prediction']
    session.pop('prediction', None)
    prediction_data = session['prediction_data']
    session.pop('prediction_data', None)

    print("##########################################")
    print(prediction_data)
    data = {'file_urls':file_urls, 'prediction': prediction, 'prediction_data': prediction_data}

    return render_template('results.html', data=data)

if __name__ == "__main__":
    app.run(debug=True)