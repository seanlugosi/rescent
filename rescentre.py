
import re,os
import beatbox
import pandas as pd
import numpy as np
import argparse
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from os.path import isfile,join
from flask import Flask, request, redirect, url_for,render_template,json as fjson,send_from_directory
from werkzeug import secure_filename
from mapping import Autotagging,Manualtagging
from defs import *

UPLOAD_FOLDER = './uploads'
PIVOT_FOLDER = './pivot'
ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PIVOT_FOLDER']= PIVOT_FOLDER

@app.route('/feedback',methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = randomword(6)+'_'+secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('csuppfb',df=filename))
    return render_template('mappingtest.html')

@app.route('/csuppfb', methods=['POST','GET'])
def csuppfb():
    csuppreport = None
    if request.args['df'] :
        dataf1 =request.args['df']
        dataf = pd.read_csv(app.config['UPLOAD_FOLDER']+'/'+dataf1)        
        index_list=["Case Owner","Case Number","Support Survey - Service rating"]
        value_list = ["Age (Hours)"]
        pvt = pd.pivot_table(dataf, index=index_list, values=value_list,
                           aggfunc=[np.sum, np.mean], fill_value=0, columns=None)          
        
    print csuppreport
    agent_df = []
    for agent in pvt.index.get_level_values(0).unique():
        agent_df.append([agent, pvt.xs(agent, level=0).to_html()])
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template("csupp.html")


    template_vars={"title": "CSUPP FB REPORT", 
                "Excellent": get_summary_stats(dataf,"Excellent"),
                "Good": get_summary_stats(dataf,"Good"),
                "csupp_pivot_table": pvt.to_html(),
                "agent_detail": agent_df}

    html_out = template.render(template_vars)
    return html_out


def get_summary_stats(dataf, product):
    """
    Get a stats summary 
    """
    if request.args['df'] :
        dataf1 =request.args['df']
        dataf = pd.read_csv(app.config['UPLOAD_FOLDER']+'/'+dataf1)   
    results=[]
    results.append(dataf[dataf["Support Survey - Service rating"]==product]["Closed"].mean())
    results.append(dataf[dataf["Support Survey - Service rating"]==product]["Age (Hours)"].mean())
    return results

    

@app.route('/')
def homepage():
    author = "Sean"
    name = "ResolutionCentreHome"
    return render_template('index.html', author=author, name=name)

@app.route('/revenue')
def camps():
    author = "Sean"
    name = "revenue"
    return render_template('camps.html', author=author, name=name)

@app.route('/bids')
def bids():
    author = "Sean"
    name ="bidding"
    return render_template('bidding.html',author=author,name=name)

@app.route('/decisiontree')
def decisiontree():
    author = "Sean"
    name ="decisiontree"
    return render_template('showTree2.html',author=author,name=name)

@app.route('/gamap',methods=['GET', 'POST'])
def gamap():
    if request.method == 'POST':
        file = request.files['file']
        type_url = request.form['optionsRadios']
        if file and allowed_file(file.filename):
            filename = randomword(6)+'_'+secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('output',filename=filename,urlmode=type_url))
    
    return render_template('upload.html')

@app.route('/output/<filename>')
def output(filename):
    if request.args['urlmode']:
        url = request.args['urlmode']
    else :
        url= 'modern'
    my_file=prep_file(app.config['UPLOAD_FOLDER']+'/'+filename)
    my_file=filter_agg(my_file)
    meta=meta_table(my_file)
    print meta.data()
    mappings=[]
    profileIDs=[]
    for i in meta.data():
        mapping_container=dict()
        map_dict=get_goals((i[0][0],),my_file)
        auto=Autotagging(i[0],map_dict)
        manual=Manualtagging(i[0],map_dict,adcontent=url)
        mapping_container.update({'Auto-tagging':auto.html_export()})
        mapping_container.update({'Manual-tagging':manual.html_export()})
        mappings.append(mapping_container)
        profileIDs.append(auto.serialize_profiles())

    return render_template('main.html',mappings=mappings,profileIDs=profileIDs)


@app.route('/result',methods = ['POST', 'GET'])
def result():
   if request.method == 'POST':
      result = request.form
      return render_template("csupp.html",result = result)


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)

