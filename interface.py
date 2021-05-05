class WebInterface:
    '''
    A class that provides interface for the HTML webpage
    '''
    def __init__(self):
        self.bus_routes = None
        self.bus_services = None
        self.bus_stops = None
        self.fareType = None
        self.paymentType = None
        self.result = None
        self.time = None
        self.day = None