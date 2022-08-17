import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import json
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
    return (
        f"Available Routes:<br/>"
        "/api/v1.0/precipitation: <a href='http://127.0.0.1:5000/api/v1.0/precipitation'>precipitation</a> <br/>"
        f"/api/v1.0/stations: <a href='http://127.0.0.1:5000/api/v1.0/stations'>Stations</a> <br/>"
        f"/api/v1.0/tobs: <a href='http://127.0.0.1:5000/api/v1.0/tobs'>Temp Observations</a> <br/>"
        f"/api/v1.0/<start>: <a href='http://127.0.0.1:5000/api/v1.0/start'>Start</a> <br/>"
        f"/api/v1.0/<start>/<end>: <a href='http://127.0.0.1:5000/api/v1.0/start/end'>Start/End</a> <br/> <br/> <br/>"
        f"**IMPORTANT - DATES MUST BE IN YYYY-MM-DD FORMAT for App Route to work**"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all precipitation values"""
    # Query all date/precipitation combo values
    results = session.query(Measurement.date,Measurement.prcp).all()

    session.close()
    
    # Create a dictionary, iterate through results and append to dictionary
    PrecipitationList = []
    for date, prcp in results:
        Precipitation_dict = {}
        Precipitation_dict["date"] = date
        Precipitation_dict["prcp"] = prcp
        PrecipitationList.append(Precipitation_dict)

    #jsonify the dictionary
    return jsonify(PrecipitationList)




@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    # Query all temperature observations
    results = session.query(Station.id,Station.station).all()

    session.close()
    
    # Create a dictionary, iterate through results and append to dictionary
    StationList = []
    for id, station in results:
        Station_dict = {}
        Station_dict["id"] = id
        Station_dict["station"] = station
        StationList.append(Station_dict)

    #jsonify the dictionary
    return jsonify(StationList)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all temperature observations"""
    # Query all temperature observations
    results = session.query(Measurement.station, Measurement.tobs).all()

    session.close()
    
    # Create a dictionary, iterate through results and append to dictionary
    TempObs = []
    for station,tobs in results:
        TempObs_dict = {}
        TempObs_dict["station"] = station
        TempObs_dict["tobs"] = tobs
        TempObs.append(TempObs_dict)

    #jsonify the dictionary
    return jsonify(TempObs)


########################################################################
########################################################################
## IMPORTANT - DATES MUST BE IN YYYY-MM-DD FORMAT for App Route to work
########################################################################
########################################################################


@app.route("/api/v1.0/<start>")     #, defaults={'start': '08-23-2016'}
def Start(start):
    """Fetch the Minimum, Average Temp, and Max Temperature for a given period greater than the start date."""

    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return functions of temperature observations"""
    # Query all temperature observations, get min, max, and average since the start date value
    resultsMinMaxAvg = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date > start).all()

    session.close()

    # Create a dictionary, iterate through results and append to dictionary
    StartList = []
    for tobsmin,tobsmax,tobsavg in resultsMinMaxAvg:
        Start_dict = {}
        Start_dict["StartDate"]  = start
        Start_dict["MinTempObs"] = tobsmin
        Start_dict["MaxTempObs"] = tobsmax
        Start_dict["AvgTempObs"] = tobsavg
        StartList.append(Start_dict)

    #jsonify the dictionary
    return jsonify(StartList)


@app.route("/api/v1.0/<start>/<end>" )     #, defaults={'start': '2016-08-23','end': '2017-08-23'}
def StartEnd(start,end):

    """Fetch the Minimum, Average Temp, and Max Temperature for a given duration between the start date and end date."""
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return functions of temperature observations"""
    # Query all temperature observations, get min, max, and average since the start date value
    StartEndresultsMinMaxAvg = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date <= end).\
        filter(Measurement.date > start)

    session.close()

    # Create a dictionary, iterate through results and append to dictionary
    StartEndList = []
    for tobsmin,tobsmax,tobsavg in StartEndresultsMinMaxAvg:
        StartEnd_dict = {}
        StartEnd_dict["StartDate"]  = start
        StartEnd_dict["EndDate"]    = end
        StartEnd_dict["MinTempObs"] = tobsmin
        StartEnd_dict["MaxTempObs"] = tobsmax
        StartEnd_dict["AvgTempObs"] = tobsavg
        StartEndList.append(StartEnd_dict)

    #jsonify the dictionary
    return jsonify(StartEndList)
 

if __name__ == '__main__':
    app.run(debug=True)


#####################################
## BEGIN OLD Incorrect Method for generating dictionary instead of json
#####################################

# @app.route("/api/v1.0/precipitation")
# def precipitation():
#     # Create our session (link) from Python to the DB
#     session = Session(engine)

#     """Return a list of all precipitation values"""
#     # Query all date/precipitation combo values
#     data = engine.execute('SELECT date, prcp FROM Measurement')
#     result = json.dumps([dict(r) for r in data])
#     return result
#     session.close()

# @app.route("/api/v1.0/stations")
# def stations():
#     # Create our session (link) from Python to the DB
#     session = Session(engine)

#     """Return a list of stations"""
#     # Query all stations
#     data = engine.execute('SELECT DISTINCT(station) FROM Station')
#     result = json.dumps([dict(r) for r in data])
#     return result
#     session.close()

    ## @app.route("/api/v1.0/tobs")
## def tobs():
##     # Create our session (link) from Python to the DB
##     session = Session(engine)

##     """Return a list of all temperature observations"""
##     # Query all temperature observations
##     data = engine.execute("SELECT date,tobs FROM Measurement WHERE Station ='USC00519397' AND Date BETWEEN '2016-08-23' AND '2017-08-23' ORDER BY date DESC")
##     result = json.dumps([dict(r) for r in data])
##     return result
##     session.close()

#####################################
## END OLD Incorrect Method for generating dictionary instead of json
#####################################