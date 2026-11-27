#use the jsons in playables to make the sound selector
#when adding new sounds generate them with generator.py

from classes.display import Display
from classes.sound import Sound
from json_manipulator import save_json, load_json
import time
import pygame
from pathlib import Path
import math

import subprocess
import sys

def find_matching_indexes(sounds:list[str], query:str) -> list:
    """
    Returns indexes of items where item['name'] contains all characters from `query`
    in the given order (not necessarily consecutively).
    """
    query=query.lower()
    def name_matches(name, query):
        it=iter(name.lower())
        return all(char in it for char in query)
    return [
        item for item in sounds
        if name_matches(item, query)
    ]

def load_json_files(folder_path) -> dict:
    result={}
    for file_path in Path(folder_path).glob("*.json"):
        data=load_json(file_path)

        result[data["NAME"]]={
            "PATH": data["PATH"],
            "SUBTITLE": data["SUBTITLE"]
        }
    return result

def update_fadeouts(subt: dict, el:float) -> dict:
    def get_new_value(c,el):
        if c > 1.0:
            c = max(1.0, c - 0.1 * el / FADE_START_TIME)
        if c <= 1.0:
            c = max(0.0, c - el / FADE_TIME)
        return c

    new_subt={}
    for text, alp in subt.items():
        new_alpha=get_new_value(alp,el)
        if new_alpha > 0.0:
            new_subt[text]=new_alpha
    return new_subt


FADE_START_TIME=10
FADE_TIME=5
FADE_START_VAL=1.1

UPDATE_INTERVAL=0.1
UPDATE_INTERVAL=1/60
UPDATE_INTERVAL_ERROR=UPDATE_INTERVAL/10

ROOTPATH = Path(__file__).resolve().parent
DEFINITIONS_DIR = ROOTPATH / "sounds" / "playables"
SECOND_MAIN=ROOTPATH / "second_main.py"

def main():
    save_json("D:\\Python_Projects\\sound_engine_v2\\data\\subtitles.json",{})
    save_json("D:\\Python_Projects\\sound_engine_v2\\data\\run.json",{"run":1})
    save_json("D:\\Python_Projects\\sound_engine_v2\\data\\u.json",{"u":UPDATE_INTERVAL})
    subprocess.Popen([sys.executable, SECOND_MAIN],start_new_session=True)


    display=Display(size=[800,600],frame=True,name="MAIN")
    
    run=True
    subtitles={}
    selectedIndex=0

    sounds=load_json_files(DEFINITIONS_DIR)
    soundNames=list(sounds.keys())

    soundPaths={}
    for sn in soundNames:
        soundPaths[sn]=sounds[sn]["PATH"]
    SoundE=Sound(soundPaths)
    del soundPaths
    
    typedStr=""

    lastTime=time.time()

    while run:
        matched=find_matching_indexes(soundNames,typedStr)
        matched.reverse()
        clippedMatched=matched[selectedIndex:]
        clippedMatched.insert(0,typedStr)
        run=display.tick(clippedMatched,True)
        if time.time()%UPDATE_INTERVAL<UPDATE_INTERVAL_ERROR:
            el=time.time()-lastTime
            lastTime=time.time()
            subtitles=update_fadeouts(subtitles,el)
            try:
                save_json("D:\\Python_Projects\\sound_engine_v2\\data\\subtitles.json",subtitles)
            except Exception as e:
                print("main can't write 1\nrace condition\n")
            try:
                save_json("D:\\Python_Projects\\sound_engine_v2\\data\\run.json",{"run":(1 if run else 0)})
            except Exception as e:
                print("main can't write 2\nrace condition\n")
        events=display.getEvents()
        if events!=[]:
            pass
            #print(events)
        for e in events:
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_UP:
                    selectedIndex+=1
                    if selectedIndex>len(matched)-1:
                        selectedIndex=0
                if e.key==pygame.K_DOWN:
                    selectedIndex-=1
                    if selectedIndex<0:
                        selectedIndex=len(matched)-1
                
                elif e.key==pygame.K_BACKSPACE:
                    typedStr=typedStr[:-1]
                elif e.key==pygame.K_RETURN:
                    soundName=matched[selectedIndex]
                    subtitles={sounds[soundName]["SUBTITLE"]:FADE_START_VAL,**subtitles}
                    typedStr=""
                elif e.key!=pygame.K_ESCAPE:
                    typedStr+=e.unicode

    while True:
        if time.time()%UPDATE_INTERVAL<UPDATE_INTERVAL_ERROR:
            try:
                save_json("D:\\Python_Projects\\sound_engine_v2\\data\\subtitles.json",subtitles)
            except Exception as e:
                print("main can't write 1\nrace condition\n")
            try:
                save_json("D:\\Python_Projects\\sound_engine_v2\\data\\run.json",{"run":(1 if run else 0)})
            except Exception as e:
                print("main can't write 2\nrace condition\n")
            break

if __name__ == "__main__":
    main()
