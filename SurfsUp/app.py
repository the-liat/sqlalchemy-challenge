# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine = engine, reflect = True)

# Save references to each table
Precipt = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

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
        f"Available Routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/start_date<br>"
        f"/api/v1.0/start_date/end_date"   
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Precipitation Analysis Results"""
    # Query participation in last 12 months of data
    prcp_data = session.query(Precipt.date, Precipt.prcp).\
        filter(Precipt.date <= '2017-08-23').\
        filter(Precipt.date >= '2016-08-23').all()

    # Convert to dictionary 
    prcp_all = []
    for date, prcp in prcp_data:
        prcp_dict = {}
        prcp_dict[date] = prcp
        prcp_all.append(prcp_dict)

    session.close()

    return jsonify(prcp_all)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all stations"""
    # Query all stations
    results = session.query(Station.station).all()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    session.close()

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def temps():
    """Query the dates and temperature observations of the most-active station"""
    # Query all temps
    active_temp = session.query(Precipt.tobs).\
        filter(Precipt.station == "USC00519281").\
        filter(Precipt.date <= '2017-08-23').\
        filter(Precipt.date >= '2016-08-23').all()

    # Convert list of tuples into normal list
    past_year_temps = list(np.ravel(active_temp))

    session.close()

    return jsonify(past_year_temps)

@app.route("/api/v1.0/<start>")
def start_date(start):
    """calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date"""
    # Query temp
    active_summary = session.query(func.min(Precipt.tobs), 
                                   func.max(Precipt.tobs), 
                                   func.avg(Precipt.tobs)).\
                                    filter(Precipt.station == "USC00519281").\
                                    filter(Precipt.date >= start).all()

    # Convert to dictionary 
    stats_dict = {}
    stats_dict["min"] = active_summary[0][0]
    stats_dict["max"] = active_summary[0][1]
    stats_dict["mean"] = active_summary[0][2]

    session.close()

    return jsonify(stats_dict)

@app.route("/api/v1.0/<start>/<end>")
def end_date(start, end):
    """Returns the min, max, and average temperatures calculated from the given start date to the given end date"""
    # Query all temps
    active_summary = session.query(func.min(Precipt.tobs), 
                                   func.max(Precipt.tobs), 
                                   func.avg(Precipt.tobs)).\
                                    filter(Precipt.station == "USC00519281").\
                                    filter(Precipt.date >= start).\
                                    filter(Precipt.date <= end).all()

    # Convert to dictionary 
    stats_dict = {}
    stats_dict["min"] = active_summary[0][0]
    stats_dict["max"] = active_summary[0][1]
    stats_dict["mean"] = active_summary[0][2]

    session.close()

    return jsonify(stats_dict)

if __name__ == '__main__':
    app.run(debug=True)

