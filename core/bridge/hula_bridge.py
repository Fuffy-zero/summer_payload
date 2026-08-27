import threading
import time
import pyhula


class HulaBridge:

    # ==========================================================
    # CONFIG
    # ==========================================================

    FRAME_INTERVAL = 0.005

    BATTERY_POLL_INTERVAL = 5.0

    # ==========================================================
    # INIT
    # ==========================================================

    def __init__(self):

        # ======================================================
        # PYHULA
        # ======================================================

        self.api = None

        self.connected = False
        self.running = False

        self.worker = None

        # ======================================================
        # COMMAND
        # ======================================================

        self.command_lock = threading.Lock()

        self.pending_command = None

        self.busy = False

        # ======================================================
        # RESULT
        # ======================================================

        self.last_result = None

        # ======================================================
        # FRAME
        # ======================================================

        self.frame = None

        self.frame_lock = threading.Lock()

        # ======================================================
        # CAMERA / RTP
        # ======================================================

        self.camera_running = False

        self.camera_lock = threading.Lock()

        # ======================================================
        # BATTERY
        # ======================================================

        self.battery_level = "--"

        self.battery_lock = threading.Lock()

        self._battery_last_poll = 0.0

    # ==========================================================
    # INTEGER
    # ==========================================================

    def _to_int(self, value, name):

        try:

            return int(
                round(
                    float(value)
                )
            )

        except (TypeError, ValueError):

            raise ValueError(
                f"Invalid {name}: {value}"
            )

    # ==========================================================
    # CONNECT
    #
    # IMPORTANT:
    #
    # pyhula 1.1.8 ต้องสร้าง UserApi และ connect()
    # ใน thread เดียวกับที่เรียกใช้งานหลัก
    #
    # ไม่สร้าง UserApi ใน worker thread
    # ==========================================================

    def connect(self):

        if self.connected:

            print(
                "Hula is already connected."
            )

            return True

        if (
            self.worker is not None
            and
            self.worker.is_alive()
        ):

            print(
                "Hula worker is already running."
            )

            return False

        print()
        print("========================================")
        print("HULA CONNECTION")
        print("========================================")

        # ======================================================
        # RESET STATE
        # ======================================================

        self.connected = False
        self.running = False

        self.api = None

        self.camera_running = False

        with self.command_lock:

            self.pending_command = None
            self.busy = False

        with self.frame_lock:

            self.frame = None

        # ======================================================
        # CREATE PYHULA API
        #
        # เหมือนโค้ดตัวอย่างโดยตรง
        # ======================================================

        try:

            print(
                "Creating pyhula.UserApi..."
            )

            self.api = pyhula.UserApi()

        except Exception as e:

            print()
            print("========================================")
            print("HULA API ERROR")
            print("========================================")

            print(
                repr(e)
            )

            self.api = None

            return False

        # ======================================================
        # CONNECT
        #
        # สำคัญ:
        # connect() อยู่ตรงนี้ ไม่ใช่ใน worker
        # ======================================================

        try:

            print(
                "Connecting to Hula..."
            )

            print(
                "Calling Hula connect..."
            )

            result = self.api.connect()

            print(
                "Hula connect result:",
                result
            )

        except Exception as e:

            print()
            print("========================================")
            print("HULA CONNECT ERROR")
            print("========================================")

            print(
                repr(e)
            )

            self.api = None
            self.connected = False

            return False

        # ======================================================
        # CONNECT FAILED
        # ======================================================

        if not result:

            print()
            print("========================================")
            print("HULA CONNECTION FAILED")
            print("========================================")

            self.api = None
            self.connected = False

            return False

        # ======================================================
        # CONNECT SUCCESS
        # ======================================================

        self.connected = True
        self.running = True

        # ======================================================
        # START WORKER
        # ======================================================

        print(
            "Starting Hula worker..."
        )

        self.worker = threading.Thread(
            target=self._worker_loop,
            name="HulaWorker",
            daemon=False
        )

        self.worker.start()

        print()
        print("========================================")
        print("HULA CONNECTED")
        print("========================================")

        return True

    # ==========================================================
    # WORKER
    #
    # Worker ไม่ connect Hula
    #
    # Worker มีหน้าที่:
    # - execute command
    # - receive RTP frame
    # ==========================================================

    def _worker_loop(self):

        print(
            "Hula worker started"
        )

        try:

            while self.running:

                command = None

                # ==================================================
                # GET COMMAND
                # ==================================================

                with self.command_lock:

                    if self.pending_command is not None:

                        command = self.pending_command

                        self.pending_command = None

                # ==================================================
                # EXECUTE COMMAND
                # ==================================================

                if command is not None:

                    action = command["action"]

                    args = command["args"]

                    self.last_result = None

                    print()
                    print("========================================")
                    print("HULA EXECUTING")
                    print("========================================")

                    print(
                        "Action:",
                        action
                    )

                    print(
                        "Source:",
                        command.get(
                            "source",
                            "manual"
                        )
                    )

                    try:

                        result = self._execute_command(
                            action,
                            args
                        )

                        self.last_result = (
                            True
                            if result is None
                            else bool(result)
                        )

                    except Exception as e:

                        print()
                        print("========================================")
                        print("HULA COMMAND ERROR")
                        print("========================================")

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

                        with self.command_lock:

                            self.busy = (
                                self.pending_command
                                is not None
                            )

                    continue

                # ==================================================
                # CAMERA FRAME
                # ==================================================

                if self.camera_running:

                    try:

                        frame = (
                            self.api.get_image_array()
                        )

                        if frame is not None:

                            with self.frame_lock:

                                self.frame = frame

                    except Exception:

                        # pyhula decoder อาจ error เป็นช่วง ๆ
                        # ไม่ spam console
                        pass

                    self._poll_battery_if_due()

                    time.sleep(
                        self.FRAME_INTERVAL
                    )

                    continue

                # ==================================================
                # IDLE
                # ==================================================

                with self.command_lock:

                    if self.pending_command is None:

                        self.busy = False

                self._poll_battery_if_due()

                time.sleep(
                    self.FRAME_INTERVAL
                )

        except Exception as e:

            print()
            print("========================================")
            print("HULA WORKER ERROR")
            print("========================================")

            print(
                repr(e)
            )

            self.connected = False
            self.camera_running = False

            with self.command_lock:

                self.pending_command = None
                self.busy = False

        finally:

            self.camera_running = False

            with self.command_lock:

                self.pending_command = None
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

        # ======================================================
        # TAKE OFF
        # ======================================================

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

            return (
                True
                if result is None
                else bool(result)
            )

        # ======================================================
        # LANDING
        # ======================================================

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

            return (
                True
                if result is None
                else bool(result)
            )

        # ======================================================
        # FORWARD
        # ======================================================

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
                f"FORWARD {distance} cm "
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

        # ======================================================
        # BACKWARD
        # ======================================================

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
                f"BACKWARD {distance} cm "
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

        # ======================================================
        # LEFT
        # ======================================================

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
                f"LEFT {distance} cm "
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

        # ======================================================
        # RIGHT
        # ======================================================

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
                f"RIGHT {distance} cm "
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

        # ======================================================
        # ROTATE LEFT
        # ======================================================

        if action == "rotate_left":

            angle = self._to_int(
                args["angle"],
                "rotate left angle"
            )

            print(
                f"ROTATE LEFT {angle} degrees"
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

        # ======================================================
        # ROTATE RIGHT
        # ======================================================

        if action == "rotate_right":

            angle = self._to_int(
                args["angle"],
                "rotate right angle"
            )

            print(
                f"ROTATE RIGHT {angle} degrees"
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

        # ======================================================
        # UP
        # ======================================================

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
                f"UP {distance} cm "
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

        # ======================================================
        # DOWN
        # ======================================================

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
                f"DOWN {distance} cm "
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

        # ======================================================
        # CAMERA ANGLE
        # ======================================================

        if action == "camera_angle":

            direction = args["direction"]

            value = self._to_int(
                args["value"],
                "camera angle"
            )

            value = max(
                0,
                min(
                    90,
                    value
                )
            )

            if direction == "down":

                hula_direction = 1

            elif direction == "up":

                hula_direction = 0

            else:

                print(
                    "Unknown camera direction:",
                    direction
                )

                return False

            print(
                f"CAMERA "
                f"{direction.upper()} "
                f"{value}"
            )

            try:

                result = (
                    self.api.Plane_cmd_camera_angle(
                        hula_direction,
                        value
                    )
                )

            except Exception as e:

                print(
                    "CAMERA ANGLE exception:",
                    repr(e)
                )

                return False

            print(
                "CAMERA ANGLE result:",
                result
            )

            return (
                True
                if result is None
                else bool(result)
            )

        # ======================================================
        # START RTP
        # ======================================================

        if action == "start_camera":

            print(
                "Starting RTP..."
            )

            with self.camera_lock:

                if self.camera_running:

                    print(
                        "RTP is already running."
                    )

                    return True

                with self.frame_lock:

                    self.frame = None

                try:

                    # ------------------------------------------
                    # STEP 1
                    # ------------------------------------------

                    print(
                        "Enabling RTP..."
                    )

                    result = (
                        self.api.Plane_cmd_swith_rtp(0)
                    )

                    print(
                        "RTP switch result:",
                        result
                    )

                    # ------------------------------------------
                    # STEP 2
                    # ------------------------------------------

                    time.sleep(
                        2.0
                    )

                    # ------------------------------------------
                    # STEP 3
                    # ------------------------------------------

                    print(
                        "Starting RTP flip..."
                    )

                    result = (
                        self.api.single_fly_flip_rtp()
                    )

                    print(
                        "RTP flip result:",
                        result
                    )

                    # ------------------------------------------
                    # STEP 4
                    # ------------------------------------------

                    time.sleep(
                        2.0
                    )

                    # ------------------------------------------
                    # STEP 5
                    # ------------------------------------------

                    self.camera_running = True

                    print(
                        "RTP started."
                    )

                    return True

                except Exception as e:

                    print(
                        "RTP start error:",
                        repr(e)
                    )

                    self.camera_running = False

                    return False

        # ======================================================
        # STOP RTP
        # ======================================================

        if action == "stop_camera":

            print(
                "Disabling RTP..."
            )

            with self.camera_lock:

                try:

                    result = (
                        self.api.Plane_cmd_swith_rtp(1)
                    )

                    print(
                        "RTP disable result:",
                        result
                    )

                except Exception as e:

                    print(
                        "RTP stop error:",
                        repr(e)
                    )

                    self.camera_running = False

                    return False

                self.camera_running = False

                with self.frame_lock:

                    self.frame = None

                time.sleep(
                    0.5
                )

                return True

        # ======================================================
        # UNKNOWN
        # ======================================================

        print(
            "Unknown Hula command:",
            action
        )

        return False

    # ==========================================================
    # MANUAL COMMAND
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

            # ==================================================
            # LATEST MANUAL COMMAND WINS
            # ==================================================

            if self.pending_command is not None:

                old_action = (
                    self.pending_command["action"]
                )

                self.pending_command = {

                    "action": action,

                    "args": args,

                    "source": "manual"
                }

                print()
                print("========================================")
                print("MANUAL COMMAND REPLACED")
                print("========================================")

                print(
                    "Old:",
                    old_action
                )

                print(
                    "New:",
                    action
                )

                print(
                    "Reason: latest manual command wins"
                )

                print(
                    "========================================"
                )

                self.busy = True

                self.last_result = None

                return True

            self.pending_command = {

                "action": action,

                "args": args,

                "source": "manual"
            }

            self.busy = True

            self.last_result = None

        return True

    # ==========================================================
    # QR COMMAND
    # ==========================================================

    def submit_qr(
        self,
        action,
        **args
    ):

        if not self.connected:

            print(
                f"Cannot submit QR '{action}': "
                "Hula is not connected."
            )

            return False

        if not self.running:

            print(
                f"Cannot submit QR '{action}': "
                "Hula worker is not running."
            )

            return False

        with self.command_lock:

            if self.pending_command is not None:

                print()
                print("========================================")
                print("QR COMMAND REJECTED")
                print("========================================")

                print(
                    "Action:",
                    action
                )

                print(
                    "Reason: another command is already queued."
                )

                print(
                    "========================================"
                )

                return False

            if self.busy:

                print()
                print("========================================")
                print("QR COMMAND REJECTED")
                print("========================================")

                print(
                    "Action:",
                    action
                )

                print(
                    "Reason: Hula is currently executing "
                    "another command."
                )

                print(
                    "QR command will NOT be queued."
                )

                print(
                    "========================================"
                )

                return False

            self.pending_command = {

                "action": action,

                "args": args,

                "source": "qr"
            }

            self.busy = True

            self.last_result = None

        print()
        print("========================================")
        print("QR COMMAND ACCEPTED")
        print("========================================")

        print(
            "Action:",
            action
        )

        print(
            "Source: QR"
        )

        print(
            "Queue: NONE"
        )

        print(
            "========================================"
        )

        return True

    # ==========================================================
    # WAIT COMMAND
    # ==========================================================

    def wait_command(
        self,
        timeout=10.0
    ):

        deadline = (
            time.monotonic()
            + timeout
        )

        while self.running:

            with self.command_lock:

                busy = self.busy

            if not busy:

                return (
                    self.last_result
                    is True
                )

            if time.monotonic() >= deadline:

                return False

            time.sleep(
                0.01
            )

        return False

    # ==========================================================
    # BUSY
    # ==========================================================

    def is_busy(self):

        with self.command_lock:

            return self.busy

    # ==========================================================
    # RESULT
    # ==========================================================

    def get_last_result(self):

        return self.last_result

    # ==========================================================
    # CAMERA ANGLE
    # ==========================================================

    def set_camera_angle(
        self,
        direction,
        value
    ):

        if direction not in (
            "up",
            "down"
        ):

            print(
                "Invalid camera direction:",
                direction
            )

            return False

        value = self._to_int(
            value,
            "camera angle"
        )

        value = max(
            0,
            min(
                90,
                value
            )
        )

        return self.submit(
            "camera_angle",
            direction=direction,
            value=value
        )

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

        with self.command_lock:

            if self.busy:

                print(
                    "Cannot start camera: "
                    "Hula is busy."
                )

                return False

            self.pending_command = {

                "action": "start_camera",

                "args": {},

                "source": "camera"
            }

            self.busy = True

            self.last_result = None

        return self.wait_command(
            timeout=10.0
        )

    # ==========================================================
    # GET FRAME
    # ==========================================================

    def get_frame(self):

        with self.frame_lock:

            if self.frame is None:

                return None

            try:

                return self.frame.copy()

            except Exception:

                return None

    # ==========================================================
    # POLL BATTERY (called from worker thread only)
    # ==========================================================

    def _poll_battery_if_due(self):

        now = time.time()

        if (
            now - self._battery_last_poll
        ) < self.BATTERY_POLL_INTERVAL:

            return

        self._battery_last_poll = now

        value = None

        try:

            if hasattr(self.api, "get_electic"):

                value = self.api.get_electic()

            elif hasattr(self.api, "get_battery"):

                value = self.api.get_battery()

        except Exception:

            value = None

        with self.battery_lock:

            self.battery_level = (
                "--"
                if value is None
                else str(value)
            )

    # ==========================================================
    # GET BATTERY
    # ==========================================================

    def get_battery(self):

        with self.battery_lock:

            return self.battery_level

    # ==========================================================
    # STOP CAMERA
    # ==========================================================

    def stop_camera(self):

        if not self.connected:

            return False

        if not self.camera_running:

            with self.frame_lock:

                self.frame = None

            return True

        with self.command_lock:

            if self.pending_command is not None:

                if (
                    self.pending_command["action"]
                    ==
                    "stop_camera"
                ):

                    return True

                print(
                    "Cannot stop camera: "
                    "another command is queued."
                )

                return False

            if self.busy:

                print(
                    "Hula is busy. "
                    "Camera stop command was not queued."
                )

                return False

            self.pending_command = {

                "action": "stop_camera",

                "args": {},

                "source": "camera"
            }

            self.busy = True

            self.last_result = None

        return self.wait_command(
            timeout=5.0
        )

    # ==========================================================
    # SHUTDOWN
    # ==========================================================

    def stop(self):

        print()
        print(
            "Stopping Hula worker..."
        )

        # ======================================================
        # STOP RTP FIRST
        # ======================================================

        if (
            self.connected
            and
            self.camera_running
            and
            self.api is not None
        ):

            print(
                "Stopping RTP before Hula shutdown..."
            )

            try:

                self._execute_command(
                    "stop_camera",
                    {}
                )

            except Exception as e:

                print(
                    "RTP shutdown error:",
                    repr(e)
                )

        # ======================================================
        # STOP WORKER
        # ======================================================

        self.running = False

        with self.command_lock:

            self.pending_command = None
            self.busy = False

        if self.worker is not None:

            self.worker.join(
                timeout=5.0
            )

        if (
            self.worker is not None
            and
            self.worker.is_alive()
        ):

            print(
                "WARNING: Hula worker did not stop cleanly."
            )

        self.worker = None

        self.camera_running = False

        with self.frame_lock:

            self.frame = None

        self.connected = False

        # ======================================================
        # DISCONNECT PYHULA INTERNAL SDK
        #
        # UserApi ไม่มีเมธอด disconnect() ให้เรียกตรงๆ
        # แต่ตัว Controlserver ข้างในมี disconnect()
        # ซึ่งจะเรียก stop_all_task() เพื่อหยุด thread
        # ภายในทั้งหมด (tcp_server_thread, mavanalyzer,
        # udp_recive_thread ฯลฯ)
        #
        # ถ้าไม่เรียกตรงนี้ thread เหล่านี้จะยังทำงานต่อ
        # แม้เราจะทิ้ง self.api = None ไปแล้ว ทำให้เกิด
        # CRC spam ไม่หยุด และ Fatal Python error ตอนปิดโปรแกรม
        # ======================================================

        if self.api is not None:

            try:

                print(
                    "Disconnecting pyhula internal SDK..."
                )

                self.api._control_server.disconnect()

            except Exception as e:

                print(
                    "pyhula internal disconnect error:",
                    repr(e)
                )

        self.api = None

        print(
            "Hula stopped"
        )