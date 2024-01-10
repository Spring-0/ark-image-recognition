import threading
import pyautogui
import time
import ctypes


SPACEBAR_KEYCODE = 0x20
KEYEVENTF_KEYUP = 0x02
KEYEVENTF_EXTENDEDKEY = 0x01

user32 = ctypes.windll.user32

class AutoClicker:
    def __init__(self, config):
        self.config = config
        self.running = False
        self.thread = None
        
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        
    def stop(self):
        self.running = False
        if self.thread is not None:
            self.thread.join()
            
    def run(self):
        last_inventory_open = time.time()
        while self.running:
            if self.config.auto_swing['enabled']:
                action = self.config.auto_swing.get('action', 'left_click')
                if action == 'left_click':
                    pyautogui.click()
                elif action == 'space':
                    user32.keybd_event(SPACEBAR_KEYCODE, 0, KEYEVENTF_EXTENDEDKEY, 0)
                    time.sleep(0.1)
                    user32.keybd_event(SPACEBAR_KEYCODE, 0, KEYEVENTF_KEYUP, 0)
                time.sleep(self.config.auto_swing.get('swing_interval', 0.1))
            
            if time.time() - last_inventory_open > self.config.auto_drop_settings.get('drop-interval', 25):
                self.drop_items()
                last_inventory_open = time.time()
            
    def drop_items(self):
        pyautogui.press("f") # Open inventory
        time.sleep(0.2)
        
        screen_width, screen_height = pyautogui.size()
        
        region = (screen_width // 2, 0, screen_width // 2, screen_height)
        
        items = self.config.auto_drop_settings.get('items', [])
        for item in items:
            try: search_icon_location = pyautogui.locateOnScreen('assets/search_icon.png', confidence=0.9, region=region)
            except pyautogui.ImageNotFoundException: print("Debug: Could not find search icon.")
            if search_icon_location is not None:
                pyautogui.click(search_icon_location)
                time.sleep(0.05)
                pyautogui.write(item)
                
                try: drop_button_location = pyautogui.locateOnScreen('assets/drop_icon.png', confidence=0.9, region=region)
                except pyautogui.ImageNotFoundException: print("Debug: Could not find drop icon.")
                if drop_button_location is not None:
                    pyautogui.moveTo(drop_button_location)
                    time.sleep(0.05)
                    pyautogui.click()
        time.sleep(0.3)
        pyautogui.press("esc")
        time.sleep(0.3)
        print("Dropped items")
        