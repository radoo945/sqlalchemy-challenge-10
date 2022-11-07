from flask import Flask, jsonify, request, render_template

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt
import dateutil.relativedelta as rd


api_version = "v1.0"

datetime_format = "%Y-%m-%d"

def try_parse_datetime(value):

	
	date = dt.datetime.now()
	#
	if type(value) is str and "-" in value:
		try:
			date = dt.datetime.strptime(value, datetime_format)
		except Exception as e:
			print(e)
			return f"Please format your dates as YYYY-MM-DD"

	else:
		try:
			date = dt.datetime.fromtimestamp(int(value)/1000)
		except Exception as e:
			print(e)
			return f"Please format your dates as corresponding to the POSIX timestamp"
	# return date
	return date

def api_path(endpoint=None):
	
	
	if (endpoint):
		
		if (endpoint.startswith("/")):
			return f"/api/{api_version}{endpoint}"
		else:
			return f"/api/{api_version}/{endpoint}"
	
	return f"/api/{api_version}"


def api_endpoints(base_url):
	
	if ("/" in base_url):
		base_url = base_url.split("/")[0]
	return {
		"home": {
			"info": "This lists all the avaliable endpoints",
			"link": base_url
		},
		"precipitation": {
			"info": "Return the JSON representation of the precipitation data",
			"link": base_url + api_path("precipitation")
		},
		"stations": {
			"info": "Return the JSON representation of the station's data",
			"link": base_url + api_path("stations")
		},
		"tobs": {
			"info": "Return a JSON list of temperature observations (TOBS) for the previous year",
			"link": base_url + api_path("tobs")
		},
		"temperature info start": {
			"info": "Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start range",
			"link": base_url + api_path("2016-08-23")
		},
		"temperature info start and end": {
			"info": "Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start and end range",
			"link": base_url + api_path("2016-08-23/2017-08-23")
		}
	}

def sqlite_link():
	
	
	engine = create_engine("sqlite:///Resources/hawaii.sqlite")
	
	Base = automap_base()
	
	Base.prepare(engine, reflect=True)
	
	Measurement = Base.classes.measurement
	Station = Base.classes.station
	
	session = Session(engine)
	
	return session, Measurement, Station

def query_to_json_dict_list(query):
	
	
	json_list = []
	
	for instance in query:
		
		class_dict = {}
		
		for key, value in instance.__dict__.items():
			
			if not key.startswith("_"):
				
				class_dict[key] = value
		
		json_list.append(class_dict)
	
	return json_list
	
def most_occurrence(session, table_column):
	
	return session.query(
		
		table_column
	
	).group_by(table_column).\
	order_by(
		
		func.count(table_column).desc()
	).first()[0]

def most_recent(session, table_column):
	
	
	return session.query(table_column).\
	order_by(
		
		table_column.desc()
	).first()[0]


app = Flask(__name__)



@app.route("/")
@app.route("/index")
@app.route("/home")
def home():
	
	return render_template("home.html", endpoints=api_endpoints(request.base_url))

@app.route(api_path("precipitation"))
def precipitation():
	
	session, Measurement, _ = sqlite_link()
	
	precipitation_scores = {}
	
	query_results = session.query(
		
		Measurement.prcp
	).order_by(Measurement.date)
	
	for result in query_results:
		
		key = str(result.date)
		value = result.prcp
		precipitation_scores[key] = value
	
	session.close()
	
	return jsonify(precipitation_scores)

@app.route(api_path("stations"))
def stations():
	
	session, _, Station = sqlite_link()
	
	stations_list = query_to_json_dict_list(session.query(Station))
	
	session.close()
	
	return jsonify(stations_list)

@app.route(api_path("tobs"))
def tobs():
	
	#	
	most_active_station = most_occurrence(session, Measurement.station)
	
	end_date = dt.datetime.strptime(
		most_recent(session, Measurement.date), 
		datetime_format
	)
	
	start_date = end_date - rd.relativedelta(years = 1)
	
	station_data_range = session.query(Measurement).filter(
		
		Measurement.station == most_active_station,
		
		func.DATE(Measurement.date) >= func.DATE(start_date.date())
	).order_by(Measurement.date)
	
	stations_list = query_to_json_dict_list(station_data_range)
	
	session.close()
	
	return jsonify(stations_list)

@app.route(api_path("<start>"))
def temperature_data_start(start):
	
	
	start_date = try_parse_datetime(start)
	
	if type(start_date) is str:
		return start_date
	
	session, Measurement, _ = sqlite_link()
	
	most_active_station = most_occurrence(session, Measurement.station)
	
	station_tobs_min, station_tobs_max, station_tobs_avg = session.query(
		func.min(Measurement.tobs),
		func.max(Measurement.tobs),
		func.avg(Measurement.tobs)
	).filter(
		
		Measurement.station == most_active_station,
		
		func.DATE(Measurement.date) >= func.DATE(start_date.date())
	).first()
	
	station_info = {
		"TMIN" : station_tobs_min,
		"TMAX" : station_tobs_max,
		"TAVG" : station_tobs_avg
	}
	
	session.close()
	
	return jsonify(station_info)


@app.route(api_path("<start>/<end>"))
def temperature_data_start_end(start, end):
	
	
	end_date = try_parse_datetime(end)
	
	if type(end_date) is str:
		return end_date
	
	
	if type(start_date) is str:
		return start_date
	
	session, Measurement, _ = sqlite_link()
	
	most_active_station = most_occurrence(session, Measurement.station)
	
	station_tobs_min, station_tobs_max, station_tobs_avg = session.query(
		func.min(Measurement.tobs),
		func.max(Measurement.tobs),
		func.avg(Measurement.tobs)
	).filter(
		
		Measurement.station == most_active_station,
		
		func.DATE(Measurement.date) >= func.DATE(start_date.date()),
		func.DATE(Measurement.date) <= func.DATE(end_date.date())
	).first()
	
	station_info = {
		"TMIN" : station_tobs_min,
		"TMAX" : station_tobs_max,
		"TAVG" : station_tobs_avg
	}
	
	session.close()
	
	return jsonify(station_info)


if __name__ == "__main__":
	
	app.run(debug=True)
