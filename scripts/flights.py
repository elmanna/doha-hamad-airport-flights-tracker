import requests
import json
import datetime
import time
import pytz
import threading
from collections import Counter


class FlightsManager():
    """
    A class to manage flight data retrieval and analysis.

    Attributes:
        queue: A queue for storing departure flight data.
        queue2: A queue for storing arrival flight data.
        depBusiestHoursQueue: A queue for storing busiest hours for departures.
        arrBusiestHoursQueue: A queue for storing busiest hours for arrivals.
        FLIGHTS_DATA_LIMIT: The limit for the number of flight records to fetch.
        SESSION: A session for making HTTP requests.
        lanCode: The language code for data retrieval.
        HAP_URL: The base URL for flight status data.
        ARRIVAL_PATH: The path for arrival flight data.
        DEPARTURE_PATH: The path for departure flight data.
        DEPARTURES_DATA: The URL for departure flights data.
        ARRIVAL_DATA: The URL for arrival flights data.

    Methods:
        __get_top_relevant__(data): Extracts the top 5 relevant airlines from flight data.
        __update_arrival_flight__(data): Updates arrival flight data.
        __update_departured_flight__(data): Updates departure flight data.
        __analyze_flights__(data, type): Analyzes flight data and updates the respective data attributes.
        __get_start_and_end__(): Gets the start and end times for flight data retrieval.
        __get_flights_by_type__(type, time): Retrieves flight data based on type and time.
        __get_Departures__(): Continuously retrieves and analyzes departure flight data.
        __get_Arrivals__(): Continuously retrieves and analyzes arrival flight data.
        __main_loop__(): Starts threads for departure and arrival flight data retrieval.
    """
     
    def __init__(self, queue, queue2, depBusiestHoursQueue, arrBusiestHoursQueue) -> None:
        """
        Initializes a FlightsManager instance.

        Args:
            queue: A queue for storing departure flight data.
            queue2: A queue for storing arrival flight data.
            depBusiestHoursQueue: A queue for storing busiest hours for departures.
            arrBusiestHoursQueue: A queue for storing busiest hours for arrivals.
        """

        self.departure_flights_keys     = []
        self.departure_flights_data     = dict()
        self.arrival_flights_keys       = []
        self.arrival_flights_data       = dict()
        self.queue                      = queue
        self.queue2                     = queue2
        self.depBusiestHoursQueue       = depBusiestHoursQueue
        self.arrBusiestHoursQueue       = arrBusiestHoursQueue
        self.FLIGHTS_DATA_LIMIT         = 3500
        self.SESSION                    = requests.session()
        self.lanCode                    = "en"
        self.HAP_URL                    = "https://dohahamadairport.com/airlines/flight-status?"
        self.ARRIVAL_PATH               = "type=arrivals&day=today&airline=all&locate=all&search_key="
        self.DEPARTURE_PATH             = "type=departures&day=today&airline=all&locate=all&search_key="
        self.DEPARTURES_DATA            = "https://dohahamadairport.com/webservices/fids/departures?"
        self.ARRIVAL_DATA               = "https://dohahamadairport.com/webservices/fids/arrivals?"

    def __get_top_relevant__(self, data):
        airlines = []
        airCount = dict()

        for line in data:
            if line["lang"]["en"]["airlineName"] not in airlines:
                airlineName = line["lang"]["en"]["airlineName"]
                airlines.append(airlineName)
                airCount[airlineName] = 1
            else:
                airlineName = line["lang"]["en"]["airlineName"]
                airCount[airlineName] += 1
        
        top_5_airlines = dict(sorted(airCount.items(), key=lambda item: item[1], reverse=True)[:5])

        return top_5_airlines.keys()
        


    def __update_arrival_flight__(self, data):
        """
        Updates arrival flight data based on incoming data.

        Args:
            data: New arrival flight data.
        """

        self.arrival_flights_keys   = []
        self.arrival_flights_data   = dict()
        busiest_hours               = []

        self.arrival_flights_keys   = self.__get_top_relevant__(data)
        

        try:
            for airlineName in self.arrival_flights_keys:
                for airtrip in data:
                    if(airlineName == airtrip["lang"]["en"]["airlineName"]):
                        if(airlineName not in self.arrival_flights_data):
                            self.arrival_flights_data[airlineName]                     = dict()
                            self.arrival_flights_data[airlineName]                     = airtrip
                            self.arrival_flights_data[airlineName]["recentArri"]       = dict()
                            self.arrival_flights_data[airlineName]["flightsCountered"] = 1
                        else:
                            if(airtrip["actualTimeOfArr"]):
                                busiest_hours.append(int(airtrip["actualTimeOfArr"]))

                            if self.arrival_flights_data[airlineName]["flightsCountered"]:
                                self.arrival_flights_data[airlineName]["flightsCountered"] += 1
                            else:
                                self.arrival_flights_data[airlineName]["flightsCountered"] = 1

                            flightsCountered = self.arrival_flights_data[airlineName]["flightsCountered"]
                            recentArri       = self.arrival_flights_data[airlineName]["recentArri"]
                            if(int(airtrip["scheduledTime"]) > int(self.arrival_flights_data[airlineName]["scheduledTime"])):
                                self.arrival_flights_data[airlineName]                     = dict()
                                self.arrival_flights_data[airlineName]                     = airtrip
                                self.arrival_flights_data[airlineName]["flightsCountered"] = flightsCountered
                                self.arrival_flights_data[airlineName]["recentArri"]       = recentArri

                            if(airtrip["actualTimeOfArr"]):
                                if(self.arrival_flights_data[airlineName]["actualTimeOfArr"] != None):
                                    if(int(self.arrival_flights_data[airlineName]["actualTimeOfArr"]) > int(airtrip["actualTimeOfArr"])):
                                        self.arrival_flights_data[airlineName]["recentArri"] = self.arrival_flights_data[airlineName]
                                    else:
                                        self.arrival_flights_data[airlineName]["recentArri"] = airtrip
                                else:
                                    self.arrival_flights_data[airlineName]["recentArri"] = airtrip


                """
                pull out (Hour) from airflights (timestamps)
                to determine busiest hours in the day
                """
                busiest_hours_temp = []
                for timestamp in busiest_hours:
                    datetimeObj = datetime.datetime.fromtimestamp(timestamp)
                    hour        = datetimeObj.hour
                    busiest_hours_temp.append(hour)
                
                # Count the occurrences of each hour
                hour_counts = Counter(busiest_hours_temp)

                # Create a list of (hour, count) tuples
                hour_count_tuples = [(hour, count) for hour, count in hour_counts.items()]

                # Sort the list in descending order based on count
                hour_count_tuples.sort(key=lambda x: x[1], reverse=True)

                """ 
                    Extract the 24 most frequent hours 
                    Because a day spans from 12:00 AM (midnight) to the following day at 12:00 AM
                    which equals 24
                """
                top_busiest_hours = [hour for hour, _ in hour_count_tuples[:24]]

                self.arrBusiestHoursQueue.put(top_busiest_hours)
                self.queue2.put(self.arrival_flights_data)
        except Exception as e:
            print("arrival_flights_data")
            print(e)

    def __update_departured_flight__(self, data):
        """
        Updates departure flight data based on incoming data.

        Args:
            data: New departure flight data.
        """

        self.departure_flights_keys = []
        self.departure_flights_data = dict()
        busiest_hours               = []


        self.departure_flights_keys = self.__get_top_relevant__(data)

        try:
            for airlineName in self.departure_flights_keys:
                for airtrip in data:
                    if(airlineName == airtrip["lang"]["en"]["airlineName"]):
                        if(airlineName not in self.departure_flights_data):
                            self.departure_flights_data[airlineName]                     = dict()
                            self.departure_flights_data[airlineName]                     = airtrip
                            self.departure_flights_data[airlineName]["recentDep"]        = dict()
                            self.departure_flights_data[airlineName]["flightsCountered"] = 1
                        else:
                            if(airtrip["actualTimeOfDep"]):
                                busiest_hours.append(int(airtrip["actualTimeOfDep"]))

                            if self.departure_flights_data[airlineName]["flightsCountered"]:
                                self.departure_flights_data[airlineName]["flightsCountered"] += 1
                            else:
                                self.departure_flights_data[airlineName]["flightsCountered"] = 1
                            
                            flightsCountered = self.departure_flights_data[airlineName]["flightsCountered"]
                            recentDep        = self.departure_flights_data[airlineName]["recentDep"]
                            if(int(airtrip["scheduledTime"]) > int(self.departure_flights_data[airlineName]["scheduledTime"])):
                                self.departure_flights_data[airlineName]                     = dict()
                                self.departure_flights_data[airlineName]                     = airtrip
                                self.departure_flights_data[airlineName]["flightsCountered"] = flightsCountered
                                self.departure_flights_data[airlineName]["recentDep"]        = recentDep

                            if(airtrip["actualTimeOfDep"]):
                                if(self.departure_flights_data[airlineName]["actualTimeOfDep"] != None):
                                    if(int(self.departure_flights_data[airlineName]["actualTimeOfDep"]) > int(airtrip["actualTimeOfDep"])):
                                        self.departure_flights_data[airlineName]["recentDep"] = self.departure_flights_data[airlineName]
                                    else:
                                        self.departure_flights_data[airlineName]["recentDep"] = airtrip
                                else:
                                    self.departure_flights_data[airlineName]["recentDep"] = airtrip

                
                """
                pull out (Hour) from airflights (timestamps)
                to determine busiest hours in the day
                """
                busiest_hours_temp = []
                for timestamp in busiest_hours:
                    datetimeObj = datetime.datetime.fromtimestamp(timestamp)
                    hour        = datetimeObj.hour
                    busiest_hours_temp.append(hour)
                
                # Count the occurrences of each hour
                hour_counts = Counter(busiest_hours_temp)

                # Create a list of (hour, count) tuples
                hour_count_tuples = [(hour, count) for hour, count in hour_counts.items()]

                # Sort the list in descending order based on count
                hour_count_tuples.sort(key=lambda x: x[1], reverse=True)

                """ 
                    Extract the 24 most frequent hours 
                    Because a day spans from 12:00 AM (midnight) to the following day at 12:00 AM
                    which equals 24
                """
                top_busiest_hours = [hour for hour, _ in hour_count_tuples[:24]]

                self.depBusiestHoursQueue.put(top_busiest_hours)
                self.queue.put(self.departure_flights_data)
        except Exception as e:
            print("departure_flights_data")
            print(e)

       


    def __analyze_flights__(self, data, type):
        """
        Analyzes flight data and updates the respective data attributes.

        Args:
            data: Flight data to analyze.
            type: Type of flight data, either "depart" or "arrival".
        """

        data = data["flights"]
        if(type == "depart"):            
            self.__update_departured_flight__(data)
        else:
            self.__update_arrival_flight__(data)

    def __get_start_and_end__(self):

        """
        Gets the start and end times for flight data retrieval.

        Returns:
            Start and end times as UNIX timestamps.
        """

        tz    = pytz.timezone('Asia/Qatar')
        today = datetime.datetime.now(tz=tz)
        # one_month_ago = today - datetime.timedelta(days=30)
        start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end   = start + datetime.timedelta(1)

        # one_month_ago = int(round(datetime.datetime.timestamp(one_month_ago))) * 1000
        start         = int(round(datetime.datetime.timestamp(start))) * 1000
        end           = int(round(datetime.datetime.timestamp(end))) * 1000

        return start, end

    def __get_flights_by_type__(self, type, time= "t=" + str(int(round(time.time() * 1000)))):
        """
        Retrieves flight data based on type and time.

        Args:
            type: Type of flight data, either "depart" or "arrival".
            time: Time parameter for the data request.

        Returns:
            Retrieved flight data.
        """

        data      = None
        response  = None

        startTime, endTime = self.__get_start_and_end__() #indicate start & end time limit to search for flights

        payload = {
            "limit": self.FLIGHTS_DATA_LIMIT,
            "startTime": startTime,
            "endTime": endTime
        }

        payload = json.dumps(payload)


        try:
            if(type == "depart"):
                response = self.SESSION.post(url=self.DEPARTURES_DATA + time, data=payload)
            else:
                response = self.SESSION.post(url=self.ARRIVAL_DATA + time, data=payload)
        except Exception as e:
            print("Error -> " + e) 
        data = response.json()

        return data
    
    def __get_Departures__(self):
        """Continuously retrieves and analyzes departure flight data."""

        data = self.__get_flights_by_type__("depart")
        self.__analyze_flights__(data, "depart")
        time.sleep(10)
        self.__get_Departures__()
    
    def __get_Arrivals__(self):
        """Continuously retrieves and analyzes arrival flight data."""

        data = self.__get_flights_by_type__("arrival")
        self.__analyze_flights__(data, "arrival")
        time.sleep(10)
        self.__get_Arrivals__()

    def __main_loop__(self):
        """Starts threads for departure and arrival flight data retrieval."""

        departures_thread = threading.Thread(target=self.__get_Departures__)
        departures_thread.start()

        arrivals_thread = threading.Thread(target=self.__get_Arrivals__)
        arrivals_thread.start()

def getFlightsData(queue, queue2, depBusiestHoursQueue, arrBusiestHoursQueue):
    """
    Function to start the FlightsManager and retrieve flight data.

    Args:
        queue: A queue for storing departure flight data.
        queue2: A queue for storing arrival flight data.
        depBusiestHoursQueue: A queue for storing busiest hours for departures.
        arrBusiestHoursQueue: A queue for storing busiest hours for arrivals.
    """
     
    HLF = FlightsManager(queue, queue2, depBusiestHoursQueue, arrBusiestHoursQueue)
    HLF.__main_loop__()