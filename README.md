git clone --recurse-submodules https://github.com/Kwan-Ho-Kim/Transformator.git

Transformator.py 파일 import해서 
transformator = Transformator("172.30.1.45",5000)
ret, response = transformator.get_3D(datas)

datas 포맷
[{'x1': x1,
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
    }}, ...]

response 포맷
[{'id': id,
'cls_name': cls_name,
'position': [x, y, z],
'color': [r, g, b, a]}, ...]