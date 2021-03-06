from datetime import datetime as dt, timedelta

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

engine = create_engine("sqlite:///hawaii.sqlite", echo = False)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)


# Save reference to the table
Measurements = Base.classes.measurements # Map measurements class
Stations = Base.classes.stations # Map stations class

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################


# Defining flask routes for all the paths as specified in the homework
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
       f"Available Routes:<br/>"  
       f"/api.v1.0/precipitation<br/>"
       f"/api/v1.0/stations<br/>"
       f"/api/v1.0/tobs<br/>"
       f"/api/v1.0/start_date<br/>"
       f"/api/v1.0/start_date/end_date<br/>"
       f"Please enter dates in 'YYYY-MM-DD' format"
   )


# Query for the dates and temperature observations from the last year.
# Convert the query results to a Dictionary using date as the key and tobs as the value.
# Return the json representation of your dictionary.

@app.route("/api.v1.0/precipitation")
def precipitation():
    # Query for retrieving last 12 months of precipitation data
    # All precipitation data for last 12 months
    latest_date = session.query(Measurements.date).order_by(Measurements.date.desc()).first()[0] #Query for latest date
    format_latest_date = dt.strptime(latest_date,"%Y-%m-%d") # Formatting the date with strptime
    sel = [Measurements.date, Measurements.prcp] # sel variable for our query below
    initial_date = format_latest_date - timedelta(days=365) # This will be start date from 12 months before final date of 8/23/17
    prcp_data = session.query(*sel).filter((Measurements.date >= initial_date)).all() # Query for 12 months of prcp data
    # We now convert prcp_data into a dataframe and then into a dictionary, so that JSON responses can be sent out
    prcp_data_df  = pd.DataFrame(prcp_data,columns=["Precipitation Date", "Precipitation"]) #convert to dataframe
    prcp_data_dict= prcp_data_df.to_dict(orient='records') #convert to dictionary from the dataframe
    return jsonify(prcp_data_dict) #returning JSON response back


@app.route("/api/v1.0/stations")
def stations():
    # Function to return a json list of stations from the dataset.
    stations = session.query(Stations.name, Stations.station).all() #Query to return station names and station IDs from the Stations table
    # We now convert prcp_data into a dataframe and then into a dictionary, so that JSON responses can be sent out
    stations_df  = pd.DataFrame(stations,columns=["Station Name", "Station ID"]) #convert to dataframe
    stations_dict = stations_df.to_dict(orient='records') #convert to dictionary from the dataframe
    return jsonify(stations_dict) #returning JSON response back



@app.route("/api/v1.0/tobs")
def tobs():
    # Function to return a json list of Temperature Observations (tobs) for the previous year
    latest_date = session.query(Measurements.date).order_by(Measurements.date.desc()).first()[0] #Query for the latest date
    format_latest_date = dt.strptime(latest_date,"%Y-%m-%d") # Formatting the date with strptime
    sel = [Measurements.date, Measurements.tobs] # sel variable for our query below
    initial_date = format_latest_date - timedelta(days=365) # This will be start date from 12 months before final date of 8/23/17
    tobs_data = session.query(*sel).filter((Measurements.date >= initial_date)).all() # Query for 12 months of tobs data
    # We now convert tobs_data into a dataframe and then into a dictionary, so that JSON responses can be sent out
    tobs_data_df  = pd.DataFrame(tobs_data,columns=["Observation Date", "Temperature Observations"]) #convert to dataframe
    tobs_data_dict= tobs_data_df.to_dict(orient='records') #convert to dictionary from the dataframe
    return jsonify(tobs_data_dict) #returning JSON response back


@app.route("/api/v1.0/<start_date>/<end_date>")
def calc_temp(start_date, end_date):
    Start_Date = dt.strptime(start_date, "%Y-%m-%d")
    #Start_Date = Start_Date.replace(Start_Date.year - 1) #This is commented out because our query is for the current year and not the prior year. This code was used in section 3 of our homework
    End_Date = dt.strptime(end_date, "%Y-%m-%d")
    #End_Date = End_Date.replace(End_Date.year - 1) #This is commented out because our query is for the current year and not the prior year. This code was used in section 3 of our homework
    
    #Collect all the dates between start date and end date
    delta = End_Date - Start_Date
    date_range = []
    for i in range(delta.days + 1):
        date_range.append(Start_Date + timedelta(days=i))
       
    #Converting to stings
    str_date_range = []
    for date in date_range:
        new_date = date.strftime("%Y-%m-%d")
        str_date_range.append(new_date)
       
   #Calculate Average Tempareure , Min and Maximum temperatures within the date range    
    temp_avg = session.query(func.avg(Measurements.tobs))\
              .filter(Measurements.date.in_(str_date_range))[0][0]
    temp_min = session.query(func.min(Measurements.tobs))\
              .filter(Measurements.date.in_(str_date_range))[0][0]
    temp_max = session.query(func.max(Measurements.tobs))\
              .filter(Measurements.date.in_(str_date_range))[0][0]
       
    #Return a json list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    trip_output_dict  = {"Minimum Temperature": temp_min, "Average Temperature":temp_avg, "Maximum Temperature":temp_max}
    return jsonify(trip_output_dict)



@app.route("/api/v1.0/<start_date>")
def calc_temp_2(start_date):
    print("The function is running")
    Start_Date = dt.strptime(start_date, "%Y-%m-%d")
    latest_date = session.query(Measurements.date).order_by(Measurements.date.desc()).first()[0] #Query for the latest date
    format_latest_date = dt.strptime(latest_date,"%Y-%m-%d") # Formatting the date with strptime
    End_Date = format_latest_date
    
    #Collect all the dates between start date and end date
    delta = End_Date - Start_Date
    date_range = []
    for i in range(delta.days + 1):
        date_range.append(Start_Date + timedelta(days=i))
       
    #Converting to stings
    str_date_range = []
    for date in date_range:
        new_date = date.strftime("%Y-%m-%d")
        str_date_range.append(new_date)
       
   #Calculate Average Tempareure , Min and Maximum temperatures within the date range    
    temp_avg = session.query(func.avg(Measurements.tobs))\
              .filter(Measurements.date.in_(str_date_range))[0][0]
    temp_min = session.query(func.min(Measurements.tobs))\
              .filter(Measurements.date.in_(str_date_range))[0][0]
    temp_max = session.query(func.max(Measurements.tobs))\
              .filter(Measurements.date.in_(str_date_range))[0][0]
       
    #Return a json list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    trip_output_dict  = {"Minimum Temperature": temp_min, "Average Temperature":temp_avg, "Maximum Temperature":temp_max} #create a dictionary for our function to return back as a JSON
    return jsonify(trip_output_dict) #return back JSON response


if __name__ == '__main__':
    app.run(debug=True)
