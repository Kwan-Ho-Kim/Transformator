# Transformator

실시간 2D 박스 정보를 3D 좌표로 변환해주는 WebSocket 클라이언트 라이브러리입니다.

---

## ✅ 설치

```bash
git clone --recurse-submodules https://github.com/Kwan-Ho-Kim/Transformator.git
```

---

## 📦 사용 예시

```python
from Transformator import Transformator

# 초기화 (서버 IP, 포트 설정)
transformator = Transformator("172.30.1.45", 5000)

# 예시 데이터
request = [
    {
        'x1': 100,
        'y1': 150,
        'x2': 200,
        'y2': 300,
        'id': 1,
        'conf': 0.95,
        'cls_name': 'car',
        'color': {
            'r': 0.8,
            'g': 0.5,
            'b': 0.3,
            'a': 1.0
        }
    },
    # ... 추가 객체들
]

# 3D 좌표 요청
ret, response = transformator.get_3D(request)
```
Demo/YOLO_demo.py 실행해서 동작 확인 가능 (Demo 폴더의 파라미터파일(.pt)과 동영상 파일(.avi)은 아래 경로에서 확인 가능)
 - 파라미터 파일 : \\Islab-Nas1\Projects\공업탑프로젝트\Data_Layer\Detect_Publisher\Weights
 - 동영상 파일 : \\Islab-Nas1\Projects\공업탑프로젝트\connect2server20

# get_3D 메소드의 입출력 형식
---

## 📥 입력 데이터 형식 (`request`)

`get_3D()` 함수에 전달되는 입력은 다음과 같은 형식의 리스트입니다:

```json
[
  {
    "x1": int,
    "y1": int,
    "x2": int,
    "y2": int,
    "id": int,
    "conf": float,
    "cls_name": "car" | "bus" | ...,
    "color": {
      "r": float,
      "g": float,
      "b": float,
      "a": 1.0
    }
  },
  ...
]
```

---

## 📤 출력 데이터 형식 (`response`)

서버에서 반환되는 응답은 다음과 같은 형식입니다:

```json
[
  {
    "id": int,
    "cls_name": "car" | "bus" | ...,
    "position": [x, y, z],
    "color": [r, g, b, a]
  },
  ...
]
```


