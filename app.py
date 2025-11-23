import PySimpleGUI as sg
import os
from config import GUI_THEME, WINDOW_TITLE,MODELS
from detection.detector import detector, THREAD_EVENT_KEY
from gui.layout import create_layout
from gui.event_handler import EventHandler
import tkinter.filedialog

STATUS_KEY = '-STATUS-'

def main():
    sg.theme(GUI_THEME)
    window = sg.Window(WINDOW_TITLE, create_layout(), finalize=True)

    window.extend_layout(
        window['-CONTROL_COLUMN-'], 
        [[
            sg.Text('Status: Initializing...', 
                    size=(40, 1), 
                    key=STATUS_KEY, 
                    relief=sg.RELIEF_SUNKEN)
                    ]])
    
    try:
        selected_model_path = MODELS.get(window['-MODEL_SELECT-'].get())
        if not selected_model_path:
            raise ValueError("Default model key not found")
        
        yolo_detector = detector(selected_model_path)
        window[STATUS_KEY].update(f'Default model loaded and ready.')
    except Exception as e:
        sg.popup_error(f"Application failed to start: {e}")
        return
    
    handler = EventHandler(window,yolo_detector)

    while True:
        event, values = window.read(timeout=100) 
        if event == sg.WIN_CLOSED:
            break
    
        handler.handle(event, values)

    window.close()

if __name__ == '__main__':
    main()