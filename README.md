# sound_engine_v2
## old_format_fixer.py
This sript attempts to regenerate the json files in the 'old' folder. This was used once to fix them.
## generator.py
This generates .wav and .json files into 'playables' based on definitions from 'sound_defs'  
When adding new sounds use this to generate them
## main.py
This will be the main file to run to use the sound engine.  
This will have the sound selector menu.

### Notes
- __crow_caw.json__  
    Included random selection.  
    Should be made into an abiance with long pauses.  
    Requires more work than I have time for right now  
- __crow_load.json__, __flies.json__, __waves.json__  
    Same issue as previouse
- Some files with names including 'random'  
    They were originally randomized but these random selections were saved into thier definitions.  
    So now they have baked randomness.  
    This should be changed.