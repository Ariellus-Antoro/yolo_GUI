
import PySimpleGUI as sg
import threading
import cv2
import os
from ultralytics import YOLO

THREAD_EVENT_KEY = '-DETECTION_COMPLETE-'

VIDEO_COMPLETE_KEY = '-VIDEO_PROCESS_END-'

class detector:
    def __init__(self,weights_path):
        self.model = None
        self.load_model(weights_path)

    def load_model(self,weights_path):
        try:
            self.model = YOLO(weights_path)
        except Exception as e:
            raise FileNotFoundError(f"Failed to load model from {weights_path}: {e}")
        
    def file_detection(self,file_path,window,size):
        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension in ['.mp4','.avi','.mkv']:
            threading.Thread(
                target=self.run_video_detection,
                args=(file_path, window, size),
                daemon=True
            ).start()
        else:
            threading.Thread(
                target=self.run_image_detection, 
                args=(file_path, window, size), 
                daemon=True
            ).start()

    def run_image_detection(self,file_path,window,size):
        try:
            results = self.model.predict(
                source=file_path,
                conf=0.5, 
                iou=0.4, 
                imgsz=size[0], 
                verbose=False
            )

            annotated_img =results[0].plot()
            annotated_img = self.resize_image(annotated_img, size)
            img_bytes = self.cv2_to_bytes(annotated_img)
            window.write_event_value(THREAD_EVENT_KEY, {
                'success': True,
                'is_video' : False,
                'image_data': img_bytes, 
                'path': file_path
            })
        except Exception as e:
            window.write_event_value(THREAD_EVENT_KEY, {
                'success': False,
                'error': str(e),
                'path': file_path
            })

    def run_video_detection(self,file_path,window,size):
        try:
            results_generator = self.model.predict(
                source=file_path, 
                conf=0.5, 
                iou=0.4, 
                imgsz=size[0], 
                stream=True, 
                verbose=False
            )
            for result in results_generator:
                annotated_frame = result.plot()
                annotated_frame = self.resize_image(annotated_frame, size)
                img_bytes = self.cv2_to_bytes(annotated_frame)
                
                window.write_event_value(THREAD_EVENT_KEY, {
                    'success': True,
                    'is_video': True,
                    'image_data': img_bytes,
                    'path': file_path
                })
                
            window.write_event_value(VIDEO_COMPLETE_KEY, {'path': file_path})

        except Exception as e:
            window.write_event_value(THREAD_EVENT_KEY, {
                'success': False, 
                'error': str(e), 
                'path': file_path
                })

    def cv2_to_bytes(self, img, ext='.png'):
        is_success, buffer = cv2.imencode(ext, img) 
        return buffer.tobytes()

    def resize_image(self, img, size):
        target_w, target_h = size

        h, w = img.shape[:2]
        scale = min(target_w / w, target_h / h)

        new_w = int(w * scale)
        new_h = int(h * scale)

        resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

        canvas = cv2.cvtColor(
            cv2.resize(
                (255 * (img * 0)).astype("uint8"),
                (target_w, target_h)
            ),
            cv2.COLOR_BGR2RGB
        )
        
        pad_x = (target_w - new_w) // 2
        pad_y = (target_h - new_h) // 2

        canvas[pad_y:pad_y + new_h, pad_x:pad_x + new_w] = resized

        return canvas



