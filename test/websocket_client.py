import asyncio
import websockets
import time
import json
import cv2
import ultralytics
from sort.sort import Sort
import numpy as np

# class TransformationService:
#     def __init__(self, url="ws://172.30.1.45:5000/gongeoptap"):


async def connect():
    uri = "ws://172.30.1.45:5000/gongeoptap"
    
    cap = cv2.VideoCapture("TrafficAgent/Dataset/output_20241031_143958.avi")
    model = ultralytics.YOLO("TrafficAgent/20240910_v1_500images.pt")
    tracker = Sort(max_age=20, iou_threshold=0.05)
    
    async with websockets.connect(uri) as websocket:
        while cap.isOpened():
            ret, frame = cap.read()
            results = model(frame, conf=0.15)
            bboxes = results[0].boxes.data.tolist()
            track_boxes = []
            if len(bboxes)>=1:
                track_boxes = tracker.update(np.array(bboxes))
            
            datas = publish_tracking(frame, track_boxes)
            frame_data = {"frame_data":datas}
            json_data = json.dumps(frame_data)
        
            send_t = time.time()
            await websocket.send(json_data)
            response = await websocket.recv()
            duration = time.time() - send_t
            print("duration for data exchange: ", duration)
            # print(f"Received: {response}")
            # time.sleep(1)

def publish_tracking(frame, tracking_boxes):
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
    
    frame = cv2.resize(frame,(720,500))
    cv2.imshow("frame", frame)
    cv2.waitKey(1)
    return track_data

asyncio.run(connect())