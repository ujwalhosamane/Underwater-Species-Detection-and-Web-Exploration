from flask import Flask, render_template, jsonify, request, Response, send_from_directory
import os
import time
import json
from ultralytics import YOLO
import os
import cv2
import time
import numpy as np
from keras.models import model_from_json
import re

import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

class wiki:

    def __init__(self,title):

        print("Page is loading...\n")
        self.title = str(title.title())

        self.url = 'https://en' + '.wikipedia.org/wiki/' + self.title 

        self.page = requests.get(self.url)

        self.contents = self.page.content
        self.soup = BeautifulSoup(self.contents, 'html.parser')

        self.wordcorpus = self.soup.find_all('p') 
        self.wordcorpus2 = self.soup.find_all('li')

        self.para=[]
        for paragraph in self.wordcorpus: 
            self.para.append(paragraph)

        self.relatedtopic = ",*RELATED WIKI TOPIC*" 
        for paragraph in self.wordcorpus2:
            if str(paragraph).find('<li><a href=') != -1:
                if str(paragraph).find('</a></li>') != -1 or str(paragraph).find('</a></sup></li>') != -1:
                    self.para.append(self.relatedtopic)
            if str(paragraph).find('toctext') == -1:
                self.para.append(paragraph)

        self.troubleshoot = self.para

        self.para = list(str(self.para)) 

        self.start = 0 
        self.end = 0 
        self.first = 1 
        self.bracket = 0 
        self.li = 0 
        self.p = 0 
        self.point = 0 
        self.para2 = []
        for letter in self.para:
            if self.first == 0:
                if letter == '<':
                    self.start = 1
                elif letter == '>':
                    self.start = 0
                    self.end = 1
                elif self.end == 1 and letter == ',':
                    self.end = 0
                    continue
                elif letter == '[':
                    self.bracket = 1
                    self.end = 0
                elif letter == ']':
                    self.bracket = 0
                    self.end = 0
                elif self.start == 0 and self.bracket == 0:
                    self.end = 0
                    if self.point == 1:
                        self.para2.append('• ')
                        self.point = 0
                    self.para2.append(letter)
            if letter == '<':
                self.li = 1
            elif letter != 'l' and self.li == 1:
                self.li = 0
            elif letter == 'l' and self.li == 1:
                self.li = 2
            elif letter == 'i' and self.li == 2:
                self.li = 3
            elif letter != '>' and self.li == 3:
                self.li = 0
            elif letter == '>' and self.li == 3:
                self.para2.append('\n\n')
                self.li = 0
                self.point = 1
            if letter == '<':
                self.p = 1
            elif letter != 'p' and self.p == 1:
                self.p = 0
            elif letter == 'p' and self.p == 1:
                self.p = 2
            elif letter == '>' and self.p == 2:
                self.para2.append('\n')
                self.p = 0
            self.first = 0

        self.para2 =''.join(self.para2)

        self.para = []

        self.missing = self.soup.find_all('b')

        self.goodsite = 1
        self.offsite = 0

        for sentence in self.wordcorpus:
            if str(sentence).find("refer to:") != -1:
                self.offsite = 1

        for sentence in self.missing:
            if str(sentence) == "<b>Wikipedia does not have an article with this exact name.</b>":
                self.goodsite = 0 

        if self.goodsite == 1 and self.offsite == 0:
            print('Wikipedia page loaded successfully!!')

            self.parashort = []
            self.noofpara = 0
            for paragraph in self.wordcorpus: 
                if self.noofpara < 6 and str(paragraph) != '<p class="mw-empty-elt">\n</p>' and len(str(paragraph)) > 199:
                    self.parashort.append(paragraph)
                    self.noofpara += 1

            self.parashort2 = self.__cleantext_summary(self.parashort)

            self.parashort = []

            print(self.parashort2)

        elif self.goodsite == 1 and self.offsite == 1:
            print('\nThe title "'+ self.title.replace("_", " ") + '" you specified is ambiguous. As a result, you are linked to a clarification page.\n\n')
            print('Here are some suggestions to use: \n')

            self.all_links = self.soup.find_all("a")
            self.wiktwords = []
            for link in self.all_links:
                self.wiktwords.append(link.get("title"))

            self.cleanlink = []
            for words in self.wiktwords:
                self.words2 = str(words)
                self.cleanlink.append(self.words2)

            for link in self.cleanlink:
                if link.find("Help:") != -1:
                    break
                elif link.find("Edit section:") != -1:
                    continue
                else:
                    print(link)

        else:
            print('Wikipedia page could not be found for "' + str(self.title.replace("_", " ")) + '". Please try again!')
            print('Other useful information: Enclose title argument with single quotes. Spaces are allowed, and title is case insensitive.')


    def __cleantext_summary(self, corpus):
        '''Gets summary of the text, internal method'''
        corpus = list(str(corpus))
        start = 0
        end = 0
        first = 1
        bracket = 0
        li = 0
        p = 0
        corpus2 = []
        for letter in corpus:
            if first == 0:
                if letter == '<': 
                    start = 1
                elif letter == '>': 
                    start = 0
                    end = 1
                elif end == 1 and letter == ',': 
                    end = 0
                    continue
                elif letter == '[':
                    bracket = 1
                    end = 0
                elif letter == ']':
                    bracket = 0
                    end = 0
                elif start == 0 and bracket == 0:
                    end = 0
                    corpus2.append(letter)
            if letter == '<':
                p = 1
            elif letter != 'p' and p == 1:
                p = 0
            elif letter == 'p' and p == 1:
                p = 2
            elif letter == '>' and p == 2:
                corpus2.append('<br><br>')
                p = 0
            first = 0 

        corpus2 = ''.join(corpus2)
        if ".mw-parser-output" in corpus2:
            pattern = r'^.?\n\n.?\n\n'
            corpus2 = re.sub(pattern, '', corpus2, count=1, flags=re.DOTALL)
            corpus2 = corpus2.strip()
        return corpus2
    
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/videos/<path:filename>')
def videos_files(filename):
    return send_from_directory('videos', filename)
# Route to serve the HTML page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle the upload of the first video
@app.route('/upload_video', methods=['POST'])
def upload_video():
    clear_videos_directory('./videos')
    global filePath
    global fileName
    video_file = request.files['videoFile']
    video_filename = "Video.mp4"
    fileName = video_filename
    video_location = os.path.join('videos', video_filename)
    video_file.save(video_location)
    filePath = "\\" + video_location
    return jsonify({'videoLocation': '/' + video_location})

def clear_videos_directory(static_directory):
    for file_name in os.listdir(static_directory):
        file_path = os.path.join(static_directory, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)

@app.route('/get_second_video_location')
def get_second_video_location():
    return Response(generate_progress(), mimetype='text/event-stream')

def preprocess(x):
    # [0,255] -> [-1, 1]
    return (x/127.5)-1.0

def deprocess_uint8(x):
    # [-1,1] -> np.uint8 [0, 255]
    im = ((x+1.0)*127.5)
    return np.uint8(im) 

def generate_progress():
    frame_count = 0
    results_list = []

    video = cv2.VideoCapture('./videos/'+fileName)
    numberOfFrames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = video.get(cv2.CAP_PROP_FPS)

    print("\n\n\n\n\n\n\n")
    print('./videos/'+fileName)
    print(fps)
    print(numberOfFrames)
    print("\n\n\n\n\n\n\n")
    i = 0
    success = True
    frames = []
    while success:
        success, image = video.read()
        if success:
            height, width, _ = image.shape
            img_lrd = cv2.resize(image, (lr_w, lr_h))
            im = np.expand_dims(preprocess(img_lrd), axis=0)

            gen_op = generator.predict(im)
            gen_hr = deprocess_uint8(gen_op[1]).reshape(hr_shape)
            gen_hr = cv2.resize(gen_hr, (width, height))

            results = model(gen_hr) 

            selected_objects = []
            for det in results[0].boxes.data:
                class_id = int(det[5])
                confidence = det[4]
                box = det[:4].cpu().numpy()
                class_name = target_classes[class_id]

                if class_name and confidence > 0.61:
                    selected_objects.append({
                        'class_name': class_name,
                        'confidence': confidence,
                        'bounding_box': [int(i) for i in box[:4]],
                    })
                    
            for obj in selected_objects:
                if obj['class_name'] not in results_list:
                    results_list.append(obj['class_name'])
                bbox = obj['bounding_box']
                cv2.rectangle(gen_hr, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
                text = f"{obj['class_name']} {obj['confidence']:.2f}"
                cv2.putText(gen_hr, text, (bbox[0] + 5, bbox[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

            frame_count += 1
            frames.append(gen_hr)

            progress = int((i / (numberOfFrames)) * 100)
            yield 'data: {}\n\n'.format(json.dumps({"progressValue": progress, "videoLocation": None}))
            if cv2.waitKey(10) == 27:
                break
            i += 1

    if len(frames):
        out_video_full_path = "./videos/Video(1).mp4"

        cv2_fourcc = cv2.VideoWriter_fourcc(*'avc1')

        size = frames[0].shape[1], frames[0].shape[0]

        video = cv2.VideoWriter(out_video_full_path, cv2_fourcc, fps, size)  # Output video name, fourcc, fps, size

        for i in range(len(frames)):
            video.write(frames[i])

        video.release()
        print("\n\n\n\n\n\n\n\n\n\n\n", out_video_full_path, "\n\n\n\n\n\n\n\n")
        yield 'data: {}\n\n'.format(json.dumps({"progressValue": 100, "videoLocation": "/videos/Video(1).mp4", "selectedObjects": results_list}))           


@app.route('/get_content', methods=['GET'])
def get_content():
    element_id = request.args.get('id')
    content = wiki(element_id).parashort2 
    return content

if __name__ == '__main__':
    model = YOLO("./models/best.pt")
    target_classes = ['Dolphin', 'Eel', 'JellyFish', 'PufferFish', 'Stingray', 'Sea-Urchin', 'Seahorse', 'Pinniped', 'Shark', 'Starfish']
    model_h5 = os.path.join("./models/deep_sesr_2x_1d.h5")
    model_json = os.path.join("./models/deep_sesr_2x_1d.json")
    hr_w, hr_h = 640, 480 
    lr_w, lr_h = 320, 240 
    hr_shape = (hr_h, hr_w, 3)

    assert (os.path.exists(model_h5) and os.path.exists(model_json))
    with open(model_json, "r") as json_file:
        loaded_model_json = json_file.read()
    generator = model_from_json(loaded_model_json)
    generator.load_weights(model_h5)

    app.run(debug=True)
