# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, session, url_for
import csv

app = Flask(__name__)

CSV_PATH='OUTPUT.csv'

@app.route('/', methods=["GET","POST"])
def home():
    data = open_csv(CSV_PATH)
    new_data = {x['Document number/name']:x for x in data  }
    return render_template('home.html', data=new_data)

def open_csv(fpath):
    with open(fpath, 'r') as file:
        file_csv = csv.DictReader(file)
        response = list(file_csv)
    return response

if __name__ == '__main__':
    app.run(debug=False)