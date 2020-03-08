# Lucas Goddin
# testing
# Feb 24, 2020

import time
import pyautogui

Screen_Width, Screen_Height = pyautogui.size()
print(str(Screen_Width) + ", " + str(Screen_Height))

erase = False

# dataFile = open("Point.txt", "r+")

# time.sleep(5)
if not erase:
    pyautogui.moveTo(25, 307, duration=0.25)
else:
    pyautogui.moveTo(25, 200)
pyautogui.click()
pyautogui.click()
pyautogui.moveTo(130, 150, duration=0.25)
pyautogui.click()

distance = 100
pause = .025
while distance > 0:
    pyautogui.dragRel(distance, 0, duration=pause, button='left')
    distance -= 5
    pyautogui.dragRel(0, distance, duration=pause, button='left')
    pyautogui.dragRel(-distance, 0, duration=pause, button='left')
    distance -= 5
    pyautogui.dragRel(0, -distance, duration=pause, button='left')

try:
    time.sleep(5)
    print("Go!")
    while True:
        posOutput = pyautogui.position()
        print(str(posOutput), end='')
        out = str(posOutput)
        # dataFile.write(out + '\n')
        time.sleep(.02)
        print('\b' * len(out), end='', flush=True)
except KeyboardInterrupt:
    print('\nDone')
