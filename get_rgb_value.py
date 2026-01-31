import pyautogui
import keyboard
import time

print("Press F to get pixel location and RGB value")

while True:
    if keyboard.is_pressed('f'):
        x, y = pyautogui.position()
        rgb = pyautogui.pixel(x, y)
        print(f"{x}, {y} = {rgb}")
        time.sleep(0.3)

    elif keyboard.is_pressed('esc'):
        print("Exiting")
        breakf