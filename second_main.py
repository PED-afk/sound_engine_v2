

from json_manipulator import load_json
import time
from classes.display import Display


def main():
    if time.time()//1%2==1:
        nextJsonUpdate=time.time()+1
    else:
        nextJsonUpdate=time.time()+2
    run=1
    subtitles={}
    display=Display()
    while run:
        if nextJsonUpdate<time.time():
            subtitles=load_json("D:\\Python_Projects\\sound_engine_v2\\data\\subtitles.json")
            run=load_json("D:\\Python_Projects\\sound_engine_v2\\data\\run.json")["run"]
            nextJsonUpdate=time.time()+1
        display.tick(subtitles)


if __name__ == "__main__":
    main()
