import numpy as np

from websockets.sync import server
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK


def run_server(cfg_queue, data_queue, port=8000, host="localhost"):
    def handler(websocket):
        while True:
            try:
                data = None
                while not data_queue.empty():
                    data = data_queue.get()
                if data is not None:
                    if isinstance(data, list):
                        payload_bytes = np.float32([item for row in data for item in row]).tobytes()
                    else:
                        payload_bytes = data.tobytes()
                    websocket.send(payload_bytes)
                msg = websocket.recv(0)
                if msg is not None:
                    cfg_queue.put(msg)
            except TimeoutError:
                pass
            except ConnectionClosedOK:
                pass
            except ConnectionClosedError:
                print("WS connection error")

    with server.serve(handler, host, port, origins=["https://localhost:8080"]) as server_instance:
        try:
            server_instance.serve_forever()
        except KeyboardInterrupt:
            server_instance.shutdown()
