

from json_manipulator import load_json
import time
from classes.display import Display


UPDATE_INTERVAL=load_json("D:\\Python_Projects\\sound_engine_v2\\data\\u.json")["u"]
UPDATE_INTERVAL_ERROR=UPDATE_INTERVAL/10

def main():
    run=1
    subtitles={}
    display=Display(size=[1000,1000],frame=True,sizable=True,name="Subtitles")
    while run==1:
        if (time.time() - UPDATE_INTERVAL / 2) % UPDATE_INTERVAL <UPDATE_INTERVAL_ERROR:
            try:
                subtitles=load_json("D:\\Python_Projects\\sound_engine_v2\\data\\subtitles.json")
            except Exception as e:
                print("second can't read 1\nrace condition\n")
            try:
                run=load_json("D:\\Python_Projects\\sound_engine_v2\\data\\run.json")["run"]
            except Exception as e:
                print("second can't read 2\nrace condition\n")
        display.tick(subtitles)


if __name__ == "__main__":
    main()
