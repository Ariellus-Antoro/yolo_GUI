import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR,'yolo_models')
OUTPUT_DIR = os.path.join(BASE_DIR,'runs')

MODELS ={
    'yolo11n' : os.path.join(MODELS_DIR,'yolo11n','best.pt'),
    'yolo11s' : os.path.join(MODELS_DIR,'yolo11s','best.pt'),
    'yolo11m' : os.path.join(MODELS_DIR,'yolo11m','best.pt')
}

WINDOW_TITLE = "Kelompok 3 TR Deep Learning E"
GUI_THEME = 'DarkGrey5'
IMAGE_DISPLAY_SIZE = (640, 480)