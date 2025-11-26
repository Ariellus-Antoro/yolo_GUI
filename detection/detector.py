
import PySimpleGUI as sg
import threading
import cv2
import os
from ultralytics import YOLO
import numpy as np

THREAD_EVENT_KEY = '-DETECTION_COMPLETE-'
VIDEO_COMPLETE_KEY = '-VIDEO_PROCESS_END-'
REGION_COUNT_COMPLETE_KEY = '-REGION_COUNT_COMPLETE-'

class detector:
    def __init__(self,weights_path):
        self.model = None
        self.load_model(weights_path)

    def load_model(self,weights_path):
        try:
            self.model = YOLO(weights_path)
        except Exception as e:
            raise FileNotFoundError(f"Failed to load model from {weights_path}: {e}")
        
    def file_detection(self,file_path,window,size,enhancement_mode):
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
                args=(file_path, window, size, enhancement_mode), 
                daemon=True
            ).start()
    
    def annotate_region_frame(self, frame, results, region_coords):
        x_min_r, y_min_r, x_max_r, y_max_r = region_coords
        
        result = results[0]
        boxes = result.boxes.cpu().numpy()
        
        total_count = len(boxes)
        region_count = 0
        
        annotated_frame = frame.copy()
        class_names = self.model.names if self.model and hasattr(self.model, 'names') else {i: f'class_{i}' for i in range(100)}
        
        region_class_counts = {}

        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].astype(int)
            cls = int(box.cls[0])
            label = class_names.get(cls, f'Unknown {cls}')
            
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            is_in_region = (center_x >= x_min_r and center_x <= x_max_r and
                            center_y >= y_min_r and center_y <= y_max_r)
            color = (0, 255, 0) if is_in_region else (0, 0, 255)
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)

            if is_in_region:
                region_count += 1
                region_class_counts[label] = region_class_counts.get(label, 0) + 1

        cv2.rectangle(annotated_frame, (x_min_r, y_min_r), (x_max_r, y_max_r), (255, 0, 0), 3)

        count_text = f"Total: {total_count} | In Region: {region_count}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.0
        thickness = 2
        (text_w, text_h), baseline = cv2.getTextSize(count_text, font, font_scale, thickness)
        
        cv2.rectangle(annotated_frame, (10, 10), (10 + text_w + 20, 10 + text_h + 20), (0, 0, 0), -1)
        cv2.putText(annotated_frame, count_text, (20, 10 + text_h + 5), font, font_scale, (255, 255, 255), thickness)

        return annotated_frame, total_count, region_count, region_class_counts

    def run_region_counting(self, file_path, window, region_coords, size, enhancement_mode):
        try:
            img_raw = cv2.imread(file_path)
            if img_raw is None: raise FileNotFoundError(f"Could not read file: {file_path}")
            
            enhanced_img = self.apply_enhancement(img_raw, enhancement_mode)

            results = self.model.predict(source=enhanced_img, conf=0.5, iou=0.4, imgsz=640, verbose=False)

            annotated_img, total, region, r_counts = self.annotate_region_frame(enhanced_img, results, region_coords)

            annotated_img_resized = self.resize_image(annotated_img, size)
            img_bytes = self.cv2_to_bytes(annotated_img_resized)

            window.write_event_value(REGION_COUNT_COMPLETE_KEY, {
                'success': True,
                'image_data': img_bytes,
                'total_count': total,
                'region_count': region,
                'path': file_path
            })
        except Exception as e:
            window.write_event_value(REGION_COUNT_COMPLETE_KEY, {'success': False, 'error': str(e)})
        
    def run_region_counting_video(self, file_path, window, region_coords, size):
        try:
            results_generator = self.model.predict(source=file_path, conf=0.5, iou=0.4, imgsz=640, stream=True, verbose=False)
            
            for results in results_generator:
                frame = results.orig_img
                
                annotated_frame, total, region, r_counts = self.annotate_region_frame(frame, [results], region_coords)
                
                annotated_frame_resized = self.resize_image(annotated_frame, size)
                img_bytes = self.cv2_to_bytes(annotated_frame_resized)

                window.write_event_value(REGION_COUNT_COMPLETE_KEY, {
                    'success': True,
                    'image_data': img_bytes,
                    'total_count': total,
                    'region_count': region,
                    'path': file_path
                })
        
            window.write_event_value(VIDEO_COMPLETE_KEY, {'path': file_path})

        except Exception as e:
             window.write_event_value(REGION_COUNT_COMPLETE_KEY, {'success': False, 'error': str(e)})

    def apply_enhancement(self, image, mode):
        if image is None:
            return None

        if mode == 'none':
            return image

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        if mode == 'he':
            ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
            y = ycrcb[:, :, 0]
            ycrcb[:, :, 0] = cv2.equalizeHist(y)
            return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)

        elif mode == 'clahe':
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
            y = ycrcb[:, :, 0]
            ycrcb[:, :, 0] = clahe.apply(y)
            return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)

        elif mode == 'cs':  
            min_val = image.min()
            max_val = image.max()

            if max_val == min_val: 
                return image

            stretched = (image - min_val) * (255.0 / (max_val - min_val))
            return stretched.astype("uint8")

        return image

    def run_image_detection(self,file_path,window,size, enhancement_mode):
        try:
            img_raw = cv2.imread(file_path)
            if img_raw is None:
                raise FileNotFoundError(f"Could not read file: {file_path}")
            
            enhanced_img = self.apply_enhancement(img_raw,enhancement_mode)

            results = self.model.predict(
                source=enhanced_img,
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



