from datastore import DataStore
from fare_data import FareData
from datetime import datetime as dt
import sqlite3,pytz

datastore = DataStore('Bussearch.db')
faredata = FareData()

class Operations:
    def __init__(self):
        pass

    def __repr__(self):
        return 'A parent class to look up database'

    def findDistance(self,bus_services,start,end):
        '''
        Find the distance travelled and the number of bus stops passes by the bus

        Parameter:
        serviceNo: Direct bus that will pass through both start and end bus stop
        start: starting BusStopCode
        end: ending BusStopCode

        Output:
        (distance_btw_bs , no_bs_passes)
        '''
        
        for bus in bus_services:
            if bus['BusStopCode'] == start:
                start_distance = bus['Distance']
                start_StopSequence = bus['StopSequence']
        
        for bus in bus_services:
            if bus['BusStopCode'] == end:
                end_distance = bus['Distance'] 
                end_StopSequence = bus['StopSequence']
        
        distance = end_distance - start_distance
        no_of_bs = end_StopSequence - start_StopSequence
        
        distance = abs(round(distance,3))
        no_of_bs = abs(no_of_bs) 
        
        return distance, no_of_bs

    def findFare(self,category,distance,fareType,paymentType):
        '''
        Find the fare needed for the distance travelled by the bus

        Paramter:
        category: Category of the bus, "EXPRESS" etc.
        distance: Distance travelled by the bus
        fareType: type of traveller, "Student" etc.
        paymentType: Type of payment (ONLY "Card" or "Cash")

        Output:
        The fare needed for the distance travelled
        Example: $0.99
        '''
        # condition for users who try to pay Express bus by cash
        # calculate the bus fare using the paymentType 'Card' instead
        if category == 'EXPRESS' and paymentType =='Cash':
            paymentType = 'Card'
        
        #Get the object that have the necessary fare data
        fare_data = self.openfile(category)
        
        #BinarySearch to find the row with the matching distance in fare_data
        req_row = self.BinarySearch(fare_data,distance)

        #Find the fare using the given fareType and paymentType
        fare = self.__searchfare(req_row,fareType,paymentType)

        return f'${float(fare)/100}'
    
    def findFreq(self,serviceNo,tframe):
        '''
        Find the frequency of the bus arrival 

        Paramter:
        serviceNo: the bus service No.
        tframe: timeframe of the current timing, "AM_Peak_Freq" etc.

        Output:
        Frequency of the bus arrival
        '''

        freq = datastore.searchBsServices('ServiceNo',serviceNo)[0][tframe]

        return freq

    def gettime(self):
        '''
        To get the current time

        Output:
        Current day, current time
        Example:
        "April 25,2021" , "23:59"
        '''
        tz_SG = pytz.timezone('Asia/Singapore')
        now_time = dt.now(tz_SG)
        now_day = dt.today()

        current_time = now_time.strftime("%H:%M")
        current_day = now_day.strftime("%B %d, %Y")
        
        return current_day, current_time

    def gettimeframe(self):
        '''
        Get the timeframe of the current time

        Output:
        "AM_Peak_Freq" etc.
        '''
        current_day, current_time = self.gettime()
        hour = int(current_time[:2])

        if hour >= 6 and hour <= 9:
            tframe = "AM_Peak_Freq"
        elif hour > 9:
            tframe = "AM_Offpeak_Freq"
        elif hour >= 17 and hour <= 19:
            tframe =  "PM_Peak_Freq"
        elif hour > 19:
            tframe = "PM_Offpeak_Freq"

        return tframe
    
    def openfile(self,busType):
        '''
        To get the necessary faredata

        Parameter:
        busType: Type of bus, "EXPRESS" etc.

        Output:
        Necessary faredata in dictionary format
        Example:
        for EXPRESS bus
        {
            'distance': ,
            'cash_fare_per_ride': ,
            'adult_card_fare_per_ride': ,
            'senior_citizen_card_fare_per_ride': ,
            'student_card_fare_per_ride': ,'workfare_transport_concession_card_fare_per_ride': ,'persons_with_disabilities_card_fare_per_ride':
        }
        '''
        if busType == "EXPRESS":
            return faredata.EXPRESS

        elif busType == "FEEDER":
            return faredata.FEEDER

        elif busType == "TRUNK":
            return faredata.TRUNK

        #for bus type "NIGHT RIDER" & "2-TIER FLAT FARE" 
        #use "EXPRESS" fare data
        else:
            return faredata.EXPRESS
    
    def BinarySearch(self,fare_data,distance):
        '''
        Find the row with the matching distance in fare_data

        Parameter:
        fare_data = csv file that has the relevant bus fare data
        distance = distance travelled by the bus

        Output: (*Express bus does not have cash data*)
        {
            'distance':,
            'adult_card_fare_per_ride':,
            'adult_cash_fare_per_ride':,
            'senior_citizen_card_fare_per_ride':,
            'senior_citizen_cash_fare_per_ride':,
            'student_cash_fare_per_ride':,
            'workfare_transport_concession_card_fare_per_ride':,
            'workfare_transport_concession_cash_fare_per_ride':,
            'persons_with_disabilities_card_fare_per_ride':,
            'persons_with_disabilities_cash_fare_per_ride':'
        }
        '''
        start = 0
        end = len(fare_data) - 1
        mid = (start + end) // 2

        while start != end:
            if distance <= float(fare_data[mid]['distance']):
                end = mid
            else:
                start = mid + 1
            
            mid = (start + end) // 2
        
        return fare_data[mid]

    @staticmethod
    def __searchfare(data,fareType,paymentType):
        '''
        Find the amount of fare needed from the one row of fare_data passed in 

        Parameter:
        data: the row in the fare data
        fareType: Type of traveller, "Student" etc.
        paymentType: Type of payment (ONLY "Card" or "Cash")

        Output:
        "0.99"
        '''
        if fareType == 'Adult':
            if paymentType == 'Card':
                fare = data['adult_card_fare_per_ride']
            else:
                fare = data['adult_cash_fare_per_ride']
            
        elif fareType == 'Senior Citizen':
            if paymentType == 'Card':
                fare = data['senior_citizen_card_fare_per_ride']
            else:
                fare = data['senior_citizen_cash_fare_per_ride']
        
        elif fareType == 'Student':
            if paymentType == 'Card':
                fare = data['student_card_fare_per_ride']
            else:
                fare = data['student_cash_fare_per_ride']

        elif fareType == 'WTCC':
            if paymentType == 'Card':
                fare = data['workfare_transport_concession_card_fare_per_ride']
            else:
                fare = data['workfare_transport_concession_cash_fare_per_ride']

        elif fareType == 'PWD':
            if paymentType == 'Card':
                fare = data['persons_with_disabilities_card_fare_per_ride']
            else:
                fare = data['persons_with_disabilities_cash_fare_per_ride']

        return fare


class serviceOps(Operations):
    def __init__(self,serviceNo,direction):

        self.direction = direction
        self.serviceNo = serviceNo.strip()

        data = datastore.searchBsRoutes('ServiceNo',self.serviceNo)
        bus_data = []
        for bus in data:
            if str(bus['Direction']) == self.direction:
                bus_data.append(bus)
        
        self.bus_services = bus_data
    
    def __repr__(self):
        return 'A child class to perform operations for finding path details through bus services'

    def findBusFareDetails(self,start_bscode,end_bscode):
        '''
        Function's input:
            .findBusFareDetails(start_bscode,end_bscode)

        Find the following details:
        1) ServiceNo of the bus
        2) Distance travelled by the bus to reach the end bus stop 
        3) Find the number of bus stops the bus will pass
        4) Depending on the fareType and paymentType, the fare required to travel for the bus service user take
        5) Frequency of the bus services to reach the bus stop
        
        Output in the format of dictionary
        bus_details = 
                    {
                        "ServiceNo":,
                        "start_bscode":,
                        "end_bscode":,
                        "Distance":,
                        "No_of_bs_passes":,
                        "Fare":
                    }
        '''
        bus_details = dict()

        bus_details['ServiceNo'] = self.serviceNo
        bus_details['start_bscode'] = start_bscode
        bus_details['end_bscode'] = end_bscode

        distance, no_of_bs_passes = self.findDistance(self.bus_services,start_bscode,end_bscode)

        bus_details['Distance'] = distance
        bus_details['No_of_bs_passes'] = no_of_bs_passes

        category = datastore.searchBsServices('ServiceNo',self.serviceNo)[0]['Category']
        fare_data = self.findFare(category,distance)

        bus_details['Fare'] = fare_data

        return bus_details

    def findFare(self,category,distance):
        '''
        Find the fare needed for the distance travelled by the bus

        Paramter:
        category: Category of the bus, "EXPRESS" etc.
        distance: Distance travelled by the bus

        Output:
        The fare needed for the distance travelled
        Example: 
        fare = {
            'Adult_card':,
            'Adult_Cash':,
            'Senior_card':,
            'Senior_card':,
            'Student_card':,
            'Student_cash':,
            'WTCC_card':,
            'WTCC_cash':,
            'PWD_card':,
            'PWD_cash':,
        }
        '''

        #Get the object that have the necessary fare data
        fare_data = self.openfile(category)
        
        #BinarySearch to find the row with the matching distance in fare_data
        req_row = self.BinarySearch(fare_data,distance)

        #turn raw data into float data
        fare = self.__translate(req_row,category)

        return fare

    @staticmethod
    def __translate(data,category):
        '''
        *Function specially for finding fare*
        Turn the raw data into float data
        '''
        fare = dict()

        for item in data.values():
            item = float(item)/100

        if category != 'EXPRESS':
            fare['Adult_card'] = f'${data["adult_card_fare_per_ride"]}'
            fare['Adult_cash'] = f'${data["adult_cash_fare_per_ride"]}'

            fare['Senior_card'] = f'${data["senior_citizen_card_fare_per_ride"]}'
            fare['Senior_cash'] = f'${data["senior_citizen_cash_fare_per_ride"]}'

            fare['Student_card'] = f'${data["student_card_fare_per_ride"]}'
            fare['Student_cash'] = f'${data["student_cash_fare_per_ride"]}'

            fare['WTCC_card'] = f'${data["workfare_transport_concession_card_fare_per_ride"]}'
            fare['WTCC_cash'] = f'${data["workfare_transport_concession_cash_fare_per_ride"]}'

            fare['PWD_card'] = f'${data["persons_with_disabilities_card_fare_per_ride"]}'
            fare['PWD_cash'] = f'${data["persons_with_disabilities_cash_fare_per_ride"]}'
        else:
            fare['Adult_card'] = f'${data["adult_card_fare_per_ride"]}'
            fare['Adult_cash'] = '-'

            fare['Senior_card'] = f'${data["senior_citizen_card_fare_per_ride"]}'
            fare['Senior_cash'] = '-'

            fare['Student_card'] = f'${data["student_card_fare_per_ride"]}'
            fare['Student_cash'] = '-'

            fare['WTCC_card'] = f'${data["workfare_transport_concession_card_fare_per_ride"]}'
            fare['WTCC_cash'] = '-'

            fare['PWD_card'] = f'${data["persons_with_disabilities_card_fare_per_ride"]}'
            fare['PWD_cash'] = '-'


        return fare

class routeOps(Operations):
    def __init__(self):
        pass

    def __repr__(self):
        return 'A child class to perform operations for finding path details through bus stops'

    def findBusRouteDetails(self,start,end,fareType,paymentType):
        '''
        Function's input:
            .findBusRouteDetails(start_busstops,end_busstops,fareType,paymentType)

        Find the following details:
        1) ServiceNo of the bus
        2) Distance travelled by the bus to reach the end bus stop 
        3) Find the number of bus stops the bus will pass
        4) Depending on the fareType and paymentType, the fare required to travel for the bus service user take
        5) Frequency of the bus services to reach the bus stop
        
        Output in the format of dictionary
        directBsService = 
                    {
                        "ServiceNo"
                        "Distance":
                        "No_of_bs_pass":
                        "Fare":
                        "Freq":
                    }
        '''

        #Find the direct bus service that passes both starting and ending bus stops
        directBsService = self.__findDirectBusServices(start,end)
        #get the timeframe for later use
        current_tframe = self.gettimeframe()

        if directBsService == []:
            return directBsService

        else:
            for bus in directBsService:
            #find the distance travelled and number of bus stop pass by the bus services
                distance_btw_bs, no_of_bs_passes = self.findDistance(bus['ServiceNo'],start,end)

                bus['Distance'] = distance_btw_bs
                bus['No_of_bs_passes'] = no_of_bs_passes

            #find the fare needed for each bus service
                category = datastore.searchBsServices('ServiceNo',bus['ServiceNo'])[0]['Category']
                distance = bus['Distance']

                bus['Fare'] = self.findFare(category,distance,fareType,paymentType)      

            #find the frequency of the bus arrival
                freq = self.findFreq(bus['ServiceNo'],current_tframe)

                bus['Freq'] = freq

            #sort the list in an ascending order of distance travlled by the bus
            directBsService = self.__quickSort(directBsService)

            return directBsService

    def __findDirectBusServices(self,start,end):
        '''
        Find direct bus services that pass both start and end bus stop

        Parameter:
        start: starting BusStopCode
        end: ending BusStopCode

        Output: 
        if there is no direct bus: listofmatch = None
        if there is direct bus: listofmatch = {'ServiceNo': value}         
        '''
        conn = datastore.get_conn()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # first time to find the bus stop that pass through both points in "direction" = 1
        cur.execute('''
                    SELECT ServiceNo,StopSequence FROM "Bus_routes"
                    WHERE 
                    "Direction" = 1 AND "BusStopCode" = (?)
                    ''',(start,))

        start_data = cur.fetchall()
        
        #find the bus services that pass end point
        cur.execute('''
                    SELECT ServiceNo,StopSequence FROM "Bus_routes"
                    WHERE 
                    "Direction" = 1 AND "BusStopCode" = (?)
                    ''',(end,))

        end_data = cur.fetchall()

        listofmatch = []
        #find the matching bus services that pass both start and end point 
        if start_data != [] and end_data != []:
            for a in range(len(start_data)):
                start_serviceNo = start_data[a]['ServiceNo']
                start_stopSequence = start_data[a]['StopSequence']

                for a in range(len(end_data)):
                    if start_serviceNo == end_data[a]['ServiceNo']:
                        if start_stopSequence < end_data[a]['StopSequence']:
                            match = dict()
                            match['ServiceNo'] = start_serviceNo
                            listofmatch.append(match)

            #repeat second time to find the bus stop that pass through both points in "direction" = 2
            cur.execute('''
                        SELECT ServiceNo,StopSequence FROM "Bus_routes"
                        WHERE 
                        "Direction" = 2 AND "BusStopCode" = (?)
                        ''',(start,))

            start_data = cur.fetchall()
            
            #find the bus services that pass end point
            cur.execute('''
                        SELECT ServiceNo,StopSequence FROM "Bus_routes"
                        WHERE 
                        "Direction" = 2 AND "BusStopCode" = (?)
                        ''',(end,))

            end_data = cur.fetchall()
 
            if start_data == [] or end_data == []:
                return listofmatch
            else:
            #find the matching bus services that pass both start and end point 
                for a in range(len(start_data)):
                    start_serviceNo = start_data[a]['ServiceNo']
                    start_stopSequence = start_data[a]['StopSequence']
                    for a in range(len(end_data)):
                        if start_serviceNo == end_data[a]['ServiceNo']:
                            if start_stopSequence < end_data[a]['StopSequence']:
                                match = dict()
                                match['ServiceNo'] = start_serviceNo
                                listofmatch.append(match)

                return listofmatch
        else:
            return listofmatch
    
    def findDistance(self,serviceNo,start,end):
        '''
        Find the distance travelled and the number of bus stops passes by the bus

        Parameter:
        serviceNo: Direct bus that will pass through both start and end bus stop
        start: starting BusStopCode
        end: ending BusStopCode

        Output:
        (distance_btw_bs , no_bs_passes)
        '''
        conn = datastore.get_conn()
        cur = conn.cursor()
        
        cur.execute('''
                    SELECT Distance,StopSequence FROM "Bus_routes"
                    WHERE ("ServiceNo","BusStopCode") = (?,?)
                    ''',(serviceNo,start,))
        start_data = cur.fetchall()

        cur.execute('''
                    SELECT Distance, StopSequence FROM "Bus_routes"
                    WHERE ("ServiceNo","BusStopCode") = (?,?)
                    ''',(serviceNo,end,))
        end_data = cur.fetchall()

        start_distance,start_StopSequence, = start_data[0]
        end_distance,end_StopSequence, = end_data[0]
        
        # for abnormally which the bus route is a loop service
        if len(end_data) >1:
            count = 1
            while start_StopSequence > end_StopSequence:
                end_distance,end_StopSequence, = end_data[count]
                count += 1
        
        distance = end_distance - start_distance
        no_of_bs = end_StopSequence - start_StopSequence

        distance = abs(round(distance,3))
        no_of_bs = abs(no_of_bs)

        return distance, no_of_bs

    def __quickSort(self,listofdirectbs):
        '''
        Sort the listofdirectbs in an ascending order of distance travelled

        Output:
        listofdirectbs with an order of ascending distance
        '''
        if len(listofdirectbs) > 1:
            ltepivot = []
            gtpivot = []
            pivot = listofdirectbs[len(listofdirectbs) - 1]['Distance']

            for a in range(len(listofdirectbs)- 1):
                if listofdirectbs[a]['Distance'] > pivot:
                    gtpivot.append(listofdirectbs[a])
                else:
                    ltepivot.append(listofdirectbs[a])

            left = self.__quickSort(ltepivot)
            right = self.__quickSort(gtpivot)

            sorted_array = left + [listofdirectbs[len(listofdirectbs) - 1]] + right

            return sorted_array
        else:
            return listofdirectbs

    
