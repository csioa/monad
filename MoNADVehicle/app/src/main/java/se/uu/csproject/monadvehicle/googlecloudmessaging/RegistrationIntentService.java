package se.uu.csproject.monadvehicle.googlecloudmessaging;


import android.app.IntentService;
import android.content.Intent;
import android.content.SharedPreferences;
import android.preference.PreferenceManager;
import android.support.v4.content.LocalBroadcastManager;
import android.util.Log;

import com.google.android.gms.gcm.GcmPubSub;
import com.google.android.gms.gcm.GoogleCloudMessaging;
import com.google.android.gms.iid.InstanceID;

import se.uu.csproject.monadvehicle.R;
import se.uu.csproject.monadvehicle.serverinteractions.VehicleAdministration;

import java.io.IOException;


public class RegistrationIntentService extends IntentService {

    private static final String TAG = "RegIntentService";
    private static final String[] TOPICS = {"global"};

    public RegistrationIntentService() {
        super(TAG);
    }

    @Override
    protected void onHandleIntent(Intent intent) {
        SharedPreferences sharedPreferences = PreferenceManager.getDefaultSharedPreferences(this);

        try {
            // [START register_for_gcm]
            // Initially this call goes out to the network to retrieve the token, subsequent calls
            // are local.
            // [START get_token]
            //String iid = InstanceID.getInstance(this).getID();
            //Log.i(TAG, "MY Instance ID: " + iid);

            InstanceID instanceID = InstanceID.getInstance(getApplicationContext());
            String authorizedEntity=getString(R.string.GoogleProjectID);
            String token = instanceID.getInstance(getApplicationContext()).getToken(authorizedEntity,GoogleCloudMessaging.INSTANCE_ID_SCOPE, null);

            // [END get_token]
            Log.i(TAG, "MY GCM Registration Token: " + token);

            VehicleAdministration.setGoogleRegistrationToken(token);

            // Implement  method to send any registration to your app's servers.
            sendRegistrationToServer(token);

            // Subscribe to topic channels
            subscribeTopics(token);

            sharedPreferences.edit().putBoolean(TokenStartupReference.SENT_TOKEN_TO_SERVER, true).apply();
            // [END register_for_gcm]
        } catch (Exception e) {
            Log.d(TAG, "Failed to complete token refresh", e);
            // If an exception happens while fetching the new token or updating our registration data
            //// on a third-party server, this ensures that we'll attempt the update at a later time.
            sharedPreferences.edit().putBoolean(TokenStartupReference.SENT_TOKEN_TO_SERVER, false).apply();
        }
        // Notify UI that registration has completed, so the progress indicator can be hidden.
        Intent registrationComplete = new Intent(TokenStartupReference.REGISTRATION_COMPLETE);
        LocalBroadcastManager.getInstance(this).sendBroadcast(registrationComplete);
    }

    private void sendRegistrationToServer(String token) {
        // Currently implemented differently

    }

    private void subscribeTopics(String token) throws IOException {
        GcmPubSub pubSub = GcmPubSub.getInstance(this);
        for (String topic : TOPICS) {
            pubSub.subscribe(token, "/topics/" + topic, null);
        }
    }
    //  everyone is subscribed to topics

}
