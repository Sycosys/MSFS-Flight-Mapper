from flask import Flask, render_template, jsonify, request
from SimConnectCust import *
from threading import Thread
import math
import sys

simconnect_dict = {}

def flask_thread_func(threadname):
    
    global simconnect_dict
    
    if getattr(sys, 'frozen', False):
        template_folder = os.path.join(sys._MEIPASS, 'templates')
        static_folder = os.path.join(sys._MEIPASS, 'static')
        app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
    else:
        app = Flask(__name__)
    
    @app.route('/_stuff', methods = ['GET'])
    def stuff():
        global simconnect_dict
        
        return jsonify(simconnect_dict)

    @app.route('/')
    def index():
        return render_template('body.html')

    app.run(host='127.0.0.1',port=5001, debug=False, use_reloader=False)

def simconnect_thread_func(threadname):
    
    global simconnect_dict
    
    # Init SimConnect
    sm = SimConnect()
    aq = AircraftRequests(sm, _time = 0)
    
    # Init variables
    airborne = False
    g_force = 0
    v_speed = 0
    plane_alt_above_ground = 0
    sim_on_ground = 0
    g_force_prev = 0
    v_speed_prev = 0
    plane_alt_above_ground_prev = 0
    lat_prev = 0
    lng_prev = 0
    bearing_prev = 0
    sim_on_ground_prev = 0

    alt_prev = 0
    gndAlt_prev = 0
    v_speed_prev = 0
    z_speed_prev = 0
    x_speed_prev = 0
    true_speed_prev = 0
    indi_speed_prev = 0
    mach_speed_prev = 0

    wind_dir_prev = 0
    wind_spd_prev= 0
    wind_vs_prev= 0

    baro_prev = 0
    slp_prev = 0 

    flightTrack=[]
    v_speed_list_all = []
    g_force_list_all = []
    v_speed_list = []
    g_force_list = []
    plane_alt_above_ground_list = []
    v_speed_list_ground = []
    g_force_list_ground = []
    plane_alt_above_ground_list_ground = []
    sim_on_ground_list = [1,1,1,1,1,1,1,1]
    run_app = 1
    simconnect_dict["G_FORCE"] = 0
    simconnect_dict["MAX_G_FORCE"] = 0
    simconnect_dict["VERTICAL_SPEED"] = 0.0
    simconnect_dict["HORIZONTAL_SPEED"]=0.0
    simconnect_dict["LATITUDE"]=0.0
    simconnect_dict["LONGITUDE"]=0.0
    simconnect_dict["PLANE_ALTITUDE"]=0.0
    simconnect_dict["PLANE_BEARING"]=0.0
    simconnect_dict["PLANE_PITCH_DEGREES"]=0.0
    simconnect_dict["PLANE_BANK_DEGREES"]=0.0
    simconnect_dict["SIM_ON_GROUND"] = 0
    simconnect_dict["G_FORCE_LANDING"] = "N/A"
    simconnect_dict["VERTICAL_SPEED_LANDING"] = "N/A"
    simconnect_dict["SIM_ON_GROUND_LIST"] = "N/A"
    simconnect_dict["AIRBORNE"] = 0
    simconnect_dict["ENGINE_TYPE"]=-1
    simconnect_dict["G_FORCE_LIST"] = g_force_list
    simconnect_dict["V_SPEED_LIST"] = v_speed_list
    simconnect_dict["G_FORCE_LANDING_LIST"] = "N/A"
    simconnect_dict["G_FORCE_LANDING_LIST_GROUND"] = "N/A"
    simconnect_dict["VERTICAL_SPEED_LANDING_LIST"] = "N/A"    
    simconnect_dict["VERTICAL_SPEED_LANDING_LIST_GROUND"] = "N/A"
    simconnect_dict["PLANE_ALT_ABOVE_GROUND_LIST"] = plane_alt_above_ground_list
    simconnect_dict["PLANE_ALT_ABOVE_GROUND_LIST_GROUND"] = plane_alt_above_ground_list_ground
    simconnect_dict["LANDING_RATING"] = "N/A"
    simconnect_dict["LANDING_COUNTER"] = 0
    
    # Create empty labels for charts
    labels_list = []
    for i in range(150):
        labels_list.append("")
    simconnect_dict["LABELS"] = labels_list
    
    # Run Simconnect Calculations
    while run_app == 1:
            
        # Get Current Data 
        # Fix for -999999 values
        max_g=round(aq.get("MAX_G_FORCE"),2)
        
        engine=aq.get("ENGINE_TYPE")

        wind_dir = round(aq.get("AMBIENT_WIND_DIRECTION"),2)
        if wind_dir < -99999:
            wind_dir = wind_dir_prev
        else:
            wind_dir_prev = wind_dir
        
        wind_vs = round(aq.get("AMBIENT_WIND_Y"),3)
        if wind_vs < -99999:
            wind_vs = wind_vs_prev
        else:
            wind_vs_prev = wind_vs

        wind_spd = round(aq.get("AMBIENT_WIND_VELOCITY"),2)
        if wind_spd < -99999:
            wind_spd = wind_spd_prev
        else:
            wind_spd_prev = wind_spd            

        baro = round(aq.get("BAROMETER_PRESSURE")*0.02953,2)
        if baro < -99999:
            baro = baro_prev
        else:
            baro_prev = baro

        slp = round(aq.get("SEA_LEVEL_PRESSURE")*0.02953,2)
        if slp < -99999:
            slp = slp_prev
        else:
            slp_prev = slp 

        v_speed = round(aq.get("VERTICAL_SPEED"),2)
        if v_speed < -99999:
            v_speed = v_speed_prev
        else:
            v_speed_prev = v_speed

        z_speed = round(aq.get("VELOCITY_WORLD_Z"),3)
        if z_speed < -99999:
            z_speed = z_speed_prev
        else:
            z_speed_prev = z_speed

        x_speed = round(aq.get("VELOCITY_WORLD_X"),3)
        if x_speed < -99999:
            x_speed = x_speed_prev
        else:
            x_speed_prev = x_speed

        alt  = aq.get("PLANE_ALTITUDE")
        if alt < -99999:
            alt = alt_prev
        else:
            alt_prev = alt

        gndAlt  = aq.get("PLANE_ALT_ABOVE_GROUND")
        if gndAlt < -99999:
            gndAlt = gndAlt_prev
        else:
            gndAlt_prev = gndAlt
        
        grnd_elv=round(alt-gndAlt,0)
        
        dist= aq.get("GPS_WP_DISTANCE")*0.539957

        grnd_speed = math.sqrt((z_speed*z_speed)+(x_speed*x_speed))*0.592484
        grnd_speed= round(grnd_speed,2)

        true_speed = round(aq.get("AIRSPEED_TRUE"),2)
        if true_speed < -99999:
            true_speed = true_speed_prev
        else:
            true_speed_prev = true_speed

        indi_speed = round(aq.get("AIRSPEED_INDICATED"),2)
        if indi_speed < -99999:
            indi_speed = indi_speed_prev
        else:
            indi_speed_prev = indi_speed

        mach_speed = round(aq.get("AIRSPEED_MACH"),3)
        if mach_speed < -99999:
            mach_speed = mach_speed_prev
        else:
            mach_speed_prev = mach_speed

        lat  = aq.get("PLANE_LATITUDE")
        if lat < -99999:
            lat = lat_prev
        else:
            lat_prev = lat
        
        lng  = aq.get("PLANE_LONGITUDE")
        if lng < -99999:
            lng = lng_prev
        else:
            lng_prev = lng
        
        bearing = aq.get("PLANE_HEADING_DEGREES_TRUE")
        if bearing < -99999:
            bearing = bearing_prev
        else:
            bearing_prev = bearing

        if v_speed < -99999:
            v_speed = v_speed_prev
        else:
            g_force_custom =  (round(aq.get("ACCELERATION_WORLD_Y")) / 32.2) + 1
            v_speed_prev = v_speed

        g_force = round(aq.get("G_FORCE"), 2)
        if g_force < -99999:
            g_force = g_force_prev
        else:
            g_force_prev = g_force






        plane_alt_above_ground = round(aq.get("PLANE_ALT_ABOVE_GROUND"), 1)
        if plane_alt_above_ground < -99999:
            plane_alt_above_ground = plane_alt_above_ground_prev
        else:
            plane_alt_above_ground_prev = plane_alt_above_ground

        sim_on_ground = aq.get("SIM_ON_GROUND")
        if sim_on_ground < -99999:
            sim_on_ground = sim_on_ground_prev
        else:
            sim_on_ground_prev = sim_on_ground        
               
        
        # Make lists
        sim_on_ground_list.insert(0, sim_on_ground)
        if len(sim_on_ground_list) > 31:
           sim_on_ground_list.pop()
        v_speed_list_all.insert(0, v_speed)
        if len(v_speed_list_all) > 151:
            v_speed_list_all.pop()
        g_force_list_all.insert(0, g_force)
        if len(g_force_list_all) > 151:
            g_force_list_all.pop() 
        
        # Make lists for graph - separation between airborne and landing
        if sim_on_ground == 1:
            v_speed_list.insert(0, "null")
            if len(v_speed_list) > 151:
                v_speed_list.pop() 
            g_force_list.insert(0, "null")
            if len(g_force_list) > 151:
               g_force_list.pop()
            plane_alt_above_ground_list.insert(0, "null")
            if len(plane_alt_above_ground_list) > 151:
               plane_alt_above_ground_list.pop()
            v_speed_list_ground.insert(0, v_speed)
            if len(v_speed_list_ground) > 151:
                v_speed_list_ground.pop() 
            g_force_list_ground.insert(0, g_force)
            if len(g_force_list_ground) > 151:
               g_force_list_ground.pop()
            plane_alt_above_ground_list_ground.insert(0, plane_alt_above_ground)
            if len(plane_alt_above_ground_list_ground) > 151:
               plane_alt_above_ground_list_ground.pop()
        else:
            v_speed_list.insert(0, v_speed)
            if len(v_speed_list) > 151:
                v_speed_list.pop() 
            g_force_list.insert(0, g_force)
            if len(g_force_list) > 151:
               g_force_list.pop()
            plane_alt_above_ground_list.insert(0, plane_alt_above_ground)
            if len(plane_alt_above_ground_list) > 151:
               plane_alt_above_ground_list.pop()
            v_speed_list_ground.insert(0, "null")
            if len(v_speed_list_ground) > 151:
                v_speed_list_ground.pop() 
            g_force_list_ground.insert(0, "null")
            if len(g_force_list_ground) > 151:
               g_force_list_ground.pop()
            plane_alt_above_ground_list_ground.insert(0, "null")
            if len(plane_alt_above_ground_list_ground) > 151:
               plane_alt_above_ground_list_ground.pop()
        

        # Populate vars to JSON dictionary
        simconnect_dict["ENGINE_TYPE"] = engine
        simconnect_dict["G_FORCE"] = g_force
        simconnect_dict["MAX_G_FORCE"] = max_g
        simconnect_dict["VERTICAL_SPEED"] = v_speed
        simconnect_dict["HORIZONTAL_SPEED"] = true_speed
        simconnect_dict["INDICATED_SPEED"] = indi_speed
        simconnect_dict["MACH_SPEED"] = mach_speed
        simconnect_dict["GRND_SPEED"] = grnd_speed
        simconnect_dict["WIND_SPEED"] = wind_spd
        simconnect_dict["WIND_DIR"] = wind_dir
        simconnect_dict["WIND_VS"] = wind_vs
        simconnect_dict["BARO"] = baro
        simconnect_dict["SEALEVEL"] = slp                               
        simconnect_dict["LATITUDE"] = round(lat,9)
        simconnect_dict["LONGITUDE"] = round(lng,9)
        simconnect_dict["BEARING"] = math.degrees(bearing)
        simconnect_dict["ALTITUDE"] = round(alt,1)
        simconnect_dict["GND_ALTITUDE"] = round(plane_alt_above_ground,1)
        simconnect_dict["GRND_ELEV"] = grnd_elv
        simconnect_dict["SIM_ON_GROUND"] = sim_on_ground
        simconnect_dict["AIRBORNE"] = airborne
        simconnect_dict["TARGET_DIST"] = round(dist/1000,2)
        
        # Make landing/airborne decision
        if airborne == True and sum(sim_on_ground_list) == 30:
            # Fix - need to get the last value before on ground readings
            v_speed_list_touchdown = v_speed_list_ground
            g_force_list_touchdown = g_force_list_ground
            change_last = False
            for idx, element in enumerate(v_speed_list_touchdown):
                if idx >= 1:
                    if element == 0 and v_speed_list_touchdown[idx-1] == 1:
                        if change_last == False:
                            v_speed_list_touchdown[idx] = v_speed_list[idx]
                            g_force_list_touchdown[idx] = g_force_list[idx]
                            change_last = True
                        else:
                            change_last = False
                    else:
                        change_last = False
            
            v_speed_list_touchdown = [0 if x=="null" else x for x in v_speed_list_touchdown]
            g_force_list_touchdown = [0 if x=="null" else x for x in g_force_list_touchdown]
            
            simconnect_dict["G_FORCE_LANDING"] = max(g_force_list_touchdown)
            simconnect_dict["VERTICAL_SPEED_LANDING"] = min(v_speed_list_touchdown)
            # Create Lists for Graphs
            simconnect_dict["G_FORCE_LANDING_LIST"] = g_force_list[::-1]*1
            simconnect_dict["G_FORCE_LANDING_LIST_GROUND"] = g_force_list_ground[::-1]*1
            v_speed_list_neg = [elem * (-1) if elem != "null" else "null" for elem in v_speed_list]
            v_speed_list_ground_neg = [elem * (-1) if elem != "null" else "null" for elem in v_speed_list_ground]
            simconnect_dict["VERTICAL_SPEED_LANDING_LIST"] = v_speed_list_neg[::-1]*1
            simconnect_dict["VERTICAL_SPEED_LANDING_LIST_GROUND"] = v_speed_list_ground_neg[::-1]*1
            simconnect_dict["PLANE_ALT_ABOVE_GROUND_LIST"] = plane_alt_above_ground_list[::-1]*1
            simconnect_dict["PLANE_ALT_ABOVE_GROUND_LIST_GROUND"] = plane_alt_above_ground_list_ground[::-1]*1
            simconnect_dict["LANDING_COUNTER"] = simconnect_dict["LANDING_COUNTER"] + 1
            
            # Landing Rating Based on G-Forces
            if simconnect_dict["VERTICAL_SPEED_LANDING"] > -60:
                simconnect_dict["LANDING_RATING"] = "Very soft landing"
            elif simconnect_dict["VERTICAL_SPEED_LANDING"] > -120:
                simconnect_dict["LANDING_RATING"] = "Soft landing"
            elif simconnect_dict["VERTICAL_SPEED_LANDING"] > -200:
                simconnect_dict["LANDING_RATING"] = "Average landing"
            elif simconnect_dict["VERTICAL_SPEED_LANDING"] > -300:
                simconnect_dict["LANDING_RATING"] = "Firm landing"
            elif simconnect_dict["VERTICAL_SPEED_LANDING"] > -400:
                simconnect_dict["LANDING_RATING"] = "Hard landing"
            elif simconnect_dict["VERTICAL_SPEED_LANDING"] > -600:
                simconnect_dict["LANDING_RATING"] = "Very hard landing"
            else:
                simconnect_dict["LANDING_RATING"] = "Structural damage to plane"
            airborne = False
        
        if sum(sim_on_ground_list) == 0 and airborne == False:
            airborne = True

if __name__ == "__main__":
    thread1 = Thread(target = simconnect_thread_func, args=('Thread-1', ))
    thread2 = Thread(target = flask_thread_func, args=('Thread-2', ))
    thread1.start()
    thread2.start()
        