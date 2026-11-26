

import random
import json

from encoder import encode, decode
from subts import get_subt_lang
from save_data import save_json

def load_json(filePath:str):
    if filePath.endswith(".json"):
        with open(filePath,"r") as f:
            return json.load(f)
    else:
        print("Incorrect file format!")
        print(f"Path was: {filePath}")
        return 1

def createPathForNumbers(folderPath,numbers,numberNames,speed):
    if speed!=1:
        speed=0
    path=[]
    wait=0.9
    j=0
    for i in range(len(numbers)):
        if numbers[i]!=' ':
            path.append([folderPath+f"combine_radio\\overw\\numbers\\{numberNames[int(numbers[i])]}.wav",1,0,j*(wait-speed*0.15)])
            j+=1
        elif speed==0:
            path.append([folderPath+f"combine_radio\\overw\\numbers\\_comma.wav",1,0,j*wait])
            j+=1
    return path

def createSubtitleForNumbers(numbers,numberNames):
    subtitle=""
    for i in range(len(numbers)):
        char=numbers[i]
        if char!=" ":
            num=int(char)
            subtitle+=numberNames[num]

            if i+1 < len(numbers) and numbers[i+1]!=" ":
                subtitle+=", "
        else:
            subtitle+="; "
    return subtitle

def createPathForWind(repeate,folderPath):
    deltaT=0
    paths=[]
    for i in range(repeate):
        paths.append([f"{folderPath}ambiance\\wind\\wind_snippet{random.randint(1,5)}.wav",1,0,deltaT])
        deltaT+=random.randint(10,30)
    return paths

def readFile(path,readingNumber=0):
    with open(path,"r") as f:
        line=f.read().strip()
        if line:
            if readingNumber==0:
                return encode(line)
            else:
                return line
    return ""

def loadSoundFromFile(folderPath,folderUNI,filePathLoad):
    global subt_sounds
    for i in load_json(filePathLoad):
        newDic={}
        newDic["NAME"]=i["NAME"]
        newDic["SUBTITLE"]=i["NAME"]
        #newDic["PATH"]=
        if i["LANG"]=="UNI":
            activeFolder=folderUNI
        else:
            activeFolder=folderPath
        paths=[]
        for j in i["PATHS"]:
            if isinstance(j["TIMES"],dict):
                times=random.randint(j["TIMES"]["min"],j["TIMES"]["max"])
            else:
                times=j["TIMES"]
            if isinstance(j["WAIT"],dict):
                wait=random.randint(j["WAIT"]["min"],j["WAIT"]["max"])
            else:
                wait=j["WAIT"]
            if isinstance(j["WAIT_BEFORE"],dict):
                wait_before=random.randint(j["WAIT_BEFORE"]["min"],j["WAIT_BEFORE"]["max"])
            else:
                wait_before=j["WAIT_BEFORE"]
            paths.append([activeFolder+j["PATH"],times,wait,wait_before])
        newDic["PATH"]=paths
        subt_sounds.append(newDic)




def load_sounds(lang,rootPath,returnq=False):
    lang=lang.upper()
    languages={
        "ENG":f"{rootPath}halflife2sounds\\sounds\\eng\\",
        "HUN":f"{rootPath}halflife2sounds\\sounds\\hun\\"
        }
    numberNamesLang={
        "ENG":["zero","one","two","three","four","five","six","seven","eight","nine"],
        "HUN":["nulla","egy","kettő","három","négy","öt","hat","hét","nyolc","kilenc"]
    }
    folderPathUNI=f"{rootPath}halflife2sounds\\sounds\\UNI\\"

    filePathEncode=f"{rootPath}halflife2sounds\\data\\ignore_in_check\\encode.txt"
    filePathLoad=f"{rootPath}halflife2sounds\\data\\subt_sound_load.json"

    if lang in languages:
        folderPath=languages[lang]
        curNumberNames=numberNamesLang[lang]
    else:
        print("Invalid language! Defaulting to ENGlish.")
        return load_sounds("ENG",rootPath)
    
    randomNumber=random.randint(0,255)
    randomWind=random.randint(1,4)
    while randomWind==3:
        randomWind=random.randint(0,4)
    
    randomNumberSequence=[]
    for i in range(random.randint(2,5)*2):
        randomNumberSequence.append(random.randint(0,9))
        if i>0 and i%2==1:
            randomNumberSequence.append(" ")

    numberSequence=["08 05 11 15 00 12 05","08 20 17 19"]
    # /|\
    #  L help me; hurt
    
    global subt_sounds
    subt_sounds=[
        #format: keys: subtitle, keep, name, path
        #It's not neccesary to specifie a subtitle here but it must be present in subts.py
        #"KEEP" doesn't have to exist. If keep is 0 or not present the subtitle will be changed to what ever is returned by get_subt_lang() else it remains what is specified here

        #path format: [["filepath",<play x times>,<wait between plays>,<wait before play>],["filepath",<play x times>,<wait between plays>,<wait before play>]]
        #if the path ends with '\\' a .wav will randomly play from that folder
        {"SUBTITLE":"Alright, you can go!","NAME":"youcango","PATH":f"{folderPath}allrightyoucango.wav"},
        {"SUBTITLE":"Welcome! Welcome to city 17!","NAME":"welcome1","PATH":f"{folderPath}characters\\breen\\br_welcome01.wav"},
        {"SUBTITLE":"You have chosen, or been chosen, to relocate to one of our finest remaining urban centers.","NAME":"welcome2","PATH":f"{folderPath}characters\\breen\\br_welcome02.wav"},
        {"SUBTITLE":"I thought so much of City 17 that I elected to establish my Administration here,...","NAME":"welcome3","PATH":f"{folderPath}characters\\breen\\br_welcome03.wav"},
        {"SUBTITLE":"...in the Citadel so thoughtfully provided by Our Benefactors.","NAME":"welcome4","PATH":f"{folderPath}characters\\breen\\br_welcome04.wav"},
        {"SUBTITLE":"I have been proud to call City 17 my home. And so, whether you are here to stay, or passing through on your way to parts unknown,...","NAME":"welcome5","PATH":f"{folderPath}characters\\breen\\br_welcome05.wav"},
        {"SUBTITLE":"...welcome to City 17.","NAME":"welcome6","PATH":f"{folderPath}characters\\breen\\br_welcome06.wav"},
        {"SUBTITLE":"It's safer here.","NAME":"welcome7","PATH":f"{folderPath}characters\\breen\\br_welcome07.wav"},
        {"SUBTITLE":"Welcome. Welcome to City 17.\nYou have chosen, or been chosen, to relocate to one of our finest remaining urban centers.\nI thought so much of City 17 that I elected to establish my Administration here,\nin the Citadel so thoughtfully provided by Our Benefactors.\nI have been proud to call City 17 my home. And so, whether you are here to stay, or passing through on your way to parts unknown,\nwelcome to City 17.\nIt's safer here.","NAME":"welcome_all","PATH":[[f"{folderPath}characters\\breen\\br_welcome01.wav",1,0,0],[f"{folderPath}characters\\breen\\br_welcome02.wav",1,0,5],[f"{folderPath}characters\\breen\\br_welcome03.wav",1,0,12],[f"{folderPath}characters\\breen\\br_welcome04.wav",1,0,20],[f"{folderPath}characters\\breen\\br_welcome05.wav",1,0,25],[f"{folderPath}characters\\breen\\br_welcome06.wav",1,0,36],[f"{folderPath}characters\\breen\\br_welcome07.wav",1,0,39.5]]},
        {"SUBTITLE":"Hahaha!","NAME":"haha","PATH":f"{folderPath}chuckle.wav"},
        {"SUBTITLE":"Hey down there! Supplies!","NAME":"supply","PATH":f"{folderPath}cit_dropper01.wav"},
        {"SUBTITLE":"Were you the only ones on that train?","NAME":"onlyyou","PATH":f"{folderPath}cit_fence_onlyones.wav"},
        {"SUBTITLE":"Don't move!","NAME":"dontmove","PATH":f"{folderPath}dontmove.wav"},
        {"SUBTITLE":"*Gunship in distance*","NAME":"gunship_far","PATH":f"{folderPathUNI}engine_rotor_loop1.wav"},
        {"SUBTITLE":"*Gunship close*","NAME":"gunship_close","PATH":f"{folderPathUNI}engine_whine_loop1.wav"},
        {"SUBTITLE":"Atention please! Unidentified person of intrest. Confirm your civil status with local protection team, immediately!","NAME":"speaker_confirm_yourself","PATH":f"{folderPath}f_confirmcivilstatus_1_spkr.wav"},
        {"SUBTITLE":"Atention please! Evasion behavior consistent with mal-compliant defendant. Ground Protection Team: alert, code: isolate, expose, administer.","NAME":"speaker_run_away","PATH":f"{folderPath}f_evasionbehavior_2_spkr.wav"},
        {"SUBTITLE":"Priority Warning. Outland stabilization force six Nova Prospekt.\nPerimeter restrictors disengaged. Priority Warning. Perimeter restrictors disengaged.","NAME":"speaker_turnedoff","PATH":f"{folderPath}fprison_perimeterrestrictors.wav"},
        {"SUBTITLE":"I have a 10-30 my 10-20 responding.","NAME":"copchatter_1","PATH":f"{folderPath}ihave10-30my10-20responding.wav"},
        {"SUBTITLE":"Officer closing on suspect.","NAME":"copchatter_closingin","PATH":f"{folderPath}officerclosingonsuspect.wav"},
        {"SUBTITLE":"Pick up that can!","NAME":"pickup_can_1","PATH":f"{folderPath}pickupthecan1.wav"},
        {"SUBTITLE":"Pick. Up. The. Can.","NAME":"pickup_can_2","PATH":f"{folderPath}pickupthecan2.wav"},
        {"SUBTITLE":"I said pick up the can!","NAME":"pickup_can_3","PATH":f"{folderPath}pickupthecan3.wav"},
        {"SUBTITLE":"*Gunship screams*","NAME":"gunship_see","PATH":f"{folderPathUNI}see_enemy.wav"},
        {"SUBTITLE":"All units, close on suspect.","NAME":"copchatter_allclosein","PATH":f"{folderPath}allunitscloseonsuspect.wav"},
        {"SUBTITLE":"All units, maintain this 'cp'","NAME":"copchatter_maintain","PATH":f"{folderPath}allunitsmaintainthiscp.wav"},
        {"SUBTITLE":"Block is holding, cohesive.","NAME":"copchatter_holding","PATH":f"{folderPath}blockisholdingcohesive.wav"},
        {"SUBTITLE":"Classify section as 'db', this block is ready for clean out.","NAME":"copchatter_blockready","PATH":f"{folderPath}classifyasdbthisblockready.wav"},
        {"SUBTITLE":"*Sniper rifle fires*","NAME":"sniper","PATH":f"{folderPathUNI}echo1.wav"},
        {"SUBTITLE":"*Manhack flies*","NAME":"manhack","PATH":[f"{folderPathUNI}mh_engine_loop1.wav",[f"{folderPathUNI}mh_blade_loop1.wav",5]]},
        {"SUBTITLE":"*Rollmine rolls*","NAME":"rollmine","PATH":[f"{folderPathUNI}rmine_moveslow_loop1.wav",[f"{folderPathUNI}rmine_blip1.wav",4,1]]},
        {"SUBTITLE":"*Siren in distance*","NAME":"alert_far","PATH":f"{folderPathUNI}scanner_alert_pass1.wav"},
        {"SUBTITLE":"*Rail-crossing bell*","NAME":"train_bell","PATH":[[f"{folderPathUNI}train_crossing_bell_loop1.wav",3],[f"{folderPathUNI}train_crossing_bell_loop1.wav",3,0,0.5]]},
        {"SUBTITLE":"*Alarm*","NAME":"alarm_bigpause","PATH":[[f"{folderPathUNI}apc_alarm_loop1.wav",4]]},
        {"SUBTITLE":"*Alarm*","NAME":"alarm_fast","PATH":f"{folderPathUNI}apc_alarm_pass1.wav"},
        {"SUBTITLE":"*Stalker breathing close*","NAME":"stalker_breath","PATH":f"{folderPathUNI}breathing3.wav"},
        {"SUBTITLE":"*Stalker screams*","NAME":"stalker_alert","PATH":f"{folderPathUNI}go_alert2.wav"},
        {"SUBTITLE":"*Stalker screams*","NAME":"stalker_alert_random","PATH":f"{folderPathUNI}stalker_scream{random.randint(1,4)}.wav"},
        {"SUBTITLE":"*Many stalker screams*","NAME":"stalker_alert_many","PATH":[[f"{folderPathUNI}stalker_scream{random.randint(1,4)}.wav",random.randint(0,3),random.randint(0,2),random.randint(0,3)],[f"{folderPathUNI}stalker_scream{random.randint(1,4)}.wav",random.randint(0,3),random.randint(0,2),random.randint(0,3)],[f"{folderPathUNI}stalker_scream{random.randint(1,4)}.wav",random.randint(0,3),random.randint(0,2),random.randint(0,3)]]},
        {"SUBTITLE":"*Strider walking*","NAME":"strider_walk","PATH":[[f"{folderPathUNI}strider_step{random.randint(1,6)}.wav",3,3,0],[f"{folderPathUNI}strider_step{random.randint(1,6)}.wav",3,3,1],[f"{folderPathUNI}strider_step{random.randint(1,6)}.wav",3,3,2]]},
        {"SUBTITLE":"*Strider alerts*","NAME":"strider_alert","PATH":f"{folderPathUNI}striderx_alert2.wav"},
        {"SUBTITLE":"*Hunter alerts*","NAME":"hunter_alert","PATH":f"{folderPathUNI}alert2.wav"},
        {"SUBTITLE":"*Hunter walks*","NAME":"hunter_walk","PATH":[[f"{folderPathUNI}ministrider_footstep5.wav",6,0,0]]},
        {"SUBTITLE":"*Hunter runs*","NAME":"hunter_run","PATH":[[f"{folderPathUNI}ministrider_footstep5.wav",8,0,0],[f"{folderPathUNI}ministrider_footstep5.wav",8,0,0.5],[f"{folderPathUNI}ministrider_footstep2.wav",1,0,4.75]]},
        {"SUBTITLE":"*Dropship in distance*","NAME":"dropship_far","PATH":[[f"{folderPathUNI}dropship_engine_distant_loop1.wav",3],[f"{folderPathUNI}dropship_engine_distant_loop1.wav",3,0,2]]},
        {"SUBTITLE":"*Dropship close*","NAME":"dropship_near","PATH":[[f"{folderPathUNI}dropship_engine_near_loop1.wav",2],[f"{folderPathUNI}dropship_engine_near_loop1.wav",2,0,2]]},
        {"SUBTITLE":"*Turret scanning*","NAME":"turret_scan","PATH":[f"{folderPathUNI}deploy.wav",[f"{folderPathUNI}retract.wav",1,0,0.6]]},
        {"SUBTITLE":"*Turret sees target*","NAME":"turret_alert","PATH":[[f"{folderPathUNI}alert.wav",1,0,0],[f"{folderPathUNI}alert.wav",1,0,0.2],[f"{folderPathUNI}alert.wav",1,0,0.4],[f"{folderPathUNI}alert.wav",1,0,0.6]]},
        {"SUBTITLE":"*Headcrab gargles*","NAME":"headcrab","PATH":f"{folderPathUNI}alert1.wav"},
        {"SUBTITLE":"*Poison headcrab rattles*","NAME":"poison_headcrab","PATH":f"{folderPathUNI}ph_warning1.wav"},
        {"SUBTITLE":"*Fast headcrab squeeks*","NAME":"fast_headcrab","PATH":f"{folderPathUNI}idle3.wav"},
        {"SUBTITLE":"*Zombie grounts*","NAME":"zombie","PATH":f"{folderPathUNI}zombie_alert1.wav"},
        {"SUBTITLE":"*Fast zombie breaths*","NAME":"fast_zombie_run","PATH":f"{folderPathUNI}breathe_loop1.wav"},
        {"SUBTITLE":"*Fast zombie screams*","NAME":"fast_zombie_scream","PATH":f"{folderPathUNI}fz_scream1.wav"},
        {"SUBTITLE":"*Poison zombie hurt*","NAME":"poison_zombie","PATH":f"{folderPathUNI}pz_pain3.wav"},
        {"SUBTITLE":"*Poison zombie calls*","NAME":"poison_zombie_call","PATH":f"{folderPathUNI}pz_call1.wav"},
        {"SUBTITLE":"*Zombine speaking*","NAME":"zombine","PATH":f"{folderPathUNI}zombine_alert2.wav"},
        {"SUBTITLE":"*Antlion scream*","NAME":"antlion","PATH":f"{folderPathUNI}distract1.wav"},
        {"SUBTITLE":"*Antlion worker screams*","NAME":"antlion_worker","PATH":f"{folderPathUNI}antlion_preburst_scream2.wav"},
        {"SUBTITLE":"*Antlion guard groands*","NAME":"antlion_guard","PATH":f"{folderPathUNI}angry3.wav"},
        {"SUBTITLE":"*Antlion guardian groands*","NAME":"antlion_guardian","PATH":f"{folderPathUNI}angry3.wav"},
        {"SUBTITLE":"*Antlion grub squeaks*","NAME":"antlion_grub","PATH":f"{folderPathUNI}agrub_stimulated{random.randint(1,3)}.wav"},
        {"SUBTITLE":"*Rocket fired and flies*","NAME":"rocket_fire","PATH":[f"{folderPathUNI}rocketfire1.wav",[f"{folderPathUNI}rocket1.wav",1,0,0.5]]},
        {"SUBTITLE":"*Train horn in distance*","NAME":"train_horn_far","PATH":f"{folderPathUNI}train_horn_distant1.wav"},
        {"SUBTITLE":"*Train passing overhead*","NAME":"train_above","PATH":f"{folderPathUNI}train_wheels_overhead_loop1.wav"},
        {"SUBTITLE":"*Train horn close*","NAME":"train_horn_close","PATH":f"{folderPathUNI}train_horn2.wav"},
        {"SUBTITLE":"*Train horn and wheels close*","NAME":"train_horn_close_wheel","PATH":[f"{folderPathUNI}train_horn2.wav",[f"{folderPathUNI}train_wheels_loop1.wav",1,0,2]]},
        {"SUBTITLE":"*Sad song*","NAME":"music_sad","PATH":f"{folderPathUNI}music\\hl2_song23_suitsong3.mp3"},
        {"SUBTITLE":"*Eerie trumpet solo from radio*","NAME":"music_creepy_radio","PATH":f"{folderPathUNI}music\\radio1.mp3"},
        {"SUBTITLE":"*Funky, upbeat music*","NAME":"music_funky","PATH":f"{folderPathUNI}music\\hl1_song25_remix3.mp3"},
        {"SUBTITLE":"*Citadel outer wall moves*","NAME":"ambiance_citadel_wall_move","PATH":[f"{folderPathUNI}ambiance\\citadel\\wall_move{random.randint(1,5)}.wav",[f"{folderPathUNI}ambiance\\citadel\\wall_crash1.wav",1,0,1]]},
        {"SUBTITLE":"*Citadel wall creaks*","NAME":"ambiance_citadel_wall","PATH":f"{folderPathUNI}ambiance\\citadel\\wall_ambient1.wav"},
        {"SUBTITLE":"*Citadel wall creaks loudly*","NAME":"ambiance_citadel_wall_loud","PATH":f"{folderPathUNI}ambiance\\citadel\\wall_ambient_loop1.wav"},
        {"SUBTITLE":"*Big fire crackles*","NAME":"ambiance_fire_big","PATH":f"{folderPathUNI}ambiance\\fire\\fire_big_loop1.wav"},
        {"SUBTITLE":"*Medium fire crackles*","NAME":"ambiance_fire_medium","PATH":f"{folderPathUNI}ambiance\\fire\\fire_med_loop1.wav"},
        {"SUBTITLE":"*Small fire crackles*","NAME":"ambiance_fire_small","PATH":f"{folderPathUNI}ambiance\\fire\\fire_small_loop{random.randint(1,2)}.wav"},
        {"SUBTITLE":"*Explosion far*","NAME":"explosion_far","PATH":f"{folderPathUNI}ambiance\\explosion\\exp{random.randint(1,4)}.wav"},
        {"SUBTITLE":"*Explosion close*","NAME":"explosion_close","PATH":f"{folderPathUNI}ambiance\\explosion\\explode_{random.randint(1,9)}.wav"},
        {"SUBTITLE":"*Flies buzzing*","NAME":"flies","PATH":[[f"{folderPathUNI}creatures\\flies\\",4,0,0]]},
        {"SUBTITLE":"*crow screams*","NAME":"crow_loud","PATH":f"{folderPathUNI}creatures\\crow\\loud\\"},
        {"SUBTITLE":"*crow caws*","NAME":"crow_caw","PATH":f"{folderPathUNI}creatures\\crow\\speak\\"},
        {"SUBTITLE":"*barnacle exists*","NAME":"barnacle","PATH":[[f"{folderPathUNI}creatures\\barnacle\\barnacle_bark{random.randint(1,2)}.wav",1],[f"{folderPathUNI}creatures\\barnacle\\barnacle_tongue_pull{random.randint(1,3)}.wav",4,0,1],[f"{folderPathUNI}creatures\\barnacle\\barnacle_crunch{random.randint(2,3)}.wav",4,0,3]]},
        {"SUBTITLE":f"{curNumberNames[randomNumber%10]}","KEEP":1,"NAME":"number_random","PATH":f"{folderPath}combine_radio\\overw\\numbers\\{curNumberNames[randomNumber%10]}.wav"},
        
        {"SUBTITLE":createSubtitleForNumbers(randomNumberSequence,curNumberNames),"KEEP":1,"NAME":"number_random_sequence","PATH":createPathForNumbers(folderPath,randomNumberSequence,numberNamesLang["ENG"],0)},
        {"SUBTITLE":createSubtitleForNumbers(numberSequence[0],curNumberNames),"KEEP":1,"NAME":"number_sequence_0","PATH":createPathForNumbers(folderPath,numberSequence[0],numberNamesLang["ENG"],0)},
        {"SUBTITLE":createSubtitleForNumbers(numberSequence[1],curNumberNames),"KEEP":1,"NAME":"number_sequence_1","PATH":createPathForNumbers(folderPath,numberSequence[1],numberNamesLang["ENG"],0)},

        {"SUBTITLE":createSubtitleForNumbers(readFile(filePathEncode),curNumberNames),"KEEP":1,"NAME":"number_sequence_file","PATH":createPathForNumbers(folderPath,readFile(filePathEncode),numberNamesLang["ENG"],0)},
        {"SUBTITLE":createSubtitleForNumbers(readFile(filePathEncode),curNumberNames),"KEEP":1,"NAME":"number_sequence_file_fast","PATH":createPathForNumbers(folderPath,readFile(filePathEncode),numberNamesLang["ENG"],1)},

        {"SUBTITLE":createSubtitleForNumbers(readFile(filePathEncode,1),curNumberNames),"KEEP":1,"NAME":"number_sequence_file_number","PATH":createPathForNumbers(folderPath,readFile(filePathEncode,1),numberNamesLang["ENG"],0)},
        {"SUBTITLE":createSubtitleForNumbers(readFile(filePathEncode,1),curNumberNames),"KEEP":1,"NAME":"number_sequence_file_number_fast","PATH":createPathForNumbers(folderPath,readFile(filePathEncode,1),numberNamesLang["ENG"],1)},
        #19 05 18 19
        {"SUBTITLE":"*wind*","NAME":"wind_ambiance","PATH":f"{folderPathUNI}ambiance\\wind\\wasteland_wind.wav"},
        {"SUBTITLE":"*wind whistle*","NAME":"wind_whistle","PATH":f"{folderPathUNI}ambiance\\wind\\wind_med{random.randint(1,2)}.wav"},
        {"SUBTITLE":"*strong wind*","NAME":"wind_storm","PATH":f"{folderPathUNI}ambiance\\wind\\wind_hit{random.randint(1,3)}.wav"},
        {"SUBTITLE":"*wind deep whistle*","NAME":"wind_moan","PATH":f"{folderPathUNI}ambiance\\wind\\wind_moan{randomWind}.wav"},

        {"SUBTITLE":"*wind*","NAME":"wind_loop","PATH":[[f"{folderPathUNI}ambiance\\wind\\wind_rooftop1.wav",4,0,0]]},
        {"SUBTITLE":"*wind*","NAME":"wind_random","PATH":f"{folderPathUNI}ambiance\\wind\\wind_snippet{random.randint(1,5)}.wav"},
        {"SUBTITLE":"*wind*","NAME":"wind_random_long","PATH":createPathForWind(random.randint(3,6),folderPathUNI)},

        {"SUBTITLE":"*wind hums*","NAME":"wind_low_hum","PATH":f"{folderPathUNI}ambiance\\wind\\wind_tunnel1.wav"},
        {"SUBTITLE":"*wind*","NAME":"wind_long","PATH":f"{folderPathUNI}ambiance\\wind\\wind1.wav"},
        {"SUBTITLE":"*wind*","NAME":"wind_strong","PATH":f"{folderPathUNI}ambiance\\wind\\windgust.wav"},
        {"SUBTITLE":"*wind*","NAME":"wind_stronger","PATH":f"{folderPathUNI}ambiance\\wind\\windgust_strong.wav"},


        {"SUBTITLE":"*water dripps*","NAME":"drip_echo","PATH":f"{folderPathUNI}ambiance\\water\\corridor_water.wav"},
        {"SUBTITLE":"*water splashes*","NAME":"drip_echo","PATH":f"{folderPathUNI}ambiance\\water\\water_splash{random.randint(1,3)}.wav"},
        {"SUBTITLE":"*wave crashes*","NAME":"waves","PATH":f"{folderPathUNI}ambiance\\water\\wave\\"},
        #"filepath",play,wait,wait before
    ]
    
    loadSoundFromFile(folderPath,folderPathUNI,filePathLoad)

    #corrrect subtitles based on language
    if returnq: return subt_sounds
    correct_subt=get_subt_lang(lang)
    for i in range(len(subt_sounds)):
        if "KEEP" not in subt_sounds[i] or subt_sounds[i]["KEEP"]!=1:
            subt_sounds[i]["SUBTITLE"]=correct_subt[subt_sounds[i]["NAME"]]

    return subt_sounds