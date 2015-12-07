package se.uu.csproject.monadvehicle;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.Date;
import java.util.Iterator;


/**
 *
 */
public class VehicleAdministration extends Administration {
    public static String[] profile = new String[5];
    /*
     * 0: vehicleID
     * 1: driverID
     * 2: password
     * 3: busLine
     * 4: googleRegistrationToken
     */

    public static String getVehicleID() {
        return profile[0];
    }
    public static void setVehicleID(String vehicleID) {
        profile[0] = vehicleID;
    }

    public static String getDriverID() {
        return profile[1];
    }
    public static void setDriverID(String driverID) {
        profile[1] = driverID;
    }

    public static String getPassword() {
        return profile[2];
    }
    public static void setPassword(String password) {
        profile[2] = password;
    }

    public static String getBusLine() {
        return profile[3];
    }
    public static void setBusLine(String busLine) {
        profile[3] = busLine;
    }

    public static String getGoogleRegistrationToken() {
        return profile[4];
    }
    public static void setGoogleRegistrationToken(String googleRegistrationToken) {
        profile[4] = googleRegistrationToken;
    }

    public static void updateProfileAfterSignIn(String vehicleID, String driverID, String password, String busLine) {
        setVehicleID(vehicleID);
        setDriverID(driverID);
        setPassword(password);
        setBusLine(busLine);
        setGoogleRegistrationToken("");
    }

    public static String profileToString() {
        String strProfile = "\nVehicleID: " + getVehicleID()
                + "\nDriverID: " + getDriverID()
                + "\nPassword: " + getPassword()
                + "\nBusLine: " + getBusLine()
                + "\nGoogleRegistrationToken: " + getGoogleRegistrationToken();
        return strProfile;
    }

    public static String postSignInRequest(String driverID, String password, String busLine) {

        /* Encrypt password */
//        password = Security.encryptPassword(password);

        String request = ROUTES_ADMINISTRATOR_HOST + ROUTES_ADMINISTRATOR_PORT + "/vehicle_sign_in";
        String urlParameters = "driver_id=" + driverID + "&password=" + password + "&bus_line=" + busLine;

        /* Send the request to the Routes Administrator */
        String response = postRequest(request, urlParameters);

        /* Handle response in case of exception */
        if (response.equals("-1")) {
            return exceptionMessage();
        }

        /*
         * By default, Erlang adds the newline '\n' character at the beginning of response.
         * For this reason substring() function is used
         */
        response = response.substring(1);
        // response = response.trim();

        /* Process Routes Administrator's response */
        return processSignInResponse(driverID, password, busLine, response);
    }

    public static String processSignInResponse(String driverID, String password, String busLine, String response) {
        String responseMessage = "";
        /*
         * Successful signIn request
         * Response: "1|vehicleID"
         */
        if (response.startsWith("1|")) {
            String vehicleID = response.substring(2);
            updateProfileAfterSignIn(vehicleID, driverID, password, busLine);
            responseMessage = "Success (1) - VehicleID: " + getVehicleID();
        }
        else if (response.equals("0")) {
            responseMessage = "Wrong Credentials (0)";
        }
        else {
            responseMessage = "ERROR - " + response;
        }
        return responseMessage;
    }

    public static String postGetNextTripRequest() {
        String request = ROUTES_ADMINISTRATOR_HOST + ROUTES_ADMINISTRATOR_PORT + "/vehicle_get_next_trip";
        String urlParameters = "vehicle_id=" + getVehicleID();

        /* Send the request to the Routes Administrator */
        String response = postRequest(request, urlParameters);

        /* Handle response in case of exception */
        if (response.equals("-1")) {
            return exceptionMessage();
        }

        /*
         * By default, Erlang adds the newline '\n' character at the beginning of response.
         * For this reason substring() function is used
         */
        response = response.substring(1);
        // response = response.trim();

        /* Process Routes Administrator's response */
        return processGetNextTripResponse(response);
    }

    public static String processGetNextTripResponse(String response) {
        JSONParser parser = new JSONParser();

        try {
            JSONObject busTripObject = (JSONObject) parser.parse(response);

            JSONObject busTripObjectID = (JSONObject) busTripObject.get("_id");
            String busTripID = (String) busTripObjectID.get("$oid");

            long tempCapacity = (long) busTripObject.get("capacity");
            int capacity = new BigDecimal(tempCapacity).intValueExact();

//            long tempLine = (long) busTripObject.get("line");
//            int line = new BigDecimal(tempLine).intValueExact();

            JSONArray trajectoryArray = (JSONArray) busTripObject.get("trajectory");
            Iterator<JSONObject> trajectoryArrayIterator = trajectoryArray.iterator();

            ArrayList<BusStop> trajectory = new ArrayList<>();

            while (trajectoryArrayIterator.hasNext()) {

                JSONObject trajectoryPoint = trajectoryArrayIterator.next();
                JSONObject busStopObject = (JSONObject) trajectoryPoint.get("busStop");

                JSONObject busStopObjectID = (JSONObject) busStopObject.get("_id");
                String busStopID = (String) busStopObjectID.get("$oid");

                String busStopName = (String) busStopObject.get("name");

                double busStopLatitude = (double) busStopObject.get("latitude");
                double busStopLongitude = (double) busStopObject.get("longitude");

                JSONObject arrivalTimeObject = (JSONObject) trajectoryPoint.get("time");
                Date busStopArrivalTime = new Date((long) arrivalTimeObject.get("$date"));

                BusStop busStop = new BusStop(busStopID, busStopName, busStopLatitude, busStopLongitude, busStopArrivalTime);
                trajectory.add(busStop);
            }

            BusTrip busTrip = new BusTrip(busTripID, capacity, trajectory);
            Storage.setBusTrip(busTrip);
            busTrip.printValues();
        }
        catch (Exception e) {
            e.printStackTrace();
            return "0";
        }
        return "1";
    }

//    public static String getBusStopCoordinatesString() {
//        BusTrip busTrip = Storage.getBusTrip();
//
//        if (busTrip != null && busTrip.getTrajectory() != null) {
//
//            for (int i = 0; i < busTrip.getTrajectory().size(); i++) {
//                double lon = busTrip.getTrajectory().get(i).getLongitude();
//                double lat = busTrip.getTrajectory().get(i).getLatitude();
//                String.valueOf();
//                String res = "(" + String.valueOf()
//            }
//
//            Storage.getBusTrip().getTrajectory()
//        }
//        else {
//
//        }
//
//    }


    public static String exceptionMessage() {
        return "ERROR - An Exception was thrown";
    }


}