import PySimpleGUI as sg
from config import WINDOW_TITLE,GUI_THEME, IMAGE_DISPLAY_SIZE,OUTPUT_DIR

sg.theme(GUI_THEME)

def create_layout():
    MODEL = ['yolo11n','yolo11s','yolo11m']
    control_panel_column = [
        [sg.Text('Deteksi Yolo11', font=('Helvetica', 37, 'bold'),justification='center', expand_x=True, pad=(0,30))],

        [sg.Text('Select Model:', size=(15, 1)), 
         sg.Combo(
             values=MODEL, 
             default_value=MODEL[0],
             key='-MODEL_SELECT-', 
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

        [sg.Text('Status: Waiting...', size=(40, 1), key='-STATUS-', relief=sg.RELIEF_SUNKEN, text_color='yellow')],
        
        [sg.Text(f'Output Saved To: {OUTPUT_DIR}', font='_ 8')],
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

if __name__ == '__main__':
    sg.theme(GUI_THEME)
    window = sg.Window("Layout Preview", create_layout(), finalize=True)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
    window.close()