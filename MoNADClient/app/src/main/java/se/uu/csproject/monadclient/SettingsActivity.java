package se.uu.csproject.monadclient;

import android.content.Context;
import android.content.Intent;
import android.os.AsyncTask;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentManager;
import android.support.v4.app.FragmentPagerAdapter;
import android.support.v4.app.NavUtils;
import android.os.Bundle;
import android.support.v4.content.ContextCompat;
import android.support.v4.view.ViewPager;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.DefaultItemAnimator;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.support.v7.widget.Toolbar;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;
import android.widget.CompoundButton;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutionException;

import se.uu.csproject.monadclient.recyclerviews.LanguageRecyclerViewAdapter;
import se.uu.csproject.monadclient.tabs.SlidingTabLayout;
import se.uu.csproject.monadclient.recyclerviews.Language;

public class SettingsActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_settings);
        Toolbar toolbar = (Toolbar) findViewById(R.id.actionToolBar);
        setSupportActionBar(toolbar);
    //    getSupportActionBar().setHomeButtonEnabled(true);
    //    getSupportActionBar().setDisplayHomeAsUpEnabled(true);

        SlidingTabLayout tabs = (SlidingTabLayout) findViewById(R.id.tabs);
        ViewPager pager = (ViewPager) findViewById(R.id.pager);
        pager.setAdapter(new SettingsPagerAdapter(getSupportFragmentManager(), SettingsActivity.this));
        tabs.setDistributeEvenly(true);
        tabs.setSelectedIndicatorColors(ContextCompat.getColor(this.getApplicationContext(), R.color.white));
        tabs.setViewPager(pager);
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        if(id == android.R.id.home){
            NavUtils.navigateUpFromSameTask(this);
        }

        if (id == R.id.action_search) {
            startActivity(new Intent(this, MainActivity.class));
        }

        if (id == R.id.action_notifications) {
            startActivity(new Intent(this, NotificationsActivity.class));
        }

        if (id == R.id.action_mytrips) {
            startActivity(new Intent(this, TripsActivity.class));
        }

        if (id == R.id.action_profile) {
            startActivity(new Intent(this, ProfileActivity.class));
        }

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        if (id == R.id.action_aboutus) {
            startActivity(new Intent(this, AboutUsActivity.class));
        }

        if (id == R.id.action_signout) {
            startActivity(new Intent(this, LoginActivity.class));
        }

        return super.onOptionsItemSelected(item);
    }

    public class SettingsPagerAdapter extends FragmentPagerAdapter{
        final int TAB_COUNT = 3; // Language, Alerts, Theme
        private String[] tabTitles;
        Context context;

        public SettingsPagerAdapter(FragmentManager fm, Context context) {
            super(fm);
            tabTitles = getResources().getStringArray(R.array.settings_tab_titles);
            this.context = context;
        }

        @Override
        public Fragment getItem(int position) {
            return SettingsFragment.getInstance(position + 1);
        }

        @Override
        public CharSequence getPageTitle(int position) {
            return tabTitles[position];
        }

        @Override
        public int getCount() {
            return TAB_COUNT; // GI - number of tabs in the settings view
        }
    }

    public static class SettingsFragment extends Fragment{
        public static final String TAB_POSITION = "tab_position";
        private int page;

        public static SettingsFragment getInstance(int position){
            SettingsFragment settingsFragment = new SettingsFragment();
            Bundle args = new Bundle();
            args.putInt(TAB_POSITION, position);
            settingsFragment.setArguments(args);
            return settingsFragment;
        }

        @Override
        public void onCreate(Bundle savedInstanceState) {
            super.onCreate(savedInstanceState);
            page = getArguments().getInt(TAB_POSITION);
        }

        //TODO 2 Ilyass: finalize language settings
        //TODO: update language settings in database
        @Override
        public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState){
            View layout;

            if(page == 1){
                layout = inflater.inflate(R.layout.fragment_settings_language,container,false);
                List<Language> languages = new ArrayList<>();
                RecyclerView recyclerView = (RecyclerView) layout.findViewById(R.id.recycler_view);
                LinearLayoutManager linearLayoutManager = new LinearLayoutManager(getContext());
                recyclerView.setLayoutManager(linearLayoutManager);
                initializeLanguages(languages);
                LanguageRecyclerViewAdapter adapter = new LanguageRecyclerViewAdapter(languages);
                recyclerView.setAdapter(adapter);
                recyclerView.setItemAnimator(new DefaultItemAnimator());
            }
            else if(page == 2){
                layout = inflater.inflate(R.layout.fragment_settings_alerts,container,false);
                final Switch switchrecommendation;
                final Switch switchalert;
                final TextView recommendationsSwitch = (TextView) layout.findViewById(R.id.label_recommendationsswitch);
                final TextView remindersSwitch= (TextView) layout.findViewById(R.id.label_remindersswitch);

                // switch button for alerts and recommendations
                switchrecommendation = (Switch)layout.findViewById(R.id.switch_fragmentsettingsalert_recommendations);
                switchalert = (Switch)layout.findViewById(R.id.switch_fragmentsettingsalert_alerts);
                switchrecommendation.setChecked(true);
                switchalert.setChecked(true);

                switchrecommendation.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
                    @Override
                    public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                        if(switchrecommendation.isChecked()) {
                            UpdateSettingsTask task = new UpdateSettingsTask();

                            String response = null;
                            try {
                                response = task.execute(
                                        ClientAuthentication.getClientId(),
                                        ClientAuthentication.getLanguage(),
                                        ClientAuthentication.getStoreLocation(),
                                        ClientAuthentication.getNotificationsAlert(),
                                        "1",
                                        ClientAuthentication.getTheme()).get();
                            } catch (InterruptedException e) {
                                e.printStackTrace();
                            } catch (ExecutionException e) {
                                e.printStackTrace();
                            }
                            if(response.startsWith("Success (1)")){
                                // The space after ON should be kept for UI formatting purposes
                                recommendationsSwitch.setText("ON ");
                            }
                            Toast.makeText(getActivity().getApplicationContext(), response, Toast.LENGTH_LONG).show();

//                            ClientAuthentication.postSettingsUpdateRequest(
//                                    ClientAuthentication.getClientId(),
//                                    ClientAuthentication.getLanguage(),
//                                    ClientAuthentication.getStoreLocation(),
//                                    ClientAuthentication.getNotificationsAlert(),
//                                    "1",
//                                    ClientAuthentication.getTheme());
                        }
                        else {
                            UpdateSettingsTask task = new UpdateSettingsTask();

                            String response = null;
                            try {
                                response = task.execute(
                                        ClientAuthentication.getClientId(),
                                        ClientAuthentication.getLanguage(),
                                        ClientAuthentication.getStoreLocation(),
                                        ClientAuthentication.getNotificationsAlert(),
                                        "0",
                                        ClientAuthentication.getTheme()).get();
                            } catch (InterruptedException e) {
                                e.printStackTrace();
                            } catch (ExecutionException e) {
                                e.printStackTrace();
                            }
                            if(response.startsWith("Success (1)")){
                                // The space after ON should be kept for UI formatting purposes
                                recommendationsSwitch.setText("OFF");
                            }
                            Toast.makeText(getActivity().getApplicationContext(), response, Toast.LENGTH_LONG).show();
//                            ClientAuthentication.postSettingsUpdateRequest(
//                                    ClientAuthentication.getClientId(),
//                                    ClientAuthentication.getLanguage(),
//                                    ClientAuthentication.getStoreLocation(),
//                                    ClientAuthentication.getNotificationsAlert(),
//                                    "0",
//                                    ClientAuthentication.getTheme());
                        }
                    }
                });

                switchalert.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
                    @Override
                    public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                        if(switchalert.isChecked()){
                            // The space after ON should be kept for UI formatting purposes
                            UpdateSettingsTask task = new UpdateSettingsTask();

                            String response = null;
                            try {
                                response = task.execute(
                                        ClientAuthentication.getClientId(),
                                        ClientAuthentication.getLanguage(),
                                        ClientAuthentication.getStoreLocation(),
                                        "1",
                                        ClientAuthentication.getRecommendationsAlert(),
                                        ClientAuthentication.getTheme()).get();
                            } catch (InterruptedException e) {
                                e.printStackTrace();
                            } catch (ExecutionException e) {
                                e.printStackTrace();
                            }
                            if(response.startsWith("Success (1)")){
                                // The space after ON should be kept for UI formatting purposes
                                remindersSwitch.setText("ON ");
                            }
                            Toast.makeText(getActivity().getApplicationContext(), response, Toast.LENGTH_LONG).show();
//                            remindersSwitch.setText("ON ");
//                            ClientAuthentication.postSettingsUpdateRequest(
//                                    ClientAuthentication.getClientId(),
//                                    ClientAuthentication.getLanguage(),
//                                    ClientAuthentication.getStoreLocation(),
//                                    "1",
//                                    ClientAuthentication.getRecommendationsAlert(),
//                                    ClientAuthentication.getTheme());
                        }
                        else {
                            UpdateSettingsTask task = new UpdateSettingsTask();

                            String response = null;
                            try {
                                response = task.execute(
                                        ClientAuthentication.getClientId(),
                                        ClientAuthentication.getLanguage(),
                                        ClientAuthentication.getStoreLocation(),
                                        "0",
                                        ClientAuthentication.getRecommendationsAlert(),
                                        ClientAuthentication.getTheme()).get();
                            } catch (InterruptedException e) {
                                e.printStackTrace();
                            } catch (ExecutionException e) {
                                e.printStackTrace();
                            }
                            if(response.startsWith("Success (1)")){
                                // The space after ON should be kept for UI formatting purposes
                                remindersSwitch.setText("OFF");
                            }
                            Toast.makeText(getActivity().getApplicationContext(), response, Toast.LENGTH_LONG).show();
//                            remindersSwitch.setText("OFF");
//                            ClientAuthentication.postSettingsUpdateRequest(
//                                    ClientAuthentication.getClientId(),
//                                    ClientAuthentication.getLanguage(),
//                                    ClientAuthentication.getStoreLocation(),
//                                    "0",
//                                    ClientAuthentication.getRecommendationsAlert(),
//                                    ClientAuthentication.getTheme());
                        }
                    }
                });
            }
            else if(page == 3){
                layout = inflater.inflate(R.layout.fragment_settings_theme,container,false);
                final RadioGroup radiogroup_themes;
                final RadioButton radiobutton_defaulttheme;
                final RadioButton radiobutton_lighttheme;
                final RadioButton radiobutton_darktheme;

                //different themes
                //radiogroup_themes  = (RadioGroup)layout.findViewById(R.id.radiogroup_fragmentsettingstheme_theme);
                radiobutton_defaulttheme = (RadioButton)layout.findViewById(R.id.radiobutton_fragmentsettingstheme_default);
                radiobutton_lighttheme = (RadioButton)layout.findViewById(R.id.radiobutton_fragmentsettingstheme_light);
                radiobutton_darktheme = (RadioButton)layout.findViewById(R.id.radiobutton_fragmentsettingstheme_dark);

                if(radiobutton_lighttheme.isChecked()){
                    //change the theme to light
                    ClientAuthentication.postSettingsUpdateRequest(
                            ClientAuthentication.getClientId(),
                            ClientAuthentication.getLanguage(),
                            ClientAuthentication.getStoreLocation(),
                            ClientAuthentication.getNotificationsAlert(),
                            ClientAuthentication.getRecommendationsAlert(),
                            "0");
                }

                if(radiobutton_defaulttheme.isChecked()){
                    //change the theme to default
                    ClientAuthentication.postSettingsUpdateRequest(
                            ClientAuthentication.getClientId(),
                            ClientAuthentication.getLanguage(),
                            ClientAuthentication.getStoreLocation(),
                            ClientAuthentication.getNotificationsAlert(),
                            ClientAuthentication.getRecommendationsAlert(),
                            "1");
                }

                if(radiobutton_darktheme.isChecked()){
                    //change the theme to dark
                    ClientAuthentication.postSettingsUpdateRequest(
                            ClientAuthentication.getClientId(),
                            ClientAuthentication.getLanguage(),
                            ClientAuthentication.getStoreLocation(),
                            ClientAuthentication.getNotificationsAlert(),
                            ClientAuthentication.getRecommendationsAlert(),
                            "2");
                }
            }
            else{
                layout = inflater.inflate(R.layout.fragment_settings_theme,container,false);
                //TextView textView = (TextView) layout.findViewById(R.id.themetxt);
                //textView.setText("DEFAULT FRAGMENT FROM THEME");
            }
            return layout;
        }

        private void initializeLanguages(List<Language> languages){
            languages.add(new Language("English", "en", R.drawable.lang_en));
            languages.add(new Language("Svenska", "sv", R.drawable.lang_sv));
            languages.add(new Language("Dansk", "dk", R.drawable.lang_dk));
            languages.add(new Language("Deutsch", "de", R.drawable.lang_de));
            languages.add(new Language("Norsk", "nr", R.drawable.lang_nr));
            languages.add(new Language("Suomi", "fi", R.drawable.lang_fi));
        }
    }

    private static class UpdateSettingsTask extends AsyncTask<String, Void, String>{

        @Override
        protected String doInBackground(String... params) {
            String response = ClientAuthentication.postSettingsUpdateRequest(params[0], params[1], params[2], params[3], params[4], params[5]);;
            return response;
        }
    }

}

