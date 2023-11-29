#!/usr/bin/env python3

import queue
import time

import numpy as np

from lib.ws_server import run_server
from lib.fps_handler import FPSHandler
from multiprocessing import Process, Queue

from BlazeposeDepthaiDefault import BlazeposeDepthaiDefault

if __name__ == '__main__':
    tracker = BlazeposeDepthaiDefault(
                               smoothing=True,
                               internal_fps=25,
                               internal_frame_height=400,
                               force_detection=False,
                               trace=True)

    cfg_rcv_queue = Queue()
    body_send_queue = Queue(1)
    p = Process(target=run_server, args=(cfg_rcv_queue, body_send_queue, 8001))
    p.start()

    fps = FPSHandler()

    # Delete face and fingers
    points_delete = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 17, 18, 19, 20, 21, 22]

    while True:
        fps.next_iter()

        # Run blazepose on next frame
        frame, body = tracker.next_frame()

        # Parse results
        if body is not None:
            landmarks_world = np.delete(body.landmarks_world, points_delete, 0).astype(np.float32)
            xyz = body.xyz.astype(np.float32)
            xyz_ref = body.xyz_ref
            body_payload = np.insert(landmarks_world, 0, xyz, 0).flatten().tobytes()
            xyz_ref_bytes = bytes(bytearray(xyz_ref, 'ascii'))
            body_payload = b"".join([body_payload, xyz_ref_bytes])

            # Send results via Websockets
            try:
                body_send_queue.put(bytes(body_payload), False)
            except queue.Full:
                pass
        else:
            time.sleep(0.04)

        if fps.frame_cnt % 25 == 0:
            print(str(fps.fps()))

    tracker.exit()
    p.kill()
