import cv2
from flask import Flask, render_template, Response
from simple_facerec import SimpleFacerec

# Encode faces from a folder
sfr = SimpleFacerec()


app = Flask(__name__)
# Load Camera
cap = cv2.VideoCapture(0)


def gen_frames():  # frameler şeklinde görüntüleri topluyoruz
    sfr.load_encoding_images("images/")
    while True:
        ret, frame = cap.read()
        # Detect Faces
        face_locations, face_names = sfr.detect_known_faces(frame)
        for face_loc, name in zip(face_locations, face_names):
            y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]

            cv2.putText(frame, name,(x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)
            
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


if __name__ == '__main__':
    app.run(debug=True)