import os
import PySimpleGUI as sg
from detection.detector import detector,THREAD_EVENT_KEY, VIDEO_COMPLETE_KEY,REGION_COUNT_COMPLETE_KEY
from config import MODELS, IMAGE_DISPLAY_SIZE
import threading

IMAGE_INPUT_KEY = '-IMAGE_FILE_PATH-'
VIDEO_INPUT_KEY = '-VIDEO_FILE_PATH-'
RUN_IMAGE_KEY = '-RUN_IMAGE_DETECTION-'
RUN_VIDEO_KEY = '-RUN_VIDEO_DETECTION-'
MODEL_SELECT_KEY = '-MODEL_SELECT-'
DISPLAY_KEY = '-DISPLAY_RESULT-'
STATUS_KEY = '-STATUS-'
ENHANCE_MODE_KEY = '-ENHANCE_SELECT-'
RUN_REGION_COUNT_KEY = '-RUN_REGION_COUNT-'
REGION_COUNT_VALUE_KEY = '-REGION_COUNT_VALUE-'


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
            self.window[STATUS_KEY].update(f'Image loaded : {file_name} READY', text_color='orange')
        elif file_path:
            self.window[STATUS_KEY].update('Error: Selected file is not valid or doesn\'t exist.', text_color='red')
        else:
            self.window[STATUS_KEY].update('Select an image file')


    def handle_video_selection(self,file_path):
        if file_path and os.path.exists(file_path):
            file_name = os.path.basename(file_path)
            self.window[STATUS_KEY].update(f'Video loaded : {file_name} READY', text_color='orange')
        elif file_path:
            self.window[STATUS_KEY].update('Error: Selected file is not valid or doesn\'t exist.', text_color='red')
        else:
            self.window[STATUS_KEY].update('Select an video file')
    
    def handle_run_region_count(self, values):
        file_path = values.get(IMAGE_INPUT_KEY)
        is_video = False

        if not file_path or not os.path.exists(file_path):
            file_path = values.get(VIDEO_INPUT_KEY) 
            if file_path and os.path.exists(file_path):
                is_video = True
            else:
                self.window[STATUS_KEY].update('Error: Please select a valid Image or Video file.', text_color='red')
                return

        enhancement_mode = values.get(ENHANCE_MODE_KEY)

        x_min, y_min = 100, 100
        x_max, y_max = 540, 380 
        region_coords = (x_min, y_min, x_max, y_max)

        self.window[STATUS_KEY].update(f'Counting in region {region_coords}...')
        self.window[RUN_REGION_COUNT_KEY].update(disabled=True)
        self.window[REGION_COUNT_VALUE_KEY].update('...', text_color='yellow')

        if is_video:
             threading.Thread(
                target=self.detector.run_region_counting_video,
                args=(file_path, self.window, region_coords, IMAGE_DISPLAY_SIZE),
                daemon=True
            ).start()
        else:
            threading.Thread(
                target=self.detector.run_region_counting,
                args=(file_path, self.window, region_coords, IMAGE_DISPLAY_SIZE, enhancement_mode),
                daemon=True
            ).start()
    
    def handle_region_count_complete(self, result_data):
        self.window[RUN_REGION_COUNT_KEY].update(disabled=False)

        if result_data['success']:
            self.window[DISPLAY_KEY].update(data=result_data['image_data'])
            
            region_cnt = result_data['region_count']
            total_cnt = result_data['total_count']
            self.window[REGION_COUNT_VALUE_KEY].update(str(region_cnt), text_color='orange')
            
            self.window[STATUS_KEY].update(
                f"Done. Total: {total_cnt} | In Region: {region_cnt}", 
                text_color='orange'
            )
        else:
            self.window[STATUS_KEY].update(f"Error: {result_data['error']}", text_color='red')
            self.window[REGION_COUNT_VALUE_KEY].update('Err', text_color='red')

    def handle_run_image(self, values): 
        file_path = values.get(IMAGE_INPUT_KEY)
        enhancement_mode = values.get(ENHANCE_MODE_KEY)
        if not file_path or not os.path.exists(file_path):
            self.window[STATUS_KEY].update('Error: Please select a valid image file.')
            return

        self.window[STATUS_KEY].update(f'Processing image...')
        self.window[RUN_IMAGE_KEY].update(disabled=True)
        self.window[RUN_VIDEO_KEY].update(disabled=True)
        
        self.detector.file_detection(file_path, self.window, IMAGE_DISPLAY_SIZE, enhancement_mode)  

    def handle_run_video(self, file_path):
        if not file_path or not os.path.exists(file_path):
            self.window[STATUS_KEY].update('Error: Please select a valid video file.')
            return

        self.window[STATUS_KEY].update(f'Processing video...')
        self.window[RUN_IMAGE_KEY].update(disabled=True)
        self.window[RUN_VIDEO_KEY].update(disabled=True)
        
        self.detector.file_detection(file_path, self.window, IMAGE_DISPLAY_SIZE, 'none')   

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
            self.handle_run_image(values)
        
        elif event == RUN_VIDEO_KEY:
            self.handle_run_video(values[VIDEO_INPUT_KEY])

        elif event == THREAD_EVENT_KEY:
            self.handle_detection_complete(values[THREAD_EVENT_KEY])

        elif event == RUN_REGION_COUNT_KEY:
            self.handle_run_region_count(values)
            
        elif event == REGION_COUNT_COMPLETE_KEY:
            self.handle_region_count_complete(values[REGION_COUNT_COMPLETE_KEY])

        