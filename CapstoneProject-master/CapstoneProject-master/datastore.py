import sqlite3, json

SQL = {
    'bus_services_init' : 
                    '''
                    CREATE TABLE IF NOT EXISTS "Bus_services"
                    (
                        "ServiceNo" TEXT,
                        "Operator" TEXT,
                        "Direction" INTEGER,
                        "Category" TEXT,
                        "OriginCode" TEXT,
                        "DestinationCode" TEXT,
                        "AM_Peak_Freq" TEXT,
                        "AM_Offpeak_Freq" TEXT,
                        "PM_Peak_Freq" TEXT,
                        "PM_Offpeak_Freq" TEXT,
                        "LoopDesc" TEXT,

                        PRIMARY KEY("ServiceNo","Direction"),
                        FOREIGN KEY("OriginCode") REFERENCES "Bus_stops"("BusStopCode"),
                        FOREIGN KEY("DestinationCode") REFERENCES "Bus_stops"("BusStopCode")
                    );
                    ''',
    'bus_routes_init' :
                    '''
                    CREATE TABLE IF NOT EXISTS "Bus_routes"
                    (
                        "ServiceNo" TEXT,
                        "Operator" TEXT,
                        "Direction" INTEGER,
                        "StopSequence" INTEGER,
                        "BusStopCode" TEXT,
                        "Distance" INTEGER,
                        "WD_FirstBus" TEXT,
                        "WD_LastBus" TEXT,
                        "SAT_FirstBus" TEXT,
                        "SAT_LastBus" TEXT,
                        "SUN_FirstBus" TEXT,
                        "SUN_LastBus" TEXT,

                        PRIMARY KEY("ServiceNo","Direction","StopSequence"),
                        FOREIGN KEY("BusStopCode") REFERENCES "Bus_stops"("BusStopCode")
                        FOREIGN KEY("ServiceNo") REFERENCES "Bus_services"("ServiceNo")
                    );
                    ''',

    'bus_stops_init' :
                    '''
                    CREATE TABLE IF NOT EXISTS "Bus_stops"
                    (
                        "BusStopCode" TEXT,
                        "RoadName" TEXT,
                        "Description" TEXT,
                        "Latitude" INTEGER,
                        "Longitude" INTEGER,

                        PRIMARY KEY("BusStopCode")
                    );
                    ''',
    
    'bus_services_update':
                        '''
                        INSERT INTO "Bus_services"
                                    (
                                        "ServiceNo",
                                        "Operator",
                                        "Direction",
                                        "Category",
                                        "OriginCode",
                                        "DestinationCode",
                                        "AM_Peak_Freq",
                                        "AM_Offpeak_Freq",
                                        "PM_Peak_Freq",
                                        "PM_Offpeak_Freq",
                                        "LoopDesc"
                                    )
                        VALUES
                                    (
                                        :ServiceNo,
                                        :Operator,
                                        :Direction,
                                        :Category,
                                        :OriginCode,
                                        :DestinationCode,
                                        :AM_Peak_Freq,
                                        :AM_Offpeak_Freq,
                                        :PM_Peak_Freq,
                                        :PM_Offpeak_Freq,
                                        :LoopDesc
                                    );
                        ''',
    'bus_routes_update' :
                    '''
                    INSERT INTO "Bus_routes"
                                    (
                                        "ServiceNo",
                                        "Operator",
                                        "Direction",
                                        "StopSequence",
                                        "BusStopCode",
                                        "Distance",
                                        "WD_FirstBus",
                                        "WD_LastBus",
                                        "SAT_FirstBus",
                                        "SAT_LastBus",
                                        "SUN_FirstBus",
                                        "SUN_LastBus"
                                    )
                    VALUES          
                                    (
                                        :ServiceNo,
                                        :Operator,
                                        :Direction,
                                        :StopSequence,
                                        :BusStopCode,
                                        :Distance,
                                        :WD_FirstBus,
                                        :WD_LastBus,
                                        :SAT_FirstBus,
                                        :SAT_LastBus,
                                        :SUN_FirstBus,
                                        :SUN_LastBus
                                    );
                    ''',

    'bus_stops_update' : 
                    '''
                    INSERT INTO "Bus_stops" 
                                    (
                                        "BusStopCode",
                                        "RoadName",
                                        "Description",
                                        "Latitude",
                                        "Longitude"
                                    )
                    VALUES
                                    (
                                        :BusStopCode,
                                        :RoadName,
                                        :Description,
                                        :Latitude,
                                        :Longitude
                                    );
                    ''',
    'bus_services_search' : 
                        '''
                        SELECT (?) FROM "Bus_services";
                        ''',
    'bus_routes_search' : '''''',
    'bus_stops_search' : ''''''

    }

class DataStore:
    '''
    A class to provide interaction between SQL database and python program
    '''
    def __init__(self,uri):
        self.uri = uri

    def get_conn(self):
        '''
        - Get connection to the SQL database
        - Create and return an sqlite3 connection object.
        '''
        conn = sqlite3.connect(self.uri)
        return conn

    def load(self,TableToImport):
        '''
        - To get data from the database
        - Deserialise data from database to dictionary object
        '''
        conn = self.get_conn()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        if TableToImport == 'Bus_routes':
            cur.execute('''
                        SELECT * FROM "Bus_routes";
                        ''')
            data = cur.fetchall()
        
        elif TableToImport == 'Bus_services':
            cur.execute('''
                        SELECT * FROM "Bus_services";
                        ''')
            data = cur.fetchall()
        
        elif TableToImport == 'Bus_stops':
            cur.execute('''
                        SELECT * FROM "Bus_stops";
                        ''')
            data = cur.fetchall()
        
        conn.commit()
        conn.close()
        return data

    def save(self):
        '''
        - To save/update data into the database
        - Serialise data from json file to database
        '''
        #import json file into dictionary object
        with open('bus_services.json','r') as f:
            bus_services = json.load(f)
        
        with open('bus_routes.json','r') as f:
            bus_routes = json.load(f)

        with open('bus_stops.json','r') as f:
            bus_stops = json.load(f)

        conn = self.get_conn()
        cur = conn.cursor()

        #initiate the table 
        cur.execute(SQL['bus_routes_init'])
        cur.execute(SQL['bus_stops_init'])
        cur.execute(SQL['bus_services_init'])

        #insert the data into the table
        for row in bus_routes:
            cur.execute(SQL['bus_routes_update'],row)
        for row in bus_stops:
            cur.execute(SQL['bus_stops_update'],row)
        for row in bus_services:
            cur.execute(SQL['bus_services_update'],row)
            
        conn.commit()
        conn.close()

    def delete(self):
        '''
        To delete all the tables and data containing in the table
        '''
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute('''DELETE FROM "Bus_services" ''')
        cur.execute('''DELETE FROM "Bus_routes" ''')
        cur.execute('''DELETE FROM "Bus_stops" ''')

        conn.commit()
        conn.close()

    def searchBsRoutes(self,ItemToMatch,ValueToMatch):
        '''
        Search with a criteria for the data in table 'Bus_routes'

        Parameter:
        ItemToMatch: Fieldname in the table
        ValueToMatch: Value to match the data under the fieldname

        Output: Rows that match the value passed in ( in dictionary form )   
        '''
        conn = self.get_conn()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        if ItemToMatch == 'BusStopCode':
            cur.execute('''
                        SELECT * FROM "Bus_routes"
                        WHERE "BusStopCode" = (?);
                        ''',(ValueToMatch,))
            result = cur.fetchall()

        elif ItemToMatch == 'ServiceNo':
            cur.execute('''
                        SELECT * FROM "Bus_routes"
                        INNER JOIN "Bus_stops" 
                        ON "Bus_routes"."BusStopCode" 
                        = "Bus_stops"."BusStopCode"
                        WHERE "ServiceNo" = (?);
                        ''',(ValueToMatch,))
            result = cur.fetchall()
            
        conn.commit()
        conn.close()

        return result

    def searchBsServices(self,ItemToMatch,ValueToMatch):
        '''
        Search for the data in table 'Bus_servcies'

        Parameter:
        ItemToMatch: Fieldname in the table
        ValueToMatch: Value to match the data under the fieldname

        Output: Rows that match the value passed in ( in dictionary form )   
        '''
        conn = self.get_conn()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        if ItemToMatch == 'Direction':
            cur.execute('''
                    SELECT * FROM "Bus_services"
                    WHERE "Direction" = (?);
                    ''',(ValueToMatch,))
            result = cur.fetchall()

        elif ItemToMatch == 'ServiceNo':
            cur.execute('''
                SELECT * FROM "Bus_services"
                WHERE "ServiceNo" = (?)
                ''',(ValueToMatch,))
            result = cur.fetchall()

        conn.commit()
        conn.close()

        return result