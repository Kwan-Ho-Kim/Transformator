import socket
import sys

HOST = "0.0.0.0"  # 모든 IP에서 연결 허용
PORT = 5000       # 포트 설정

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server.close()
server.bind((HOST, PORT))
server.listen(5)  # 최대 5개의 클라이언트 대기

print(f"서버 시작됨, {PORT} 포트에서 대기 중...")

while True:
    client, addr = server.accept()  # 클라이언트 연결 대기
    print(f"클라이언트 연결됨: {addr}")

    try:
        while True:
            data = client.recv(1024).decode()  # 데이터 수신
            if not data:
                break
            print(f"받은 메시지: {data}")

            response = "서버 응답: " + data.upper()  # 대문자로 변환해서 응답
            client.sendall(response.encode())

    except Exception as e:
        print(f"오류 발생: {e}")

    finally:
        client.close()
        server.close()
        sys.exit()
        print("클라이언트 연결 종료")
