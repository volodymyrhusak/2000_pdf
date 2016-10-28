# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, session, url_for
import csv
app = Flask(__name__)

CSV_PATH='CSV_PDFs.csv'

@app.route('/')
def home():
    data = open_csv(CSV_PATH)
    return render_template('home.html', data=data )
	

def open_csv(fpath):
    with open(fpath, 'r') as file:
        file_csv = csv.DictReader(file)
        response = list(file_csv)
        # file_csv.close()
    return response

if __name__ == '__main__':
    app.run(debug=True)