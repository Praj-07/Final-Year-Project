from flask import Flask, render_template, request, jsonify

from flask_sqlalchemy import SQLAlchemy
import sqlite3
from chat import get_response
from num_to_words import num_to_word
from num2words import num2words
import pandas as pd
import numpy as np
import pickle

app = Flask(__name__)


data = pd.read_csv("cleaned_data.csv")
pipe = pickle.load(open("model.pkl",'rb'))

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.post("/bot")
def bot():
    text = request.get_json().get("message")
    response = get_response(text)

    message = {"answer": response}
    return jsonify(message)



@app.route('/price')
def price():

    locations = sorted(data['location'].unique())
    return render_template('price.html',locations=locations)

@app.route('/predict', methods=["GET", "POST"])
def predict():
    if request.method == 'POST':
        data=request.get_json()
        
        location = data.get('location')
        bhk = data.get('bhk')
        bath = float(data.get('bath'))
        sqft = float(data.get('total_sqft'))
    
        input = pd.DataFrame ([[sqft,bath,location,bhk]],columns=['total_sqft','bath','location','bhk'])
        prediction = pipe.predict(input)[0] * 1e5
        output = str(np.round(prediction, 2))
        output = int(float(output))
        words = num_to_word(output, lang='en')
        predict_data = {"price": output,"price_word":words}
        return jsonify(predict_data)
        # return render_template('price.html', prediction_text=output, words=words)
    print("hellow")
    return render_template('price.html')




@app.route('/recommendation', methods=["GET", "POST"])
def recommendation():
    locations = sorted(data['location'].unique())

    if request.method == 'POST':
        conn = sqlite3.connect('property_data.db')
        cursor = conn.cursor()
   
        location = request.form.get('location')
        minprice = request.form.get('minprice')
        maxprice = request.form.get('maxprice')

        houses = cursor.execute("select * from properties where location = ? and (price between ? and ?)", (location,minprice,maxprice,)).fetchall()
        conn.close()
        return render_template('recommendation.html',locations=locations, houses=houses )

            
    return render_template('recommendation.html',locations=locations)

if __name__ == "__main__":
    app.run(debug=True)
