import json
import os

if not os.path.isfile('config.json'):
    config_data = {}
    config_data['recording_path'] = 'game_recordings'
    
    with open('config.json', 'w') as outfile:
        json.dump(config_data, outfile)

with open('config.json') as config_file:
    config = json.load(config_file)

if not os.path.isdir(config['recording_path']):
    os.mkdir(config['recording_path'])
