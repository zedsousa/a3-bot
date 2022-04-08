import sys
import mss
import time
import yaml
import numpy as np
from cv2 import cv2
from os import listdir

last_log_is_progress = False
stream = open("config.yaml", 'r')
c = yaml.safe_load(stream)

COLOR = {
    'blue': '\033[94m',
    'default': '\033[99m',
    'grey': '\033[90m',
    'yellow': '\033[93m',
    'black': '\033[90m',
    'cyan': '\033[96m',
    'green': '\033[92m',
    'magenta': '\033[95m',
    'white': '\033[97m',
    'red': '\033[91m'
}


#SCREEN FUNCTIONS

def screenShot(monitor_number):
    #Get a screenshot of a monitor
    with mss.mss() as sct:
        monitor = sct.monitors[monitor_number-1]
        sct_img = np.array(sct.grab(monitor))

        return sct_img[:,:,:3]

def positions(target, threshold=0.7,img = None):
    #Returns a list of positions of a target within an image
    if img is None:
        img = screenShot(c['monitor'])

    result = cv2.matchTemplate(img,target,cv2.TM_CCOEFF_NORMED)
    h = target.shape[0]
    w = target.shape[1]

    yloc, xloc = np.where(result >= threshold)

    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
    return rectangles

def findImage(img, timeout=3, threshold=0.7):
    #Search for img in the screen, if found, return True.
    start = time.time()
    has_timed_out = False
    while(not has_timed_out):
        matches = positions(img, threshold=threshold)

        if(len(matches)==0):
            has_timed_out = time.time()-start > timeout
            continue
        return True
    return False

#TARGET FUNCTIONS    
def remove_suffix(input_string, suffix):
    #Returns the input_string without the suffix
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string

def load_images(dir_path='./targets/'):
    #Loads all images from the targets folder, removes the .png suffix and returns a list of the loaded images
    file_names = listdir('./'+dir_path)
    targets = {}
    for file in file_names:
        path = dir_path + file
        targets[remove_suffix(file, '.png')] = cv2.imread(path)

    return targets

#OTHER FUNCTIONS
def logger(message, progress_indicator = False, color = 'default'):
    global last_log_is_progress
    color_formatted = COLOR.get(color.lower(), COLOR['default'])

    formatted_datetime = dateFormatted()
    formatted_message = "[{}] => {}".format(formatted_datetime, message)
    formatted_message_colored  = color_formatted + formatted_message + '\033[0m'

    
    # Start progress indicator and append dots to in subsequent progress calls
    if progress_indicator:
        if not last_log_is_progress:
            last_log_is_progress = True
            formatted_message = color_formatted + "[{}] => {}".format(formatted_datetime, '⬆️ Processing last action..')
            sys.stdout.write(formatted_message)
            sys.stdout.flush()
        else:
            sys.stdout.write(color_formatted + '.')
            sys.stdout.flush()
        return

    if last_log_is_progress:
        sys.stdout.write('\n')
        sys.stdout.flush()
        last_log_is_progress = False    

    print(formatted_message_colored)
    return True    

def dateFormatted(format = '%Y-%m-%d %H:%M:%S'):
    datetime = time.localtime()
    formatted = time.strftime(format, datetime)
    return formatted

    