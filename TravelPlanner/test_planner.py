# Copyright 2015 Ericsson AB
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not 
# use this file except in compliance with the License. You may obtain a copy 
# of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software 
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT 
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the 
# License for the specific language governing permissions and limitations 
# under the License.

from planner import TravelPlanner, Mode
import unittest
import datetime
import pytest
import sys
import pymongo
from pymongo import MongoClient
import bson
from bson.objectid import ObjectId

YEAR  = 2015
MONTH = 10
DAY   = 10

TIMEDIFF_0MIN = datetime.timedelta(minutes = 0)
TIMEDIFF_10MIN = datetime.timedelta(minutes = 10)
TIMEDIFF_15MIN = datetime.timedelta(minutes = 15)
TIMEDIFF_20MIN = datetime.timedelta(minutes = 20)
TIMEDIFF_25MIN = datetime.timedelta(minutes = 25)
TIMEDIFF_30MIN = datetime.timedelta(minutes = 30)
TIMEDIFF_45MIN = datetime.timedelta(minutes = 45)
TIMEDIFF_60MIN = datetime.timedelta(minutes = 60)
TIME_1255H = datetime.datetime(YEAR, MONTH, DAY, 12, 55)
TIME_1300H = datetime.datetime(YEAR, MONTH, DAY, 13, 00)
TIME_1305H = datetime.datetime(YEAR, MONTH, DAY, 13,  5)
TIME_1315H = datetime.datetime(YEAR, MONTH, DAY, 13, 15)
TIME_1320H = datetime.datetime(YEAR, MONTH, DAY, 13, 20)
TIME_1330H = datetime.datetime(YEAR, MONTH, DAY, 13, 30)
TIME_1345H = datetime.datetime(YEAR, MONTH, DAY, 13, 45)
TIME_1400H = datetime.datetime(YEAR, MONTH, DAY, 14, 00)

class TestTravelPlanner(unittest.TestCase):

    client = MongoClient()
    dbName = "monad1"
    db = client[dbName]
    tp = TravelPlanner(db)
    version = sys.version_info[0]

    def test_init(self):
        self.tp._prepareSearch()
        if (self.version == 2):
            mongoString = "Collection(Database(MongoClient('localhost', 27017), u'"
            requestDBString = mongoString + self.dbName + "'), u'TravelRequest')"
            routeDBString = mongoString + self.dbName + "'), u'Route')"
            timetableDBString = mongoString + self.dbName + "'), u'TimeTable')"
            usertripDBString = mongoString + self.dbName + "'), u'UserTrip')"
            busTripDBString = mongoString + self.dbName + "'), u'BusTrip')"
            busStopDBString = mongoString + self.dbName + "'), u'BusStop')"
        elif (self.version == 3):
            mongoString = "Collection(Database(MongoClient(host=['localhost:27017'], " + \
                    "document_class=dict, tz_aware=False, connect=True), '"
            requestDBString = mongoString + self.dbName + "'), 'TravelRequest')"
            routeDBString = mongoString + self.dbName + "'), 'Route')"
            timetableDBString = mongoString + self.dbName + "'), 'TimeTable')"
            usertripDBString = mongoString + self.dbName + "'), 'UserTrip')"
            busTripDBString = mongoString + self.dbName + "'), 'BusTrip')"
            busStopDBString = mongoString + self.dbName + "'), 'BusStop')"

        self.assertEqual(self.tp.singleRoutes, [])
        self.assertEqual(self.tp.multiRoutes, [])
        self.assertEqual(self.tp.possibleRoutes, [])
        self.assertEqual(self.tp.tripTuples, [])
        self.assertEqual(self.tp.lineTuples, [])

        self.assertEqual(str(self.tp.travelRequest), requestDBString)
        self.assertEqual(str(self.tp.route), routeDBString)
        self.assertEqual(str(self.tp.timeTable), timetableDBString)
        self.assertEqual(str(self.tp.userTrip), usertripDBString)
        self.assertEqual(str(self.tp.busTrip), busTripDBString)
        self.assertEqual(str(self.tp.busStop), busStopDBString)

    def test_range(self):
        r1 = [2, 1, 0]
        r2 = [0, 1, 2]
        self.assertEqual(r1, self.tp._range(4))
        self.assertNotEqual(r2, self.tp._range(4))

    def test_isBetterTripStartTime(self):
        self.tp.tripTuples = [("trip", TIMEDIFF_30MIN, TIME_1300H, TIME_1315H)]
        self.tp.timeMode = Mode.startTime

        self.tp.timeToArrival = TIMEDIFF_25MIN
        self.assertTrue(self.tp._isBetterTrip(0))

        self.tp.timeToArrival = TIMEDIFF_30MIN
        self.tp.dptTime = TIME_1305H
        self.tp.routeMode = Mode.tripTime
        self.assertTrue(self.tp._isBetterTrip(0))
        self.tp.routeMode = Mode.waitTime
        self.assertFalse(self.tp._isBetterTrip(0))

        self.tp.dptTime = TIME_1255H
        self.tp.routeMode = Mode.waitTime
        self.assertTrue(self.tp._isBetterTrip(0))
        self.tp.routeMode = Mode.tripTime
        self.assertFalse(self.tp._isBetterTrip(0))

        self.tp.timeToArrival = TIMEDIFF_60MIN
        self.assertFalse(self.tp._isBetterTrip(0))

    def test_isBetterTripArrivalTime(self):
        self.tp.tripTuples = [("trip", TIMEDIFF_30MIN, TIME_1300H, TIME_1315H)]
        self.tp.timeMode = Mode.arrivalTime

        self.tp.diffToArrTime = TIMEDIFF_25MIN
        self.assertTrue(self.tp._isBetterTrip(0))

        self.tp.diffToArrTime = TIMEDIFF_30MIN
        self.tp.dptTime = TIME_1305H
        self.tp.routeMode = Mode.tripTime
        self.assertTrue(self.tp._isBetterTrip(0))
        self.tp.routeMode = Mode.waitTime
        self.assertFalse(self.tp._isBetterTrip(0))

        self.tp.dptTime = TIME_1255H
        self.tp.routeMode = Mode.waitTime
        self.assertTrue(self.tp._isBetterTrip(0))
        self.tp.routeMode = Mode.tripTime
        self.assertFalse(self.tp._isBetterTrip(0))

        self.tp.diffToArrTime = TIMEDIFF_60MIN
        self.assertFalse(self.tp._isBetterTrip(0))

    def test_rankTripStartTime(self):
        trip1 = ("trip1", TIMEDIFF_15MIN, TIME_1305H, TIME_1315H)
        trip2 = ("trip2", TIMEDIFF_20MIN, TIME_1300H, TIME_1320H)
        trip3 = ("trip3", TIMEDIFF_30MIN, TIME_1315H, TIME_1330H)
        trip4 = ("trip4", TIMEDIFF_30MIN, TIME_1300H, TIME_1330H)
        self.tp.tripTuples = [trip1, trip2, trip3, trip4]
        self.tp.timeMode = Mode.startTime
        self.tp.routeMode = Mode.tripTime

        trip = "trip5"
        self.tp.timeToArrival = TIMEDIFF_60MIN
        self.tp.dptTime = TIME_1330H
        self.tp.arrTime = TIME_1400H
        trip5 = (trip, self.tp.timeToArrival, self.tp.dptTime, self.tp.arrTime)
        self.tp._rankTrip(trip)
        self.assertEqual(self.tp.tripTuples, [trip1, trip2, trip3, trip4, trip5])

        trip = "trip6"
        self.tp.timeToArrival = TIMEDIFF_20MIN
        self.tp.dptTime = TIME_1305H
        self.tp.arrTime = TIME_1320H
        trip6 = (trip, self.tp.timeToArrival, self.tp.dptTime, self.tp.arrTime)
        self.tp._rankTrip(trip)
        self.assertEqual(self.tp.tripTuples, [trip1, trip6, trip2, trip3, trip4])

        trip = "trip7"
        self.tp.timeToArrival = TIMEDIFF_60MIN
        self.tp.dptTime = TIME_1330H
        self.tp.arrTime = TIME_1400H
        trip7 = (trip, self.tp.timeToArrival, self.tp.dptTime, self.tp.arrTime)
        self.tp._rankTrip(trip)
        self.assertEqual(self.tp.tripTuples, [trip1, trip6, trip2, trip3, trip4])

    def test_rankTripArrivalTime(self):
        trip1 = ("trip1", TIMEDIFF_0MIN, TIME_1330H, TIME_1400H)
        trip2 = ("trip2", TIMEDIFF_30MIN, TIME_1320H, TIME_1330H)
        trip3 = ("trip3", TIMEDIFF_30MIN, TIME_1315H, TIME_1330H)
        trip4 = ("trip4", TIMEDIFF_30MIN, TIME_1300H, TIME_1330H)
        self.tp.tripTuples = [trip1, trip2, trip3, trip4]
        self.tp.timeMode = Mode.arrivalTime
        self.tp.routeMode = Mode.tripTime

        trip = "trip5"
        self.tp.diffToArrTime = TIMEDIFF_45MIN
        self.tp.dptTime = TIME_1300H
        self.tp.arrTime = TIME_1315H
        trip5 = (trip, self.tp.diffToArrTime, self.tp.dptTime, self.tp.arrTime)
        self.tp._rankTrip(trip)
        self.assertEqual(self.tp.tripTuples, [trip1, trip2, trip3, trip4, trip5])

        trip = "trip6"
        self.tp.diffToArrTime = TIMEDIFF_15MIN
        self.tp.dptTime = TIME_1330H
        self.tp.arrTime = TIME_1345H
        trip6 = (trip, self.tp.diffToArrTime, self.tp.dptTime, self.tp.arrTime)
        self.tp._rankTrip(trip)
        self.assertEqual(self.tp.tripTuples, [trip1, trip6, trip2, trip3, trip4])

        trip = "trip7"
        self.tp.diffToArrTime = TIMEDIFF_60MIN
        self.tp.dptTime = TIME_1300H
        self.tp.arrTime = TIME_1255H
        trip7 = (trip, self.tp.diffToArrTime, self.tp.dptTime, self.tp.arrTime)
        self.tp._rankTrip(trip)
        self.assertEqual(self.tp.tripTuples, [trip1, trip6, trip2, trip3, trip4])

    def test_insertTrip(self):
        self.tp.tripTuples = []
        self.tp.counter = 0
        self.tp.startingWaypoint = [0]
        self.tp.endingWaypoint = [1]
        self.tp.startTime = TIME_1300H
        self.tp.timeMode = Mode.startTime

        trip = "trip1"
        self.tp.dptTime = TIME_1305H
        self.tp.arrTime = TIME_1315H
        self.tp._insertTrip(trip)
        trip1 = (trip, TIMEDIFF_15MIN, TIME_1305H, TIME_1315H)
        self.assertEqual(self.tp.tripTuples, [trip1])

        trip = "trip2"
        self.tp.dptTime = TIME_1315H
        self.tp.arrTime = TIME_1320H
        self.tp._insertTrip(trip)
        trip2 = (trip, TIMEDIFF_20MIN, TIME_1315H, TIME_1320H)
        self.assertEqual(self.tp.tripTuples, [trip1, trip2])

        self.tp.tripTuples = []
        self.tp.endTime = TIME_1400H
        self.tp.timeMode = Mode.arrivalTime

        trip = "trip1"
        self.tp.dptTime = TIME_1330H
        self.tp.arrTime = TIME_1345H
        self.tp._insertTrip(trip)
        trip1 = (trip, TIMEDIFF_15MIN, TIME_1330H, TIME_1345H)
        self.assertEqual(self.tp.tripTuples, [trip1])

        trip = "trip2"
        self.tp.dptTime = TIME_1345H
        self.tp.arrTime = TIME_1400H
        self.tp._insertTrip(trip)
        trip2 = (trip, TIMEDIFF_0MIN, TIME_1345H, TIME_1400H)
        self.assertEqual(self.tp.tripTuples, [trip2, trip1])

    def test_isFastRoute(self):
        self.tp.tripTuples = []
        self.assertFalse(self.tp._isFastRoute())
        self.tp.tripTuples = [("trip", TIMEDIFF_15MIN, TIME_1305H, TIME_1315H)]
        self.assertTrue(self.tp._isFastRoute())
        self.tp.tripTuples = [("trip", TIMEDIFF_30MIN, TIME_1305H, TIME_1330H)]
        self.assertFalse(self.tp._isFastRoute())

    def test_convertToJason(self):
        stops = ["Stora Torget", "Centralstationen"]
        objectID = ObjectId()
        objectIDstr = str(objectID)
        time = TIME_1300H
        timeStr = str(time)
        self.tp.userTripDict = {1:[
                {
                    "_id": objectID,
                    "userID" : 4711,
                    "line": 2,
                    "busID": 56,
                    "startBusStop": stops[0],
                    "endBusStop": stops[1],
                    "startTime": time,
                    "endTime": time,
                    "requestTime": time,
                    "feedback": -1,
                    "requestID": objectID,
                    "next": objectID,
                    "busTripID": objectID,
                    "booked": False,
                    "trajectory": [stops[0], stops[1]]
                },
                {
                    "_id": objectID,
                    "userID" : 4711,
                    "line": 14,
                    "busID": 57,
                    "startBusStop": stops[0],
                    "endBusStop": stops[1],
                    "startTime": time,
                    "endTime": time,
                    "requestTime": time,
                    "feedback": -1,
                    "requestID": objectID,
                    "busTripID": objectID,
                    "booked": False,
                    "trajectory": [stops[0], stops[1]]
                }
            ]
        }
        self.tp._convertToJson()
        jsonObject = self.tp.jsonObject
        self.assertEqual(objectIDstr, jsonObject[1][0]["_id"])
        self.assertEqual(objectIDstr, jsonObject[1][0]["requestID"])
        self.assertEqual(objectIDstr, jsonObject[1][1]["busTripID"])
        self.assertEqual(objectIDstr, jsonObject[1][0]["next"])
        self.assertEqual(objectIDstr, jsonObject[1][1]["_id"])
        self.assertEqual(objectIDstr, jsonObject[1][1]["requestID"])
        self.assertEqual(objectIDstr, jsonObject[1][1]["busTripID"])

        self.assertEqual(stops[0], jsonObject[1][0]["startBusStop"])
        self.assertEqual(stops[1], jsonObject[1][0]["endBusStop"])
        self.assertEqual(stops[0], jsonObject[1][0]["trajectory"][0])
        self.assertEqual(stops[1], jsonObject[1][0]["trajectory"][1])
        self.assertEqual(stops[0], jsonObject[1][1]["startBusStop"])
        self.assertEqual(stops[1], jsonObject[1][1]["endBusStop"])
        self.assertEqual(stops[0], jsonObject[1][1]["trajectory"][0])
        self.assertEqual(stops[1], jsonObject[1][1]["trajectory"][1])

        self.assertEqual(timeStr, jsonObject[1][0]["startTime"])
        self.assertEqual(timeStr, jsonObject[1][0]["endTime"])
        self.assertEqual(timeStr, jsonObject[1][0]["requestTime"])
        self.assertEqual(timeStr, jsonObject[1][1]["startTime"])
        self.assertEqual(timeStr, jsonObject[1][1]["endTime"])
        self.assertEqual(timeStr, jsonObject[1][1]["requestTime"])

        self.assertTrue("next" in jsonObject[1][0])
        self.assertFalse("next" in jsonObject[1][1])

    # The number of tests is very important!
    def test_hereIsOneMoreTestThatWillSucceed(self):
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()

