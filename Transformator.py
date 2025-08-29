import asyncio
import websockets
import json
import time
import atexit
import threading
import concurrent.futures

import asyncio
import websockets
import json
import time
import atexit
import threading
import concurrent.futures

class Transformator:
    def __init__(self, ip: str, port: int = 5000, env: str = "gongeoptap",
                 rpc_timeout: float = 10.0, ws_close_timeout: float = 2.0):
        self.uri = f"ws://{ip}:{port}/{env}"
        print(self.uri)

        self.loop = asyncio.new_event_loop()
        self.websocket = None
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

        self.rpc_timeout = rpc_timeout
        self.ws_close_timeout = ws_close_timeout
        self._io_lock = asyncio.run_coroutine_threadsafe(self._make_lock(), self.loop).result()

        self._connect_future = asyncio.run_coroutine_threadsafe(self._connect(), self.loop)
        self._connect_future.result()

        self.alive = True
        atexit.register(self.close)

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    async def _make_lock(self):
        self._lock = asyncio.Lock()
        return self._lock

    def get_3D(self, bboxes):
        if not self.alive:
            return False, []

        # 한 번에 하나의 요청만 보장 (웹소켓은 동시 send/recv 취약)
        async def wrapped():
            async with self._lock:
                return await self._get_3D_async(bboxes)

        fut = asyncio.run_coroutine_threadsafe(wrapped(), self.loop)
        try:
            res = fut.result(timeout=self.rpc_timeout + 1.0)  # 약간의 여유 버퍼
            return True, res
        except concurrent.futures.TimeoutError:
            # 요청 코루틴을 반드시 취소
            fut.cancel()
            try:
                fut.result(timeout=0.5)
            except Exception:
                pass
            print("[Transformator] Timeout reached, request cancelled.")
            return False, []

    async def _connect(self):
        try:
            # close_timeout을 짧게 설정
            self.websocket = await websockets.connect(self.uri, close_timeout=self.ws_close_timeout)
            print("[Transformator] WebSocket connected.")
        except Exception as e:
            print("[Transformator] Failed to connect:", e)
            self.websocket = None

    async def _get_3D_async(self, bboxes):
        if not self.websocket:
            return []

        try:
            data = {"frame_data": bboxes}
            json_data = json.dumps(data)

            send_t = time.time()
            await self.websocket.send(json_data)

            # recv에 비동기 타임아웃 적용 → 코루틴이 스스로 끝남
            response = await asyncio.wait_for(self.websocket.recv(), timeout=self.rpc_timeout)
            duration = time.time() - send_t
            print("duration for data exchange: ", duration)

            return json.loads(response)

        except (asyncio.TimeoutError, asyncio.CancelledError):
            # 서버 응답 지연 → 다음 요청을 위해 웹소켓을 강제 닫고 재연결하도록 설계할 수도 있음
            print("[Transformator] Async timeout or cancelled; consider reconnect.")
            return []
        except Exception as e:
            print("WebSocket error:", e)
            return []

    def close(self):
        if not self.alive:
            return
        self.alive = False

        # 루프에서 모든 작업 취소 및 소켓 닫기 예약 (비차단)
        async def _shutdown():
            try:
                if self.websocket:
                    try:
                        await asyncio.wait_for(self.websocket.close(), timeout=self.ws_close_timeout)
                        print("[Transformator] WebSocket closed.")
                    except asyncio.TimeoutError:
                        print("[Transformator] WebSocket close timeout; aborting.")
            finally:
                # 루프 내 pending task들 취소
                tasks = [t for t in asyncio.all_tasks(self.loop) if t is not asyncio.current_task(loop=self.loop)]
                for t in tasks:
                    t.cancel()
                if tasks:
                    try:
                        await asyncio.gather(*tasks, return_exceptions=True)
                    except Exception:
                        pass

        # 종료 절차를 스케줄하고 잠깐 기다림
        try:
            fut = asyncio.run_coroutine_threadsafe(_shutdown(), self.loop)
            try:
                fut.result(timeout=self.ws_close_timeout + 1.0)
            except Exception:
                pass
        finally:
            # 마지막으로 루프 중지
            self.loop.call_soon_threadsafe(self.loop.stop)
            # 백그라운드 스레드 조인(타임아웃 포함)
            self.thread.join(timeout=1.0)


# class Transformator:
#     def __init__(self, ip : str, port : int = 5000, env : str = "gongeoptap"):
#         self.uri = f"ws://{ip}:{str(port)}/{env}"
#         # self.uri = "ws://172.30.1.45:5000/gongeoptap"
#         print(self.uri)
#         self.loop = asyncio.new_event_loop()
#         self.websocket = None
#         self.thread = threading.Thread(target=self._run_loop, daemon=True)
#         self.thread.start()
        
#         self._connect_future = asyncio.run_coroutine_threadsafe(self._connect(), self.loop)
#         self._connect_future.result()  # Connect가 끝날 때까지 대기

#         self.alive = True
#         atexit.register(self.close)  # 자동 종료 등록

#     def _run_loop(self):
#         asyncio.set_event_loop(self.loop)
#         self.loop.run_forever()

#     def get_3D(self, bboxes):
#         if self.alive:
#             """
#             사용자는 동기 방식으로 호출하지만,
#             내부적으로는 비동기로 웹소켓 통신을 수행.
#             """
#             future = asyncio.run_coroutine_threadsafe(self._get_3D_async(bboxes), self.loop)
#             try:
#                 return True, future.result(timeout=10)  # 결과 받을 때까지 블로킹
#             except concurrent.futures.TimeoutError:
#                 print("[Transformator] Timeout reached, returning empty result.")
#                 return False, []
#         else:
#             return False, []

#     async def _connect(self):
#         try:
#             self.websocket = await websockets.connect(self.uri)
#             print("[Transformator] WebSocket connected.")
#         except Exception as e:
#             print("[Transformator] Failed to connect:", e)
#             self.websocket = None

#     async def _get_3D_async(self, bboxes):
#         try:
#             data = {"frame_data": bboxes}
#             json_data = json.dumps(data)

#             send_t = time.time()
#             await self.websocket.send(json_data)
#             response = await self.websocket.recv()
#             duration = time.time() - send_t
#             print("duration for data exchange: ", duration)

#             return json.loads(response)
        
#         except Exception as e:
#             print("WebSocket error:", e)
#             self.close()
#             return []

#     def close(self):
#         if self.websocket:
#             try:
#                 asyncio.run_coroutine_threadsafe(self.websocket.close(), self.loop).result()
#                 print("[Transformator] WebSocket closed.")
#             except Exception as e:
#                 print("[Transformator] Error while closing websocket:", e)
#         self.loop.call_soon_threadsafe(self.loop.stop)
#         self.alive = False
