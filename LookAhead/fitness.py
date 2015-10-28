# -*- coding: utf-8 -*-
"""
Copyright 2015 Ericsson AB

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.

"""
import itertools
import unittest
from dbConnection import DB
from operator import itemgetter
from datetime import datetime
from datetime import timedelta
from datetime import date


class Fitness():

    # Main [class] variables
    diffMinutes = 0
    formatString = '%d-%m-%Y %H:%M'
    formatTime = '%H:%M'
    secondMinute = 60.0
    firstMinute = "00:00"
    lastMinute = "23:59"
    requests = []
    routes = []
    request = []
    requestIndex = []
    yesterday = date.today() - timedelta(7)

# A decorator is a function that can accept another function as
# a parameter to be able to modify or extend it
    def __init__(self):
        self.runOnce()

    def decorator(afunction):
        # A wrapper function is used to wrap functionalites you want around the original function
        def wrapper(*args):
            # Checks whether or not the original function as been executed once
            if not wrapper.has_run:
                wrapper.has_run = True
                return afunction(*args)
            else:
                pass

        wrapper.has_run = False
        return wrapper

    @decorator
    def runOnce(self):
        db = DB()
        #request = []
        Fitness.requests, Fitness.routes = db.getRequestsFromDB()
        #self.routes[:] = self.routes[0][1]
        #print self.routes
        #print Fitness.routes[0][1]
        # DB calls can ve avoided by querying the whole Request Collection for a particular day

        # Replace the dates here from yesterday's date
        #yesterday = date.today() - timedelta(3)


        # The result here should be added into a class variable: the order is by hour, minute and initialBusStop
        Fitness.request = db.getTravelRequestSummary(datetime.combine(Fitness.yesterday, datetime.strptime(Fitness.firstMinute, Fitness.formatTime).time()),
                                                      datetime.combine(Fitness.yesterday, datetime.strptime(Fitness.lastMinute, Fitness.formatTime).time()))
        self.createRequestIndex(Fitness.request)       

    def timeDiff(self, time1, time2):
        ''' Evaluates the difference between two times.

        Args: time1 and time2 in datetime format, time1 > time2
        Returns: the timedelta between time1 and time2.
        '''
        return datetime.strptime(time1, Fitness.formatTime) - datetime.strptime(time2, Fitness.formatTime)

    def getMinutes(self, td):
        return (td.seconds//Fitness.secondMinute) % Fitness.secondMinute

    def getNumberOfRequests(self, tripStartTime, lineNumber=2):
        ''' find the total number of requests that can be served by the trip for all requests with startBusStop along the
        bus line. For these requests, find the maximum number of requests in transit

        @param: tripStartTime - departure time for this trip
        @return maximum number of requests between two stops in the trip
        '''
        self.expectedTimes = {}
        self.stopsCount = {}
        self.reqGroup = []
        for i, item in enumerate(self.routes):
            if item[2] == 2:
                self.busStops = [[i[0], i[1]] for i in self.routes[i][1]]
                self.expTime = tripStartTime;
                for i, stop in enumerate(self.busStops):
                    self.expectedTimes[stop[0]] = self.expTime.time()
                    self.expTime = self.expTime + timedelta(minutes=stop[1])
                    self.stopsCount[stop[0]] = 0

        for req in self.requests:
            if req[1] in self.expectedTimes:
                if req[0].time() < self.expectedTimes[req[1]]:
                    self.reqGroup.append(req)
                    self.stopsCount[req[1]] += 1
                    self.stopsCount[req[2]] -= 1

        #print "sum of requests ", sum(self.stopsCount.itervalues())
        #print "Max request count", self.stopsCount[max(self.stopsCount, key = self.stopsCount.get)]
        return self.stopsCount[max(self.stopsCount, key = self.stopsCount.get)]

    def createRequestIndex(self, request):
        minute = 0
        for i in range(len(request)):
            if request[i]["minute"] != minute or i == 0:
                Fitness.requestIndex.append([request[i]["hour"], request[i]["minute"], i])
                minute = request[i]["minute"]

    def searchRequestIndex(self, index, initialHour, initialMinute, finalHour, finalMinute):
        result = []
        for i in range(len(index)):
            if index[i][0] == initialHour and index[i][1] == initialMinute:
                result.append(index[i][2])
                break
        # TODO: Watch out with MIDNIGHT trips !!!!
        if len(result) == 0:
            result.append(len(Fitness.request))
        # if result[0] > len(Fitness.request):
        #    result[0] = len(Fitness.request)
        for i in range(i, len(index)):
            if index[i][0] == finalHour and index[i][1] == finalMinute:
                result.append(index[i][2])
                break
        # TODO: Watch out with MIDNIGHT trips !!!!
        if len(result) == 1:
            result.append(len(Fitness.request))
        return result

    def searchRequest(self, initialTime, finalTime, busStop):
        result = []
        index = self.searchRequestIndex(Fitness.requestIndex, initialTime.hour, initialTime.minute, finalTime.hour, finalTime.minute)
        request = Fitness.request[index[0]:index[1]]
        for i in range(len(request)):
            if request[i]["startBusStop"] == busStop:
                result.append(request[i])
        return result

    def evalIndividualCapacity(self, individual):
        ''' Evaluates an individual based on the capacity/bus type chosen for each trip.

        @param: individual - a possible timetable for a bus line, covering the whole day.
        @return: a fitness score assigned in accordance with how close the requested
        capacity is to the availed capacity on the individual
        '''
        individual.sort(key = itemgetter(2))
        self.expectedTimes = {}
        for trip, item in enumerate(individual):
            if trip == 0:
                self.start = datetime.strptime('00:00', '%H:%M')
                self.end   = datetime.strptime(individual[0][2], '%H:%M')
                self.nrReqs = self.getNumberOfRequests(self.start) 
                print "max number of requests for trip " + str(trip) + " is " + str(self.nrReqs)

            else:
                self.start = datetime.strptime(individual[trip-1][2], '%H:%M')
                self.end   = datetime.strptime(individual[trip][2], '%H:%M')
                self.nrReqs = self.getNumberOfRequests(self.start)

        return self.nrReqs

    def evalIndividual(self, individual):
        ''' Evaluate an individual in the population. Based on how close the
        average bus request time is to the actual bus trip time.

        @param an individual in the population
        @return a summation of the difference between past past requests'
        average trip starting time and actual start time
        according to the evolving timetable.
        Lower values are better.
        '''
        # DONE Store the date on mongo as datetime 
        # Store the requests of the previous day into a JSON file order them by date and KEEP IT during the whole iteration on memory
        # DONE Group by request query from the file to reduce the number of elements being processed

        # Use map function instead of LOOP
        # Query the DB only once to retrieve all the data needed
        # Multi thread the MAP functions
        # First, the randomly-generated starting times are sorted in order to check sequentially the number of requests for that particular trip
        individual = sorted(individual, key=itemgetter(2))
        # Second, we loop trough the number of genes in order to retrieve the number of requests for that particular trip
        # For the 1st trip, the starting time has to be selected
        db = DB()
        # Replace the dates here from yesterday's date
        request = Fitness.requests
        dif = []
        cnt = []
        intialTripTime = "00:00"
        # TODO: Change to timedelta(1)
        yesterday = date.today() - timedelta(6)

        # The result here should be added into a file: the order is by hour, minute and initialBusStop
        request = []
        dif = []
        cnt = []
        intialTripTime = "00:00"
        for i in range(len(individual)):
            tripTimeTable = db.generateFitnessTripTimeTable(individual[i][0], individual[i][2])
            # For each gene, the corresponding requests are returned
            for j in range(len(tripTimeTable)):
                # Search on Fitness.request array for the particular requests
                request = self.searchRequest(datetime.combine(Fitness.yesterday, datetime.strptime(intialTripTime, Fitness.formatTime).time()), datetime.combine(Fitness.yesterday, datetime.strptime(tripTimeTable[j][1], Fitness.formatTime).time()), tripTimeTable[j][0])
                intialTripTime = tripTimeTable[j][1]
                if len(request) > 0:
                    diff = 0
                    count = 0
                    for k in range(len(request)):
                        diff = diff + self.getMinutes(self.timeDiff(tripTimeTable[j][1], str(int(request[k]["hour"])) + ":" + str(int(request[k]["minute"]))))*int(request[k]["count"])
                        count = count + int(request[k]["count"])
                    dif.append(diff)
                    cnt.append(count)
        return sum(dif)/sum(cnt),
