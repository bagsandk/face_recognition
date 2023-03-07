import cv2,os, psutil,base64,time,sys
from flask import Flask, render_template, Response,request,jsonify
from simple_facerec import SimpleFacerec
from flask_socketio import SocketIO
from datetime import datetime
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'donsky!'
socketio = SocketIO(app, cors_allowed_origins='*')

# Encode faces from a folder
sfr = SimpleFacerec()
sfr.load_encoding_images("images/")

cs = int(os.getenv('CAMERA_SOURCE')) if os.getenv('CAMERA_SOURCE').isnumeric() else os.getenv('CAMERA_SOURCE',0) #camera source
# Load Camera
cap = cv2.VideoCapture(cs)
# cap = cv2.VideoCapture('rtsp://192.168.100.4:8080/h264.sdp')
if not cap.isOpened():
    sys.exit('Video source not found...')
else:
    print('Video source ready...')

def gen_frames(): 
    # used to record the time when we processed last frame
    prev_frame_time = 0
    new_frame_time = 0
    while True:
        ret, frame = cap.read()
        psutil.Process(os.getpid())
        memory = round(psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)
        cpu = psutil.cpu_percent()

        new_frame_time = time.time()

        # Detect Faces
        face_locations, face_names = sfr.detect_known_faces(frame)
        if not face_names:
            socketio.emit('updateSensorDataEmpty', {'date':get_current_datetime()})

        for face_loc, name in zip(face_locations, face_names):
            y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]

            # cv2.putText(frame, name,(x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
            width, height = 300, 300
            x, y = x1, y1

            crop_img = frame[y:y+height, x:x+width]
            ret, buffer = cv2.imencode('.jpg', crop_img)
            face_base64 = base64.b64encode(buffer).decode()
            r, b = cv2.imencode('.jpg', frame)
            face2_base64 = base64.b64encode(b).decode()
            socketio.emit('updateSensorData', {'object':name, 'img':face_base64, 'img2':face2_base64,  'date':get_current_datetime()})
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)
            # if name != 'Unknown':
            #     socketio.sleep(5)

            

        # Calculating the fps
        fps = 1/(new_frame_time-prev_frame_time)
        prev_frame_time = new_frame_time
        fps = int(fps)
        print('fps : {}'.format(fps))
        socketio.emit('updateSensorDataDevice', {'date':get_current_datetime(),'cpu':cpu,'memory':memory,'fps':fps})

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    if request.method == 'POST':
        data = request.get_json()
        if 'name' not in data:
            return jsonify({'message':'nama harus di isi',"status":"failed"}),400
        
        if 'img' not in data:
            return jsonify({'message':'nama harus di isi',"status":"failed"}),400
        
        if data['name'] is None or data['name'] == "" :
            return jsonify({'message':'nama harus di isi',"status":"failed"}),400
        
        name = data['name']
        file_exists = os.path.exists('images/{}.jpg'.format(name))
        if  file_exists:
            return jsonify({'message':'nama sudah digunakan',"status":"failed"}),400
        
        file = data['img']
        starter = file.find(',')
        image_data = file[starter+1:]
        image_data = bytes(image_data, encoding="ascii")
        im = Image.open(BytesIO(base64.b64decode(image_data))).convert('RGB')
        im.save('images/{}.jpg'.format(name))
        sfr.encoding_images('images/{}.jpg'.format(name))

        return jsonify({"message":"berhasil tambah data","status":"success"})

# Get current date time
def get_current_datetime():
    now = datetime.now()
    return now.strftime("%m/%d/%Y %H:%M:%S")

# Decorator for connect
@socketio.on('connect')
def connect():
    print('Client connected')

# Decorator for disconnect
@socketio.on('disconnect')
def disconnect():
    print('Client disconnected',  request.sid)

if __name__ == '__main__':
    socketio.run(app,host='0.0.0.0',port=os.getenv('PORT',5000))