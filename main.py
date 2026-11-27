#use the jsons in playables to make the sound selector
#when adding new sounds generate them with generator.py

from classes.display import Display
from json_manipulator import save_json, load_json
import time
import pygame
from pathlib import Path

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

def update_fadeouts(subt:dict) -> dict:
    def get_new_value(t):
        if t <= FADE_START_TIME:
            return 1.1 - (0.1 / FADE_START_TIME) * t
        elif t <= FADE_TIME:
            return 1.0 - (t - FADE_START_TIME) / (FADE_TIME - FADE_START_TIME)
        else:
            return 0.0
    newSubt={}
    for subt, alp in subt.items():
        newSubt[subt]=get_new_value(alp)
    return newSubt


FADE_TIME=5
FADE_START_TIME=10

ROOTPATH = Path(__file__).resolve().parent
DEFINITIONS_DIR = ROOTPATH / "sounds" / "playables"

def main():
    if time.time()//1%2==0:
        nextJsonUpdate=time.time()+1
    else:
        nextJsonUpdate=time.time()+2
    display=Display()
    run=True
    subtitles={}
    selectedIndex=0

    sounds=load_json_files(DEFINITIONS_DIR)
    soundNames=list(sounds.keys())
    
    typedStr=""
    while run:
        matched=find_matching_indexes(soundNames,typedStr)
        matched.reverse()
        clippedMatched=matched[selectedIndex:]
        clippedMatched.insert(0,typedStr)
        run=display.tick(clippedMatched,True)
        if nextJsonUpdate<time.time():
            save_json("D:\\Python_Projects\\sound_engine_v2\\data\\subtitles.json",subtitles)
            save_json("D:\\Python_Projects\\sound_engine_v2\\data\\run.json",{"run":(1 if run else 0)})
            nextJsonUpdate=time.time()+1
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
                    print(typedStr)
                    soundName=matched[selectedIndex]
                    subtitles[sounds[soundName]["SUBTITLE"]]=1.0
                    typedStr=""
                elif e.key!=pygame.K_ESCAPE:
                    typedStr+=e.unicode

if __name__ == "__main__":
    main()
