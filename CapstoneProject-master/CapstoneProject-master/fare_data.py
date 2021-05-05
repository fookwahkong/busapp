import csv

class FareData:
    '''
    A class to store the fare data
    '''
    def __init__(self):
        self.EXPRESS = self.set("EXPRESS")
        self.TRUNK = self.set("TRUNK")
        self.FEEDER = self.set("FEEDER")

    def set(self,busType):
        '''
        Deserialise fare_data file into fare_data objects
        '''
        if busType == "EXPRESS":
            with open('fare_data/fares-for-express.csv','r') as f:
                file = csv.DictReader(f)
                fare_data = []
                for line in file:
                    fare_data.append(line)
                return fare_data

        elif busType == "FEEDER":
            with open('fare_data/fares-for-feeder.csv','r') as f:
                file = csv.DictReader(f)
                fare_data = []
                for line in file:
                    fare_data.append(line)
                return fare_data

        elif busType == "TRUNK":
            with open('fare_data/fares-for-trunk.csv','r') as f:
                file = csv.DictReader(f)
                fare_data = []
                for line in file:
                    fare_data.append(line)
                return fare_data

        #for bus type "NIGHT RIDER" & "2-TIER FLAT FARE" 
        #use "EXPRESS" fare data
        else:
            with open('fare_data/fares-for-express.csv','r') as f:
                file = csv.DictReader(f)
                fare_data = []
                for line in file:
                    fare_data.append(line)
                return fare_data