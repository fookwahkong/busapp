from flask import Flask, render_template, request
from datastore import DataStore
from classes_ import serviceOps,routeOps
from interface import WebInterface
import json,sqlite3

app = Flask("Capstone Project")
URI = 'Bussearch.db'
rOps = routeOps()
datastore = DataStore(URI)
ui = WebInterface()

# datastore.delete()
# datastore.save()

app = Flask(__name__)

@app.route('/', methods=['GET'])
def main():
    ui.bus_stops = datastore.load('Bus_stops')
    ui.bus_services = datastore.searchBsServices('Direction',1)
    
    return render_template('main.html', ui=ui)

#FEATURE1: DISPLAY THE BUS ROUTE DETAILS
@app.route('/search',methods=["POST"])
def search():
    start_bscode = request.form['start_bscode']
    end_bscode = request.form['end_bscode']
    fareType = request.form['fareType']
    paymentType = request.form['paymentType']

    if fareType == '-':
        fareType = 'Adult' #fareType by default is "Adult"
    if paymentType == '-':
        paymentType = 'Card' #paymentType by default is "Card"

    ui.fareType = fareType
    ui.paymentType = paymentType
    ui.time , ui.day = rOps.gettime()

    ui.result = rOps.findBusRouteDetails(start_bscode,end_bscode,fareType,paymentType)

    if ui.result == []:
        ui.bus_routes = datastore.searchBsRoutes('BusStopCode',start_bscode)
        
        return render_template('path_finder.html',ui=ui)
    else:
        return render_template('path_finder.html',ui=ui)


#FEATURE 2: DISPLAY THE DETAILS FOR THE BUS SERVICES
@app.route('/bus_services',methods=['POST'])
def bus_services():
    serviceNo = request.form['serviceNo']
    
    ui.bus_services = datastore.searchBsServices('ServiceNo',serviceNo)
    ui.bus_routes = datastore.searchBsRoutes('ServiceNo',serviceNo)
    
    length = len(ui.bus_services)

    return render_template('bus_services.html',length=length,ui=ui)

@app.route('/fare_info',methods=['POST'])
def fare_info():
    serviceNo = request.form['serviceNo']
    direction = request.form['Direction']
    start_bscode = request.form['start_bscode']
    end_bscode = request.form['end_bscode']
    
    sOps = serviceOps(serviceNo,direction)
    ui.result = sOps.findBusFareDetails(start_bscode,end_bscode) 
    
    return render_template('fare_results.html',ui=ui)

@app.route('/debug', methods=['GET'])
def debug():
    data = []
    bus_stops = datastore.load("Bus_stops")
    bus_stops1 = datastore.load("Bus_stops")
    fareType = "Adult"
    paymentType = "Card"
    print(bus_stops[0]['BusStopCode'])
    for start in bus_stops[:1]:
        start_bscode = start['BusStopCode']
        print(f"start: {start_bscode}")

        for a in range(len(bus_stops1)):
            end_bscode = bus_stops1[a]['BusStopCode']
            print(f"end: {end_bscode}")
        
            result = routeOps.findBusRouteDetails(start_bscode,end_bscode,fareType,paymentType)
            data.append(result)

    return render_template('debug.html',data=data)


app.run('0.0.0.0')