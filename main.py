#!/usr/bin/env python3

import queue
import numpy as np

from lib.ws_server import run_server
from multiprocessing import Process, Queue

from BlazeposeDepthai import BlazeposeDepthai

if __name__ == '__main__':
    tracker = BlazeposeDepthai(pd_model='models/pose_detection_sh6.blob',
                               lm_model='lite',
                               smoothing=True,
                               xyz=True,
                               crop=False,
                               internal_fps=25,
                               internal_frame_height=400,
                               force_detection=False,
                               stats=True,
                               trace=True)

    cfg_rcv_queue = Queue()
    body_send_queue = Queue(1)
    p = Process(target=run_server, args=(cfg_rcv_queue, body_send_queue, 8001))
    p.start()

    while True:
        # Run blazepose on next frame
        frame, body = tracker.next_frame()
        # Parse results
        if body is not None:
            landmarks_world = body.landmarks_world.astype(np.float32)
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

    p.kill()
    renderer.exit()
    tracker.exit()
