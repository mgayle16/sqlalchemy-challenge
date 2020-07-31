import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect
Base = automap_base()
# reflect my tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Function used to calculate my date range
def date_calc():
    #Retreive the latest date present in the database
    oldest_date = session.query(func.max(Measurement.date)).all()
   
    # 1 year date range calc.
    today = dt.date.today()
    #Format to date format
    oldest_date_datefmt = today.replace(year=int(Latest_date[0][0][:4]),\
                                        month=int(Latest_date[0][0][5:7]),\
                                        day=int(Latest_date[0][0][8:]))
    
    # Calculate the date 1 year ago from the recent date
    One_Year_back_date = oldest_date_datefmt-dt.timedelta(days=365)
    
    Current_Year_End_Date = oldest_date_datefmt.strftime("%Y-%m-%d")
    Prior_Year_Start_Date = Year_backdate.strftime("%Y-%m-%d")
    
    Year_list = [Prior_Year_Start_Date,Current_Year_End_Date]
    return(tuple(Year_list))

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return(
        f"Available Routes are referenced below:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"Put the start date in 'YYYY-MM-DD' format<br/>"
        f"/api/v1.0/<start>/<end><br/>"   
        f"Put the dates in 'YYYY-MM-DD/YYYY-MM-DD' format<br/>"
        )  

@app.route("/api/v1.0/precipitation")
def precipitation():
    """
        Convert the query results to a Dictionary using date as the key and prcp as the value.
        Return the JSON representation of your dictionary.
        
    """
    # Calling date_calc function to get the start & end date of the previous year
    Range = date_calc()
    End_date = Range[1]
    Start_date = Range[0]
    # Query for the dates and temperature observations from the last year.
    results = session.query(Measurement.date, Measurement.station,Measurement.prcp).\
                                       filter(Measurement.date <= End_date).\
                                       filter(Measurement.date >= Start_date).all()                                                                  
    list = []
    for result in results:
        dict = {"Date":result[0],"Station":result[1],"Precipitation":result[2]}
        list.append(dict)
    return jsonify(list)

@app.route("/api/v1.0/stations")
def stations():
    """ Return a JSON list of stations from the dataset 
    """    
    stations = session.query(Station.station,Station.name).all()
    
    list=[]
    for station in stations:
        dict = {"Station ID:":stations[0],"Station Name":stations[1]}
        list.append(dict)

    return jsonify(list)

@app.route("/api/v1.0/tobs")
def tobs():
    """ Return a JSON list of Temperature Observations (tobs) for the prior year."""  
    Range = date_calc()
    End_date = Range[1]
    Start_date = Range[0]
    tobs = session.query(Measurement.date,Measurement.tobs).\
                            filter(Measurement.date <= End_date).\
                            filter(Measurement.date >= Start_date).all()
    list = []
    for temp in tobs:
        dict = {"date": temp[0], "tobs": temp[1]}
        list.append(dict)

    return jsonify(list)  

""" Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    Note: returning dictionary instead of list"""
@app.route("/api/v1.0/<start>")
def t_start(start):
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).order_by(Measurement.date.desc()).all()
    #list = []
    print(f"Analysis of temps that for dates that are greater than or equivalent to start date")
    for temps in results:
        dict = {"Minimum Temp":results[0][0],"Average Temp":results[0][1],"Maximum Temp":results[0][2]}
    return jsonify(dict) 

    @app.route("/api/v1.0/<start>/<end>")
def t_start_end(start,end):
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= start, Measurement.date <= end).order_by(Measurement.date.desc()).all()
    #list = []
    print (f"TAnalysis of temps that for dates that are greater than or equivalent to the start date & less than or equivalent to end date")
    for temps in results:
        dict = {"Minimum Temp":results[0][0],"Average Temp":results[0][1],"Maximum Temp":results[0][2]}
    return jsonify(dict)   

if __name__ == '__main__':
    app.run(debug=True)
