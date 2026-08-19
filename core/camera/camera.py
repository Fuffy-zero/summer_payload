import cv2


class Camera:

    def __init__(self):

        self.bridge = None

        self.connected = False
        self.running = False

    # ==========================================
    # CONNECT
    # ==========================================

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

    # ==========================================
    # START
    # ==========================================

    def start(self):

        if not self.connected:

            print(
                "Camera is not connected"
            )

            return False

        print(
            "Starting camera..."
        )

        result = self.bridge.start_camera()

        if not result:

            print(
                "Camera start failed"
            )

            return False

        self.running = True

        print(
            "Camera ready"
        )

        return True

    # ==========================================
    # GET FRAME
    # ==========================================

    def get_frame(self):

        if not self.running:

            return None

        frame = self.bridge.get_frame()

        if frame is None:

            return None

        try:

            frame = cv2.cvtColor(
                frame,
                cv2.COLOR_RGB2BGR
            )

        except cv2.error:

            return None

        return frame

    # ==========================================
    # STOP
    # ==========================================

    def stop(self):

        print()
        print(
            "Stopping camera..."
        )

        self.running = False

        if self.bridge is not None:

            self.bridge.stop_camera()

        print(
            "Camera stopped"
        )

    # ==========================================
    # STATUS
    # ==========================================

    def is_connected(self):

        return self.connected

    def is_running(self):

        return self.running

    # ==========================================
    # API
    # ==========================================

    def get_api(self):

        if self.bridge is None:

            return None

        return self.bridge.api