import face_recognition
import cv2
import os
import glob
import numpy as np
import logging

format = "%(asctime)s : %(message)s"
logging.basicConfig(
    format=format,
    level=logging.INFO,
    datefmt="%H:%M:%S",
    filename="log.txt"
)
class SimpleFacerec:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []

        # Resize frame for a faster speed
        self.frame_resizing = 0.24

    def encoding_images(self,img_path):
        img = cv2.imread(img_path)
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Get the filename only from the initial file path.
        basename = os.path.basename(img_path)
        (filename, ext) = os.path.splitext(basename)
        # Get encoding

        img_encoding = face_recognition.face_encodings(rgb_img)
        # Store file name and file encoding
        self.known_face_encodings.append(img_encoding[0])
        self.known_face_names.append(filename)
        print('success encoding {}'.format(img_path))
        logging.info('success encoding {}'.format(img_path))

    def delete_encoding_image(self,nameperson):
        if nameperson in self.known_face_names:
            file_exists = os.path.exists('images/{}.jpg'.format(nameperson))
            if file_exists:
                index = self.known_face_names.index(nameperson)
                self.known_face_names.remove(nameperson)
                del self.known_face_encodings[index]
                os.remove('images/{}.jpg'.format(nameperson))
            return True;
        else:
            return False;
        
    def edit_encoding_image(self,nameperson,namepersonnew):
        if nameperson in self.known_face_names:
            file_exists = os.path.exists('images/{}.jpg'.format(nameperson))
            if file_exists:
                index = self.known_face_names.index(nameperson)
                self.known_face_names[index] = namepersonnew
                os.rename('images/{}.jpg'.format(nameperson),'images/{}.jpg'.format(namepersonnew))
            return True;
        else:
            return False;
        

    def load_encoding_images(self, images_path):
        """
        Load encoding images from path
        :param images_path:
        :return:
        """
        # Load Images
        images_path = glob.glob(os.path.join(images_path, "*.*"))

        print("{} encoding images found.".format(len(images_path)))

        # Store image encoding and names
        for img_path in images_path:
            self.encoding_images(img_path)
            
        print("Encoding images loaded")

    def detect_known_faces(self, frame):
        small_frame = cv2.resize(frame, (0, 0), fx=self.frame_resizing, fy=self.frame_resizing)
        # Find all the faces and face encodings in the current frame of video
        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            name = "Unknown"
            if len(self.known_face_encodings) > 0:
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)

                # # If a match was found in known_face_encodings, just use the first one.
                if os.getenv('MODE','FIRST') == 'FIRST':
                    if True in matches:
                        first_match_index = matches.index(True)
                        name = self.known_face_names[first_match_index]
                        logging.info('Found face {}'.format(name))
                    else:
                        logging.info('Unknown face')

                # Or instead, use the known face with the smallest distance to the new face
                else:
                        face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                        best_match_index = np.argmin(face_distances)
                        if matches[best_match_index]:
                            name = self.known_face_names[best_match_index]
                            logging.info('Found face {}'.format(name))
                        else :
                            logging.info('Unknown face')

            face_names.append(name)


        # Convert to numpy array to adjust coordinates with frame resizing quickly
        face_locations = np.array(face_locations)
        face_locations = face_locations / self.frame_resizing
        # fac = ''.join(face_names)
        # logging.info(fac)
        return face_locations.astype(int), face_names
