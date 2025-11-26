import PySimpleGUI as sg
from config import WINDOW_TITLE,GUI_THEME, IMAGE_DISPLAY_SIZE,OUTPUT_DIR

sg.theme(GUI_THEME)

def create_layout():
    MODEL = ['yolo11n','yolo11s','yolo11m',
             'cs-yolo11n','cs-yolo11s','cs-yolo11m',
             'clahe-yolo11n','clahe-yolo11s','clahe-yolo11m',
             'he-yolo11n','he-yolo11s','he-yolo11m']
    
    ENHANCE = ['none','cs', 'he', 'clahe']
    
    control_panel_column = [
        [sg.Text('Deteksi Retail Yolo11', font=('Helvetica', 37, 'bold'),justification='center', expand_x=True, pad=(0,30))],

        [sg.Text('Select Model:', size=(15, 1)), 
         sg.Combo(
             values=MODEL, 
             default_value=MODEL[0],
             key='-MODEL_SELECT-', 
             enable_events=True,
             readonly=True,
             size=(20, 1)
         )],
        [sg.Text('Select Enhancement:', size=(15, 1)), 
         sg.Combo(
             values=ENHANCE, 
             default_value=ENHANCE[0],
             key='-ENHANCE_SELECT-', 
             enable_events=True,
             readonly=True,
             size=(20, 1)
         )],
        [sg.HSep()],

        [sg.Text('Image File:', size=(12, 1))],
        [sg.Input(key='-IMAGE_FILE_PATH-', enable_events=True, visible=False), 
         sg.FileBrowse('Browse Image', target='-IMAGE_FILE_PATH-', file_types=(("Image Files", "*.png *.jpg *.jpeg"),))],
        [sg.Button('Run Image Detection', key='-RUN_IMAGE_DETECTION-', size=(16, 1))],
        [sg.HSep(pad=(0, 5))],
        
        [sg.Text('Video File:', size=(12, 1))],
        [sg.Input(key='-VIDEO_FILE_PATH-', enable_events=True, visible=False), 
         sg.FileBrowse('Browse Video', target='-VIDEO_FILE_PATH-', file_types=(("Video Files", "*.mp4 *.avi"),))],
        [sg.Button('Run Video Detection', key='-RUN_VIDEO_DETECTION-', size=(16, 1))],
        [sg.HSep(pad=(0, 5))],

        [sg.Text('Object Region & Count', font='Helvetica 12 bold')],
        [sg.Button('Run Object Region & Count', key='-RUN_REGION_COUNT-', size=(25, 1))],
        [sg.Text('Objects in Region:', key='-REGION_COUNT_LABEL-', size=(20, 1)), 
         sg.Text('N/A', key='-REGION_COUNT_VALUE-', size=(5, 1), text_color='yellow')],
        [sg.HSep(pad=(0, 5))],

        [sg.Text('Status: Waiting...', size=(40, 1), key='-STATUS-', relief=sg.RELIEF_SUNKEN, text_color='yellow')],
    ]
    visualization_column = [
        [sg.Text('Detection Output', font='Helvetica 14')],
        [sg.Image(filename='', key='-DISPLAY_RESULT-', size=IMAGE_DISPLAY_SIZE, background_color='black')] 
    ]

    layout = [
        [
            sg.Column(control_panel_column,key='-CONTROL_COLUMN-', pad=(20, 40)),
            sg.VSeperator(),
            sg.Column(visualization_column, pad=(40, 20), element_justification='c')
        ]
    ]
    return layout