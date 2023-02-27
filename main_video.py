import cv2
from flask import Flask, render_template, Response,request
from simple_facerec import SimpleFacerec
import sys
from random import random
from flask_socketio import SocketIO
from threading import Lock
from datetime import datetime
import os, psutil,base64

thread = None
thread_lock = Lock()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'donsky!'
socketio = SocketIO(app, cors_allowed_origins='*')

# Encode faces from a folder
sfr = SimpleFacerec()
sfr.load_encoding_images("images/")

# Load Camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    sys.exit('Video source not found...')
else:
    print('Video source ready...')

def gen_frames():  # frameler şeklinde görüntüleri topluyoruz
    while True:
        ret, frame = cap.read()
        fps = cap.get(cv2.CAP_PROP_FPS)
        process = psutil.Process(os.getpid())
        memory = round(psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)
        cpu = psutil.cpu_percent()
        socketio.emit('updateSensorDataDevice', {'date':get_current_datetime(),'cpu':cpu,'memory':memory,'fps':fps})

        # Detect Faces
        face_locations, face_names = sfr.detect_known_faces(frame)
        if not face_names:
            socketio.emit('updateSensorDataEmpty', {'date':get_current_datetime()})

        for face_loc, name in zip(face_locations, face_names):
            y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]

            # cv2.putText(frame, name,(x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
            width, height = 200, 200
            x, y = x1, y1

            crop_img = frame[y:y+height, x:x+width]
            ret, buffer = cv2.imencode('.jpg', crop_img)
            face_base64 = base64.b64encode(buffer).decode()
            socketio.emit('updateSensorData', {'object':name, 'img':face_base64, 'date':get_current_datetime()})
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)
            
        socketio.sleep(1)
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


@app.route('/video_feed')
def video_feed():
    #outputu stream ediyoruz :
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    """Real Time Object Detection v3."""
    return render_template("index.html")



"""
Get current date time
"""
def get_current_datetime():
    now = datetime.now()
    return now.strftime("%m/%d/%Y %H:%M:%S")

"""
Generate random sequence of dummy sensor values and send it to our clients
"""


"""
Decorator for connect
"""
@socketio.on('connect')
def connect():
    print('Client connected')

"""
Decorator for disconnect
"""
@socketio.on('disconnect')
def disconnect():
    print('Client disconnected',  request.sid)


if __name__ == '__main__':
    socketio.run(app)