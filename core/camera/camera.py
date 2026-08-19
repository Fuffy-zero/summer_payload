import time
import cv2


class Camera:

    # ==========================================================
    # CONFIG
    # ==========================================================

    # เวลาสูงสุดที่รอให้ video stream พร้อม
    START_TIMEOUT = 10.0

    # เวลาระหว่างการตรวจ frame
    START_CHECK_INTERVAL = 0.1

    # จำนวน frame ที่ต้องได้ติดต่อกัน
    # ก่อนถือว่ากล้องพร้อมจริง
    START_VALID_FRAMES = 3

    # ==========================================================
    # INIT
    # ==========================================================

    def __init__(self):

        self.bridge = None

        self.connected = False
        self.running = False

    # ==========================================================
    # CONNECT
    # ==========================================================

    def connect(
        self,
        bridge
    ):

        self.bridge = bridge

        if self.bridge is None:

            print(
                "Camera bridge unavailable"
            )

            return False

        if not self.bridge.connected:

            print(
                "Hula is not connected"
            )

            return False

        self.connected = True

        print(
            "Camera connected"
        )

        return True

    # ==========================================================
    # CHECK FRAME
    # ==========================================================

    def _is_valid_frame(
        self,
        frame
    ):

        if frame is None:

            return False

        try:

            if not hasattr(
                frame,
                "shape"
            ):

                return False

            if len(
                frame.shape
            ) < 2:

                return False

            height = int(
                frame.shape[0]
            )

            width = int(
                frame.shape[1]
            )

            if height <= 0:
                return False

            if width <= 0:
                return False

            # --------------------------------------------------
            # ต้องมีข้อมูลจริง
            # --------------------------------------------------

            if frame.size <= 0:

                return False

            return True

        except Exception:

            return False

    # ==========================================================
    # START
    # ==========================================================

    def start(self):

        if not self.connected:

            print(
                "Camera is not connected"
            )

            return False

        print(
            "Starting camera..."
        )

        # ------------------------------------------------------
        # START RTP
        # ------------------------------------------------------

        result = (
            self.bridge.start_camera()
        )

        if not result:

            print(
                "Camera start failed"
            )

            return False

        # ------------------------------------------------------
        # RTP อาจเริ่มแล้ว แต่ frame ยังไม่มา
        # ------------------------------------------------------

        print(
            "Waiting for video stream..."
        )

        timeout = (
            time.monotonic()
            +
            self.START_TIMEOUT
        )

        valid_count = 0

        while (
            time.monotonic()
            <
            timeout
        ):

            frame = (
                self.bridge.get_frame()
            )

            # --------------------------------------------------
            # FRAME VALID
            # --------------------------------------------------

            if self._is_valid_frame(
                frame
            ):

                valid_count += 1

                print(
                    "Valid camera frame:",
                    valid_count,
                    "/",
                    self.START_VALID_FRAMES
                )

                if (
                    valid_count
                    >=
                    self.START_VALID_FRAMES
                ):

                    self.running = True

                    print(
                        "Camera ready"
                    )

                    return True

            # --------------------------------------------------
            # FRAME INVALID / ยังไม่มา
            # --------------------------------------------------

            else:

                valid_count = 0

            time.sleep(
                self.START_CHECK_INTERVAL
            )

        # ======================================================
        # STARTUP FAILED
        # ======================================================

        print(
            "Camera stream timeout."
        )

        print(
            "No valid video frame received."
        )

        # ------------------------------------------------------
        # ป้องกันไม่ให้ระบบคิดว่ากล้องยังใช้งานอยู่
        # ------------------------------------------------------

        self.running = False

        try:

            self.bridge.stop_camera()

        except Exception as e:

            print(
                "Camera cleanup error:",
                e
            )

        return False

    # ==========================================================
    # GET FRAME
    # ==========================================================

    def get_frame(self):

        if not self.running:

            return None

        frame = (
            self.bridge.get_frame()
        )

        if not self._is_valid_frame(
            frame
        ):

            return None

        try:

            frame = cv2.cvtColor(
                frame,
                cv2.COLOR_RGB2BGR
            )

        except cv2.error:

            return None

        return frame

    # ==========================================================
    # STOP
    # ==========================================================

    def stop(self):

        print()
        print(
            "Stopping camera..."
        )

        self.running = False

        if self.bridge is not None:

            try:

                self.bridge.stop_camera()

            except Exception as e:

                print(
                    "Camera stop error:",
                    e
                )

        self.connected = False

        print(
            "Camera stopped"
        )

    # ==========================================================
    # STATUS
    # ==========================================================

    def is_connected(self):

        return self.connected

    def is_running(self):

        return self.running

    # ==========================================================
    # API
    # ==========================================================

    def get_api(self):

        if self.bridge is None:

            return None

        return self.bridge.api