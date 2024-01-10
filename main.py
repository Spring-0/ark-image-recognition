import cv2
import numpy as np
from PIL import ImageGrab
import time
from config import Config
import pyautogui
from autoclicker import AutoClicker
import threading
import pygetwindow as gw
import keyboard
  
play = True
config = Config("config/config.json")
auto_clicker = AutoClicker(config)

def start_clicker():
    auto_clicker.start()

def stop_program():
    print("Stopping program")
    auto_clicker.stop()
    stop = False
    exit(0)

keyboard.add_hotkey('f12', stop_program)

clicker_thread = threading.Thread(target=start_clicker)
clicker_thread.start()

def no_food():
    print("No food")

def no_stamina():
    print("No stamina")
    auto_clicker.stop()
    time.sleep(config.regain_stamina.get('pause_duration', 0))
    print("Regained stamina")
    auto_clicker.start()
    
def no_water():
    print("No water")
    slots = config.auto_eat_slots
    if 'water' in slots:
        pyautogui.press(str(slots['water']))
        time.sleep(0.5)
    if 'food' in slots:
        pyautogui.press(str(slots['food']))
        time.sleep(0.5)
    print("Consumed food & water")

actions = [no_stamina, no_water]


def detect_red_in_image(image):
    # Convert BGR to HSV
    img_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_red = np.array([0, 50, 50])
    upper_red = np.array([10, 255, 255])
    mask0 = cv2.inRange(img_hsv, lower_red, upper_red)

    lower_red = np.array([170, 50, 50])
    upper_red = np.array([180, 255, 255])
    mask1 = cv2.inRange(img_hsv, lower_red, upper_red)

    mask = mask0 + mask1

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    min_contour_area = 500  # Min contour area to keep
    large_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_contour_area]

    large_mask = np.zeros_like(mask)
    cv2.drawContours(large_mask, large_contours, -1, 255, thickness=cv2.FILLED)

    res = cv2.bitwise_and(image, image, mask=large_mask)

    cv2.imwrite('red_detected.png', res)

    return res, large_contours

if __name__ == "__main__":
    time.sleep(2)
    screen_width, screen_height = pyautogui.size()
    
    window = gw.getWindowsWithTitle("ArkAscended")[0]
    right_region = (window.left, window.top, window.width, window.height)

    template2 = cv2.imread('assets/no_stamina.png')
    template3 = cv2.imread('assets/no_water.png')
    templates = [template2, template3]

    while play:
        screenshot = ImageGrab.grab(right_region)
        screenshot_np = np.array(screenshot)
        screenshot_np = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

        red_detected, contours = detect_red_in_image(screenshot_np)
        
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)

            # Cropped contour
            cropped = red_detected[y:y+h, x:x+w]

            for template, action in zip(templates, actions):
                try:
                    result = cv2.matchTemplate(cropped, template, cv2.TM_CCOEFF_NORMED)
                    _, max_val, _, max_loc = cv2.minMaxLoc(result)
                    if max_val > 0.9:  # threshold
                        action()
                except:
                    pass

        time.sleep(0.5)
