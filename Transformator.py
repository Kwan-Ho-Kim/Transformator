import asyncio
import websockets
import json
import time
import atexit
import threading
import concurrent.futures

class Transformator:
    def __init__(self, ip : str, port : int = 5000, env : str = "gongeoptap"):
        self.uri = f"ws://{ip}:{str(port)}/{env}"
        # self.uri = "ws://172.30.1.45:5000/gongeoptap"
        print(self.uri)
        self.loop = asyncio.new_event_loop()
        self.websocket = None
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        
        self._connect_future = asyncio.run_coroutine_threadsafe(self._connect(), self.loop)
        self._connect_future.result()  # Connect가 끝날 때까지 대기

        self.alive = True
        atexit.register(self.close)  # 자동 종료 등록

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def get_3D(self, bboxes):
        if self.alive:
            """
            사용자는 동기 방식으로 호출하지만,
            내부적으로는 비동기로 웹소켓 통신을 수행.
            """
            future = asyncio.run_coroutine_threadsafe(self._get_3D_async(bboxes), self.loop)
            try:
                return True, future.result(timeout=10)  # 결과 받을 때까지 블로킹
            except concurrent.futures.TimeoutError:
                print("[Transformator] Timeout reached, returning empty result.")
                return False, []
        else:
            return False, []

    async def _connect(self):
        try:
            self.websocket = await websockets.connect(self.uri)
            print("[Transformator] WebSocket connected.")
        except Exception as e:
            print("[Transformator] Failed to connect:", e)
            self.websocket = None

    async def _get_3D_async(self, bboxes):
        try:
            data = {"frame_data": bboxes}
            json_data = json.dumps(data)

            send_t = time.time()
            await self.websocket.send(json_data)
            response = await self.websocket.recv()
            duration = time.time() - send_t
            print("duration for data exchange: ", duration)

            return json.loads(response)
        except Exception as e:
            print("WebSocket error:", e)
            self.close()
            return []

    def close(self):
        if self.websocket:
            try:
                asyncio.run_coroutine_threadsafe(self.websocket.close(), self.loop).result()
                print("[Transformator] WebSocket closed.")
            except Exception as e:
                print("[Transformator] Error while closing websocket:", e)
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.alive = False
