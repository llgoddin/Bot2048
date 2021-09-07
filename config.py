import json
import os

if not os.path.isfile('config.json'):
    CONFIG_data = {}
    CONFIG_data['recording_path'] = 'game_recordings'
    CONFIG_data['Up'] = 'w'
    CONFIG_data['Down'] = 's'
    CONFIG_data['Left'] = 'a'
    CONFIG_data['Right'] = 'd'
    
    with open('config.json', 'w') as outfile:
        json.dump(CONFIG_data, outfile)

with open('config.json') as CONFIG_file:
    CONFIG = json.load(CONFIG_file)

if not os.path.isdir(CONFIG['recording_path']):
    os.mkdir(CONFIG['recording_path'])
