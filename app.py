import numpy as np
import datetime as dt
from datetime import date

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Station = Base.classes.station
Measurement = Base.classes.measurement


app = Flask(__name__)

@app.route("/")
def home():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"--Precipitation (Inches) by Date<br/>"
        f"/api/v1.0/stations<br/>"
        f"--Stations information<br/>"
        f"/api/v1.0/tobs<br/>"
        f"--A list of Temperature Observed from the most active station for the last year<br/>"
        f"/api/v1.0/YYYY-MM-DD<br/>"
        f"--Minimum, Maximum and Average Temperature Observed for a given start range<br/>"
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD<br/>"
        f"--Minimum, Maximum and Average Temperature Observed for a given start-end range<br/>"
        f"Note: Data available from 2010-01-01 to 2017-08-23<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    prcp_dict = {}
    for prcp_date, prcp_prcp in results:
        prcp_dict[prcp_date] = prcp_prcp
    
    return jsonify(prcp_dict)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station).all()
    session.close()
    all_stations = []
    for i in results:
        station_dict = {}
        station_dict["id"] = i.id
        station_dict["station"] = i.station
        station_dict["latitude"] = i.latitude
        station_dict["longitude"] = i.longitude
        station_dict["elevation"] = i.elevation
        all_stations.append(station_dict)
    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    most_active = session.query(Measurement.station).group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]
    
    latest = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year_ago = date.fromisoformat(latest[0]) - dt.timedelta(days=365)
    
    tobs_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago).\
        filter(Measurement.station == most_active).all()
    session.close()
    
    tobs_list = []
    for tobs_date, tobs_tobs in tobs_data:
        tobs_dict = {}
        tobs_dict["date"] = tobs_date
        tobs_dict["tobs"] = tobs_tobs
        tobs_list.append(tobs_dict)
        
    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
def temp_date_start(start):
    session = Session(engine)
    temp = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()
    
    temp_list = [round(i,1) for t in temp for i in t]
    
    return jsonify(temp_list)


@app.route("/api/v1.0/<start>/<end>")
def temp_date_start_end(start, end):
    session = Session(engine)
    temp = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()
    
    temp_list = [round(i,1) for t in temp for i in t]
    
    return jsonify(temp_list)


if __name__ == '__main__':
    app.run(debug=True)