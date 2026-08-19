import threading
import time
import pyhula


class HulaBridge:

    def __init__(self):

        self.api = None

        self.connected = False
        self.running = False

        # ==========================================================
        # HULA WORKER
        # ==========================================================

        self.worker = None

        # ==========================================================
        # COMMAND
        # ==========================================================

        self.command_lock = threading.Lock()

        self.pending_command = None

        self.busy = False

        # ==========================================================
        # RESULT
        # ==========================================================

        self.last_result = None

        # ==========================================================
        # FRAME
        # ==========================================================

        self.frame = None

        self.frame_lock = threading.Lock()

        # ==========================================================
        # CONNECT EVENT
        # ==========================================================

        self.connect_event = threading.Event()
        self.connect_result = False

    # ==========================================================
    # INTEGER PARAMETER
    # ==========================================================

    def _to_int(
        self,
        value,
        name
    ):

        try:

            result = int(
                round(
                    float(value)
                )
            )

            return result

        except (
            TypeError,
            ValueError
        ):

            raise ValueError(
                f"Invalid {name}: {value}"
            )

    # ==========================================================
    # CONNECT
    # ==========================================================

    def connect(self):

        print(
            "Starting Hula worker..."
        )

        self.running = True

        self.connect_event.clear()
        self.connect_result = False

        self.worker = threading.Thread(
            target=self._worker_loop,
            name="HulaWorker",
            daemon=True
        )

        self.worker.start()

        print(
            "Connecting to Hula..."
        )

        self.connect_event.wait()

        if not self.connect_result:

            print(
                "Hula connection failed"
            )

            self.running = False

            return False

        self.connected = True

        print(
            "Hula connected!"
        )

        return True

    # ==========================================================
    # WORKER LOOP
    # ==========================================================

    def _worker_loop(self):

        print(
            "Hula worker started"
        )

        try:

            # ==================================================
            # CREATE API
            # ==================================================

            try:

                self.api = pyhula.UserApi()

                result = self.api.connect()

                self.connect_result = bool(
                    result
                )

            except Exception as e:

                print()
                print(
                    "HULA CONNECT ERROR:"
                )

                print(
                    repr(e)
                )

                self.connect_result = False

            self.connect_event.set()

            if not self.connect_result:

                self.running = False

                return

            # ==================================================
            # MAIN LOOP
            # ==================================================

            while self.running:

                # ==================================================
                # GET COMMAND
                # ==================================================

                command = None

                with self.command_lock:

                    if self.pending_command is not None:

                        command = (
                            self.pending_command
                        )

                        self.pending_command = None

                # ==================================================
                # EXECUTE COMMAND
                # ==================================================

                if command is not None:

                    action = command[
                        "action"
                    ]

                    args = command[
                        "args"
                    ]

                    self.last_result = None

                    try:

                        result = (
                            self._execute_command(
                                action,
                                args
                            )
                        )

                        self.last_result = (
                            bool(result)
                        )

                    except Exception as e:

                        print()
                        print(
                            "========================================"
                        )

                        print(
                            "HULA COMMAND ERROR"
                        )

                        print(
                            "========================================"
                        )

                        print(
                            "Action:",
                            action
                        )

                        print(
                            "Error:",
                            repr(e)
                        )

                        self.last_result = False

                    finally:

                        self.busy = False

                    continue

                # ==================================================
                # CAMERA FRAME
                # ==================================================

                if self.connected:

                    try:

                        frame = (
                            self.api.get_image_array()
                        )

                        if frame is not None:

                            with self.frame_lock:

                                self.frame = frame

                    except Exception as e:

                        if self.running:

                            print(
                                "Hula camera error:",
                                repr(e)
                            )

                time.sleep(
                    0.001
                )

        except Exception as e:

            print()
            print(
                "========================================"
            )

            print(
                "HULA WORKER ERROR"
            )

            print(
                "========================================"
            )

            print(
                repr(e)
            )

            self.connect_result = False
            self.connected = False
            self.busy = False

            with self.command_lock:

                self.pending_command = None

            self.connect_event.set()

        finally:

            self.busy = False

            print(
                "Hula worker stopped"
            )

    # ==========================================================
    # EXECUTE COMMAND
    # ==========================================================

    def _execute_command(
        self,
        action,
        args
    ):

        # ==================================================
        # TAKE OFF
        # ==================================================

        if action == "take_off":

            print(
                "Sending TAKEOFF..."
            )

            try:

                result = (
                    self.api.single_fly_takeoff()
                )

            except Exception as e:

                print(
                    "TAKEOFF exception:",
                    repr(e)
                )

                return False

            print(
                "TAKEOFF result:",
                result
            )

            return bool(
                result
            )

        # ==================================================
        # LANDING
        # ==================================================

        if action == "landing":

            print(
                "Sending LANDING..."
            )

            try:

                result = (
                    self.api.single_fly_touchdown()
                )

            except Exception as e:

                print(
                    "LANDING exception:",
                    repr(e)
                )

                return False

            print(
                "LANDING result:",
                result
            )

            return bool(
                result
            )

        # ==================================================
        # FORWARD
        # ==================================================

        if action == "forward":

            distance = self._to_int(
                args["distance"],
                "forward distance"
            )

            speed = self._to_int(
                args["speed"],
                "forward speed"
            )

            print(
                f"FORWARD "
                f"{distance} cm "
                f"@ {speed} cm/s"
            )

            try:

                result = (
                    self.api.single_fly_forward(
                        distance,
                        speed
                    )
                )

            except Exception as e:

                print(
                    "FORWARD exception:",
                    repr(e)
                )

                return False

            print(
                "FORWARD result:",
                result
            )

            return (
                True
                if result is None
                else bool(result)
            )

        # ==================================================
        # BACKWARD
        # ==================================================

        if action == "backward":

            distance = self._to_int(
                args["distance"],
                "backward distance"
            )

            speed = self._to_int(
                args["speed"],
                "backward speed"
            )

            print(
                f"BACKWARD "
                f"{distance} cm "
                f"@ {speed} cm/s"
            )

            try:

                result = (
                    self.api.single_fly_back(
                        distance,
                        speed
                    )
                )

            except Exception as e:

                print(
                    "BACKWARD exception:",
                    repr(e)
                )

                return False

            print(
                "BACKWARD result:",
                result
            )

            return (
                True
                if result is None
                else bool(result)
            )

        # ==================================================
        # LEFT
        # ==================================================

        if action == "left":

            distance = self._to_int(
                args["distance"],
                "left distance"
            )

            speed = self._to_int(
                args["speed"],
                "left speed"
            )

            print(
                f"LEFT "
                f"{distance} cm "
                f"@ {speed} cm/s"
            )

            try:

                result = (
                    self.api.single_fly_left(
                        distance,
                        speed
                    )
                )

            except Exception as e:

                print(
                    "LEFT exception:",
                    repr(e)
                )

                return False

            print(
                "LEFT result:",
                result
            )

            return (
                True
                if result is None
                else bool(result)
            )

        # ==================================================
        # RIGHT
        # ==================================================

        if action == "right":

            distance = self._to_int(
                args["distance"],
                "right distance"
            )

            speed = self._to_int(
                args["speed"],
                "right speed"
            )

            print(
                f"RIGHT "
                f"{distance} cm "
                f"@ {speed} cm/s"
            )

            try:

                result = (
                    self.api.single_fly_right(
                        distance,
                        speed
                    )
                )

            except Exception as e:

                print(
                    "RIGHT exception:",
                    repr(e)
                )

                return False

            print(
                "RIGHT result:",
                result
            )

            return (
                True
                if result is None
                else bool(result)
            )

        # ==================================================
        # ROTATE LEFT
        # ==================================================

        if action == "rotate_left":

            angle = self._to_int(
                args["angle"],
                "rotate left angle"
            )

            print(
                f"ROTATE LEFT "
                f"{angle} degrees"
            )

            try:

                result = (
                    self.api.single_fly_turnleft(
                        angle
                    )
                )

            except Exception as e:

                print(
                    "ROTATE LEFT exception:",
                    repr(e)
                )

                return False

            print(
                "ROTATE LEFT result:",
                result
            )

            return (
                True
                if result is None
                else bool(result)
            )

        # ==================================================
        # ROTATE RIGHT
        # ==================================================

        if action == "rotate_right":

            angle = self._to_int(
                args["angle"],
                "rotate right angle"
            )

            print(
                f"ROTATE RIGHT "
                f"{angle} degrees"
            )

            try:

                result = (
                    self.api.single_fly_turnright(
                        angle
                    )
                )

            except Exception as e:

                print(
                    "ROTATE RIGHT exception:",
                    repr(e)
                )

                return False

            print(
                "ROTATE RIGHT result:",
                result
            )

            return (
                True
                if result is None
                else bool(result)
            )

        # ==================================================
        # UP
        # ==================================================

        if action == "up":

            distance = self._to_int(
                args["distance"],
                "up distance"
            )

            speed = self._to_int(
                args["speed"],
                "up speed"
            )

            print(
                f"UP "
                f"{distance} cm "
                f"@ {speed} cm/s"
            )

            try:

                result = (
                    self.api.single_fly_up(
                        distance,
                        speed
                    )
                )

            except Exception as e:

                print(
                    "UP exception:",
                    repr(e)
                )

                return False

            print(
                "UP result:",
                result
            )

            return (
                True
                if result is None
                else bool(result)
            )

        # ==================================================
        # DOWN
        # ==================================================

        if action == "down":

            distance = self._to_int(
                args["distance"],
                "down distance"
            )

            speed = self._to_int(
                args["speed"],
                "down speed"
            )

            print(
                f"DOWN "
                f"{distance} cm "
                f"@ {speed} cm/s"
            )

            try:

                result = (
                    self.api.single_fly_down(
                        distance,
                        speed
                    )
                )

            except Exception as e:

                print(
                    "DOWN exception:",
                    repr(e)
                )

                return False

            print(
                "DOWN result:",
                result
            )

            return (
                True
                if result is None
                else bool(result)
            )

        # ==================================================
        # START RTP
        # ==================================================

        if action == "start_camera":

            print(
                "Starting RTP..."
            )

            try:

                self.api.Plane_cmd_swith_rtp(
                    0
                )

                time.sleep(
                    2
                )

                try:

                    self.api.single_fly_flip_rtp()

                except Exception as e:

                    print(
                        "Flip RTP error:",
                        repr(e)
                    )

                time.sleep(
                    2
                )

                return True

            except Exception as e:

                print(
                    "RTP start error:",
                    repr(e)
                )

                return False

        # ==================================================
        # STOP RTP
        # ==================================================

        if action == "stop_camera":

            print(
                "Disabling RTP..."
            )

            try:

                self.api.Plane_cmd_swith_rtp(
                    1
                )

                print(
                    "RTP disable command returned"
                )

                return True

            except Exception as e:

                print(
                    "RTP stop error:",
                    repr(e)
                )

                return False

        # ==================================================
        # UNKNOWN
        # ==================================================

        print(
            "Unknown Hula command:",
            action
        )

        return False

    # ==========================================================
    # SUBMIT COMMAND
    # ==========================================================

    def submit(
        self,
        action,
        **args
    ):

        if not self.connected:

            print(
                f"Cannot submit '{action}': "
                "Hula is not connected."
            )

            return False

        if not self.running:

            print(
                f"Cannot submit '{action}': "
                "Hula worker is not running."
            )

            return False

        with self.command_lock:

            self.pending_command = {

                "action": action,

                "args": args

            }

            self.busy = True

        self.last_result = None

        return True

    # ==========================================================
    # BUSY
    # ==========================================================

    def is_busy(self):

        return self.busy

    # ==========================================================
    # RESULT
    # ==========================================================

    def get_last_result(self):

        return self.last_result

    # ==========================================================
    # START CAMERA
    # ==========================================================

    def start_camera(self):

        if not self.connected:

            print(
                "Cannot start camera: "
                "Hula is not connected."
            )

            return False

        accepted = self.submit(
            "start_camera"
        )

        if not accepted:

            return False

        timeout = (
            time.monotonic()
            + 5.0
        )

        while self.running:

            if not self.is_busy():

                return (
                    self.last_result
                    is True
                )

            if time.monotonic() >= timeout:

                print(
                    "Camera start timeout"
                )

                return False

            time.sleep(
                0.01
            )

        return False

    # ==========================================================
    # GET FRAME
    # ==========================================================

    def get_frame(self):

        with self.frame_lock:

            if self.frame is None:

                return None

            return self.frame.copy()

    # ==========================================================
    # STOP CAMERA
    # ==========================================================

    def stop_camera(self):

        if not self.connected:

            return

        accepted = self.submit(
            "stop_camera"
        )

        if not accepted:

            return

        timeout = (
            time.monotonic()
            + 2.0
        )

        while self.is_busy():

            if time.monotonic() >= timeout:

                print(
                    "Camera stop timeout"
                )

                break

            time.sleep(
                0.01
            )

    # ==========================================================
    # SHUTDOWN
    # ==========================================================

    def stop(self):

        print()
        print(
            "Stopping Hula worker..."
        )

        self.running = False

        with self.command_lock:

            self.pending_command = None
            self.busy = False

        if self.worker is not None:

            self.worker.join(
                timeout=1.0
            )

        self.worker = None

        self.connected = False
        self.api = None

        print(
            "Hula worker stopped"
        )