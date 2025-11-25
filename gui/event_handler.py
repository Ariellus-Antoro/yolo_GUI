import os
import PySimpleGUI as sg
from detection.detector import detector,THREAD_EVENT_KEY, VIDEO_COMPLETE_KEY
from config import MODELS, IMAGE_DISPLAY_SIZE

IMAGE_INPUT_KEY = '-IMAGE_FILE_PATH-'
VIDEO_INPUT_KEY = '-VIDEO_FILE_PATH-'
RUN_IMAGE_KEY = '-RUN_IMAGE_DETECTION-'
RUN_VIDEO_KEY = '-RUN_VIDEO_DETECTION-'
MODEL_SELECT_KEY = '-MODEL_SELECT-'
DISPLAY_KEY = '-DISPLAY_RESULT-'
STATUS_KEY = '-STATUS-'


class EventHandler:
    def __init__(self,window,detector):
        self.window = window
        self.detector = detector

    def handle_model_selection(self,selected_model):
        selected_path = MODELS.get(selected_model)

        if selected_path:
            self.window[STATUS_KEY].update(f'Loading {selected_model}...')
            try:
                self.detector.load_model(selected_path) 
                self.window[STATUS_KEY].update(f'{selected_model} loaded and ready.')
            except Exception as e:
                self.window[STATUS_KEY].update(f'Error loading {selected_model}: {e}', text_color='red')
                sg.popup_error(f"Error loading model: {e}")
        
    def handle_image_selection(self,file_path):
        if file_path and os.path.exists(file_path):
            file_name = os.path.basename(file_path)
            self.window[STATUS_KEY].update(f'Image loaded : {file_name} READY', text_color='green')
        elif file_path:
            self.window[STATUS_KEY].update('Error: Selected file is not valid or doesn\'t exist.', text_color='red')
        else:
            self.window[STATUS_KEY].update('Select an image file')

    def handle_video_selection(self,file_path):
        if file_path and os.path.exists(file_path):
            file_name = os.path.basename(file_path)
            self.window[STATUS_KEY].update(f'Video loaded : {file_name} READY', text_color='green')
        elif file_path:
            self.window[STATUS_KEY].update('Error: Selected file is not valid or doesn\'t exist.', text_color='red')
        else:
            self.window[STATUS_KEY].update('Select an video file')

    def handle_run_image(self, file_path): 
        if not file_path or not os.path.exists(file_path):
            self.window[STATUS_KEY].update('Error: Please select a valid image file.')
            return

        self.window[STATUS_KEY].update(f'Processing image...')
        self.window[RUN_IMAGE_KEY].update(disabled=True)
        self.window[RUN_VIDEO_KEY].update(disabled=True)
        
        self.detector.file_detection(file_path, self.window, IMAGE_DISPLAY_SIZE)  

    def handle_run_video(self, file_path):
        if not file_path or not os.path.exists(file_path):
            self.window[STATUS_KEY].update('Error: Please select a valid video file.')
            return

        self.window[STATUS_KEY].update(f'Processing video...')
        self.window[RUN_IMAGE_KEY].update(disabled=True)
        self.window[RUN_VIDEO_KEY].update(disabled=True)
        
        self.detector.file_detection(file_path, self.window, IMAGE_DISPLAY_SIZE)   

    def handle_detection_complete(self, result_data):

        if not result_data.get('is_video', False):
            self.window[RUN_IMAGE_KEY].update(disabled=False)
            self.window[RUN_VIDEO_KEY].update(disabled=False)

        if result_data['success']:
            self.window[DISPLAY_KEY].update(data=result_data['image_data'])
            self.window[STATUS_KEY].update(f"Detection complete for {os.path.basename(result_data['path'])}.")
        else:
            self.window[STATUS_KEY].update(f"Detection failed. Error: {result_data['error']}", text_color='red')
            print(f"Detection Error: {result_data['error']}") 


    def handle(self,event,values):
        if event == MODEL_SELECT_KEY:
            self.handle_model_selection(values[MODEL_SELECT_KEY])

        elif event == IMAGE_INPUT_KEY:
            self.handle_image_selection(values[IMAGE_INPUT_KEY])

        elif event == VIDEO_INPUT_KEY:
            self.handle_video_selection(values[VIDEO_INPUT_KEY])
        
        elif event == RUN_IMAGE_KEY:
            self.handle_run_image(values[IMAGE_INPUT_KEY])
        
        elif event == RUN_VIDEO_KEY:
            self.handle_run_video(values[VIDEO_INPUT_KEY])

        elif event == THREAD_EVENT_KEY:
            self.handle_detection_complete(values[THREAD_EVENT_KEY])

        