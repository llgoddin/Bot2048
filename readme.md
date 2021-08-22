# Terminal 2048
The objective of the game is to create the 2048 tile by combining tiles with the same number.
The tiles are multiples of 2, every turn a new tile is generated.  

## Status  
Under Development  

## Motivation
I created this project to learn more about algorithms. My first goal was to create the game and recording system. Then I used these tools to experiment with different ways of playing using an algorithm or agent.

## Controls
* Menus
    * Use the options to navigate
    * Only enter one letter at a time then press enter
    * Use q to exit from any feature to the most recent menu.

* Game
    * Use w, a, s, d as arrow keys to move up, left, down and right accordingly
    * Only type one letter per move and press enter to make the move
    * Use q to exit from game to the main menu

## Installation
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install dependencies found in requirements.txt.
Follow the instructions below to set up your virtual enviornment:

1. Create the virtual environment using python3's venv command
    >$python3 -m venv /example/path/destination/venv
    - Make sure to include /venv at the end in order to package the environment in a single directory

2. Navigate to the directory containing /venv
    >$cd /example/path/destination
3. Activate the virtual environment by calling the 'activate' script
    >$source venv/bin/activate
4. Install dependencies using the included requirements file
    >$pip install -r requirements.txt  

Next create a config file, config.json. This file only needs to contain a path for recordings to be saved.

Example config.json

```json
{
    "recording_path": "/Users/bobsmith/Documents/pythonProjects/2048Recording"
}
```

## Dependencies Used
Terminal 2048 is built with
* Pandas
* Matplotlib
* Colorama 
* Jinja 2

## Credits
Original 2048 game devloped by Gabriele Cirulli

## Author
Lucas Goddin

