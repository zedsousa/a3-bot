import time
import pyautogui
import telegram_send
import yaml
from src import load_images, findImage, logger

images = load_images()
stream = open("config.yaml", 'r')
c = yaml.safe_load(stream)

def sendImageToTelegram():
    logger('🔎 Looking for headstone on screen')
    if findImage(images['dead']):
        logger('📸 Taking a screenshot of the game')  
        myScreenshot = pyautogui.screenshot()
        myScreenshot.save(r'map_image.png')
        map_image = open('map_image.png', 'rb')

        logger('🗺️ Sending game image to telegram: ')
        telegram_send.send(images=[map_image])    

def main():
    
    last = {
        "sendImage":0
    } 

    while True:
        now = time.time()
        if now - last["sendImage"] > c['countdown']:
            last["sendImage"] = now
            
            sendImageToTelegram()
  
if __name__ == '__main__':
   
    main()
