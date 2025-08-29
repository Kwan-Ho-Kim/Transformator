import sys
import ultralytics
import cv2
import numpy as np
import os

root_path = os.path.dirname(os.path.dirname(__file__))  # Transformator
sys.path.append(root_path)
from Transformator import Transformator
from Demo.sort.sort import Sort

transformator = Transformator("172.30.1.45")

video_path = os.path.join(root_path, "Demo/20240123-053055-055400-0.avi")
weight_path = os.path.join(root_path, "Demo/yolov9_uav_gongeoptap50.pt")

cap = cv2.VideoCapture(video_path)
model = ultralytics.YOLO(weight_path)
tracker = Sort(max_age=20, iou_threshold=0.1)

def make_tracking(frame, tracking_boxes):
    track_data = []
    print("\nbefore visualization of tracking")
    for *xyxy, id in tracking_boxes:
        
        frame = cv2.rectangle(frame, (int(xyxy[0]),int(xyxy[1])), (int(xyxy[2]),int(xyxy[3])), (0,0,255),2)
        
        x1 = int(xyxy[0])
        y1 = int(xyxy[1])
        x2 = int(xyxy[2])
        y2 = int(xyxy[3])
        id = int(id)
        width = x2-x1
        height = y2 - y1
        conf = 0.
        # if width >= 100 or height >= 200 or width*height >= 4500:
        # cls_name = "car"
        if width*height >= 5000:
            cls_name = "bus"
        else:
            cls_name = "car"
            
        vehicle_color = frame[int((y1+y2)/2),int((x1+x2)/2)]/255
        track_data.append({
            'x1': x1,
            'y1': y1,
            'x2': x2,
            'y2': y2,
            'id': id,
            'conf': float(conf),
            'cls_name': cls_name,
            'color': {
                'r': float(vehicle_color[2]),  
                'g': float(vehicle_color[1]),
                'b': float(vehicle_color[0]),
                'a': 1.0
                }})
    # print(track_data)
    # print(frame.shape)
    # frame = cv2.resize(frame,(int(frame.shape[1]/2),int(frame.shape[0]/2)))
    cv2.imshow("frame", frame)
    return track_data

is_pause = False
while cap.isOpened():
    if not is_pause:
        ret, frame = cap.read()
        if not ret: break
        frame = cv2.resize(frame, (960,540))

        results = model(frame, conf=0.15)
        bboxes = results[0].boxes.data.tolist()
        track_boxes = []
        if len(bboxes)>=1:
            track_boxes = tracker.update(np.array(bboxes))
        
        datas = make_tracking(frame, track_boxes)
        
        # 여기서 3D 변환 요청 (동기 방식)
        ret, response = transformator.get_3D(datas)
        
        if not ret: break
    
    q = cv2.waitKey(1)
    if q == 27:     # esc
        break
    elif q == 13:   # carriage return
        if is_pause: is_pause = False
        else: is_pause = True
        
    # 이후 필요한 처리 수행
    # print(response)
    
transformator.close()
cap.release()
cv2.destroyAllWindows()