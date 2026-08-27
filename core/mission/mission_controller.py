import time
import winsound


class MissionController:

    def __init__(
        self,
        bridge,
        config
    ):

        self.bridge = bridge
        self.config = config

        self.running = False

        # ==========================================================
        # MODE
        # ==========================================================

        self.mode = getattr(
            self.config,
            "MISSION_START_MODE",
            getattr(
                self.config,
                "DEFAULT_MODE",
                "MANUAL"
            )
        ).upper()

        if self.mode not in (
            "MANUAL",
            "AUTO"
        ):

            self.mode = "MANUAL"

        # ==========================================================
        # MISSION STATE
        # ==========================================================

        self.mission_state = "WAITING"

        # ==========================================================
        # QR FOCUS STATE
        # ==========================================================

        self.focus_locked = False
        self.focus_qr_id = None

        self.focus_x = None
        self.focus_y = None

        self.last_center_x = None
        self.last_center_y = None

        # ==========================================================
        # QR RE-ENTRY STATE
        # ==========================================================

        self.qr_inside = False
        self.qr_triggered_this_entry = False

        # ==========================================================
        # CORRECTION STATE
        # ==========================================================

        self.correction_active = False
        self.correction_count = 0

        self.correction_started_at = 0.0
        self.last_correction_at = 0.0

        # ==========================================================
        # CURRENT MISSION TARGET
        # ==========================================================

        self.target_qr_id = None
        self.target_action = None

        # ==========================================================
        # FLIGHT STATE
        # ==========================================================

        self.flight_state = "LANDED"

        # ==========================================================
        # TAKEOFF READY TIME
        # ==========================================================

        self.takeoff_ready_at = 0.0

        # ==========================================================
        # TAKEOFF QUEUE
        # ==========================================================

        self.pending_takeoff = False

        # ==========================================================
        # COMMAND QUEUE
        # ==========================================================

        self.pending_action = None
        self.pending_source = None

        # ==========================================================
        # CURRENT COMMAND
        # ==========================================================

        self.current_action = None
        self.current_source = None

        # ==========================================================
        # QR COOLDOWN
        # ==========================================================

        self.last_qr = None
        self.last_qr_time = 0.0

        # ==========================================================
        # QR POST COUNTDOWN COOLDOWN
        # ==========================================================

        self.qr_cooldown_until = 0.0
        self.qr_cooldown_source = None
        self.qr_cooldown_qr_id = None

        # ==========================================================
        # COMMAND DELAY
        # ==========================================================

        self.command_wait_until = 0.0
        self.command_warning_next_at = 0.0
        self.command_warning_count = 0

        # ==========================================================
        # COMMAND DELAY SOURCE
        # ==========================================================

        self.command_wait_source = None

    # ==========================================================
    # START
    # ==========================================================

    def start(self):

        if self.running:
            return

        self.running = True

        start_mode = getattr(
            self.config,
            "MISSION_START_MODE",
            getattr(
                self.config,
                "DEFAULT_MODE",
                "MANUAL"
            )
        ).upper()

        if start_mode not in (
            "MANUAL",
            "AUTO"
        ):

            start_mode = "MANUAL"

        self.mode = start_mode

        self._reset_focus_state()
        self._clear_command_delay()
        self._clear_qr_cooldown()

        if self.mode == "AUTO":
            self.mission_state = "SEARCHING_QR"
        else:
            self.mission_state = "WAITING"

        print()
        print("========================================")
        print("MISSION CONTROLLER STARTED")
        print("========================================")

        print("Mode:", self.mode)
        print("Mission state:", self.mission_state)

    # ==========================================================
    # MODE CONTROL
    # ==========================================================

    def set_mode(
        self,
        mode
    ):

        mode = str(mode).upper()

        if mode not in (
            "MANUAL",
            "AUTO"
        ):

            print(
                "Unknown mode:",
                mode
            )

            return False

        if self.mode == mode:

            print(
                "Already in",
                mode,
                "mode."
            )

            return True

        if mode == "MANUAL":
            self.correction_active = False

        self.mode = mode

        self._reset_focus_state()
        self._clear_command_delay()
        self._clear_qr_cooldown()

        if mode == "AUTO":
            self._set_mission_state("SEARCHING_QR")
        else:
            self._set_mission_state("WAITING")

        print()
        print("========================================")
        print("MODE CHANGED")
        print("========================================")

        print("Mode:", self.mode)
        print("Mission state:", self.mission_state)

        return True

    # ==========================================================
    # TOGGLE MODE
    # ==========================================================

    def toggle_mode(self):

        if self.mode == "MANUAL":
            return self.set_mode("AUTO")

        return self.set_mode("MANUAL")

    # ==========================================================
    # MODE GETTERS
    # ==========================================================

    def get_mode(self):
        return self.mode

    def is_manual(self):
        return self.mode == "MANUAL"

    def is_auto(self):
        return self.mode == "AUTO"

    # ==========================================================
    # MISSION STATE
    # ==========================================================

    def get_mission_state(self):
        return self.mission_state

    # ==========================================================
    # UI STATUS GETTERS
    # ==========================================================

    def get_flight_state(self):
        return self.flight_state

    def get_target_qr(self):
        return self.target_qr_id

    def get_target_action(self):
        return self.target_action

    def get_position(self):

        if (
            self.last_center_x is None
            or self.last_center_y is None
        ):
            return None

        return (
            self.last_center_x,
            self.last_center_y
        )

    def get_focus_position(self):

        point = getattr(
            self.config,
            "QR_FOCUS_POINT",
            None
        )

        if point is not None:

            try:

                if isinstance(
                    point,
                    dict
                ):

                    return (
                        float(point["x"]),
                        float(point["y"])
                    )

                return (
                    float(point[0]),
                    float(point[1])
                )

            except (
                KeyError,
                IndexError,
                TypeError,
                ValueError
            ):

                pass

        # ------------------------------------------------------
        # fallback ใช้ focus ที่ถูก lock ไว้
        # ------------------------------------------------------

        if (
            self.focus_x is None
            or self.focus_y is None
        ):
            return None

        return (
            self.focus_x,
            self.focus_y
        )

    def is_focus_locked(self):
        return self.focus_locked

    def is_correction_active(self):
        return self.correction_active

    def get_correction_count(self):
        return self.correction_count

    def get_current_action(self):
        return self.current_action

    def get_current_source(self):
        return self.current_source

    def get_correction_distance(self):

        return float(
            getattr(
                self.config,
                "CORRECTION_DISTANCE",
                5.0
            )
        )

    def get_correction_speed(self):

        return float(
            getattr(
                self.config,
                "CORRECTION_SPEED",
                10.0
            )
        )

    def get_correction_status(self):

        if self.current_source == "AUTO CORRECTION":
            return "CORRECTING"

        if self.correction_active:
            return "CORRECTING"

        if self.mission_state == "EXECUTING":
            return "EXECUTING"

        if self.focus_locked:
            return "QR LOCKED"

        return self.mission_state

    # ==========================================================
    # COMMAND DELAY GETTERS
    # ==========================================================

    def get_command_delay(self):

        return float(
            getattr(
                self.config,
                "COMMAND_DELAY",
                10.0
            )
        )

    def get_command_warning_time(self):

        return float(
            getattr(
                self.config,
                "COMMAND_WARNING_TIME",
                5.0
            )
        )

    def get_command_warning_interval(self):

        return float(
            getattr(
                self.config,
                "COMMAND_WARNING_INTERVAL",
                1.0
            )
        )

    def get_command_warning_frequency(self):

        return int(
            getattr(
                self.config,
                "COMMAND_WARNING_FREQUENCY",
                1000
            )
        )

    def get_command_warning_duration(self):

        return int(
            getattr(
                self.config,
                "COMMAND_WARNING_DURATION",
                150
            )
        )

    def get_command_correction_stop_time(self):

        return float(
            getattr(
                self.config,
                "COMMAND_CORRECTION_STOP_TIME",
                3.0
            )
        )

    # ==========================================================
    # QR COOLDOWN GETTERS
    # ==========================================================

    def get_qr_cooldown(self):

        return float(
            getattr(
                self.config,
                "QR_POST_COUNTDOWN_COOLDOWN",
                5.0
            )
        )

    def is_qr_cooldown_active(self):

        if self.qr_cooldown_until <= 0.0:
            return False

        return (
            time.monotonic()
            <
            self.qr_cooldown_until
        )

    def get_qr_cooldown_remaining(self):

        if not self.is_qr_cooldown_active():
            return 0.0

        remaining = (
            self.qr_cooldown_until
            - time.monotonic()
        )

        if remaining < 0.0:
            return 0.0

        return remaining

    def get_qr_cooldown_seconds(self):

        remaining = (
            self.get_qr_cooldown_remaining()
        )

        if remaining <= 0.0:
            return 0

        return int(
            remaining + 0.999
        )

    def _clear_qr_cooldown(self):

        self.qr_cooldown_until = 0.0
        self.qr_cooldown_source = None
        self.qr_cooldown_qr_id = None

    def _start_qr_cooldown(
        self,
        qr_id=None,
        source=None
    ):

        cooldown = self.get_qr_cooldown()

        if cooldown <= 0.0:

            self._clear_qr_cooldown()

            return

        now = time.monotonic()

        self.qr_cooldown_until = (
            now + cooldown
        )

        self.qr_cooldown_qr_id = qr_id
        self.qr_cooldown_source = source

        print()
        print("========================================")
        print("QR POST COUNTDOWN COOLDOWN START")
        print("========================================")

        print(
            "QR:",
            qr_id
        )

        print(
            "Source:",
            source
        )

        print(
            f"Next QR command allowed "
            f"in {cooldown:.1f}s"
        )

    # ==========================================================
    # COMMAND COUNTDOWN FOR UI
    # ==========================================================

    def is_command_countdown_active(self):

        if self.command_wait_until <= 0.0:
            return False

        if not self._is_qr_source(
            self.command_wait_source
        ):
            return False

        if not self._is_qr_source(
            self.pending_source
        ):
            return False

        return (
            time.monotonic()
            <
            self.command_wait_until
        )

    # ==========================================================
    # GET REMAINING COMMAND COUNTDOWN
    # ==========================================================

    def get_command_countdown(self):

        if not self.is_command_countdown_active():
            return 0.0

        remaining = (
            self.command_wait_until
            - time.monotonic()
        )

        if remaining < 0.0:
            remaining = 0.0

        return remaining

    # ==========================================================
    # GET COMMAND COUNTDOWN INTEGER
    # ==========================================================

    def get_command_countdown_seconds(self):

        remaining = self.get_command_countdown()

        if remaining <= 0.0:
            return 0

        return int(
            remaining + 0.999
        )

    # ==========================================================
    # GET COMMAND COUNTDOWN SOURCE
    # ==========================================================

    def get_command_countdown_source(self):

        if not self.is_command_countdown_active():
            return None

        return self.command_wait_source

    # ==========================================================
    # SET MISSION STATE
    # ==========================================================

    def _set_mission_state(
        self,
        state
    ):

        if self.mission_state == state:
            return

        self.mission_state = state

        print(
            "Mission state:",
            state
        )

    # ==========================================================
    # RESET FOCUS STATE
    # ==========================================================

    def _reset_focus_state(self):

        self.focus_locked = False
        self.focus_qr_id = None

        self.focus_x = None
        self.focus_y = None

        self.last_center_x = None
        self.last_center_y = None

        self.qr_inside = False
        self.qr_triggered_this_entry = False

        self.correction_active = False
        self.correction_count = 0

        self.correction_started_at = 0.0
        self.last_correction_at = 0.0

        self.target_qr_id = None
        self.target_action = None

        self.last_qr = None
        self.last_qr_time = 0.0

    # ==========================================================
    # CHECK QR SOURCE
    # ==========================================================

    def _is_qr_source(
        self,
        source
    ):

        if source is None:
            return False

        return str(
            source
        ).upper().startswith(
            "QR "
        )

    # ==========================================================
    # GET GLOBAL FOCUS POINT
    # ==========================================================

    def _get_qr_id_from_source(
        self,
        source
    ):

        # ------------------------------------------------------
        # source มีรูปแบบ "QR qr3" -> ดึงเอาแค่ "qr3"
        # ------------------------------------------------------

        if not self._is_qr_source(
            source
        ):

            return None

        return str(
            source
        )[3:].strip()

    def _get_qr_movement_override(
        self,
        qr_id
    ):

        # ------------------------------------------------------
        # QR_MOVEMENT_OVERRIDES ใน config.py
        # ใช้กำหนดระยะ/ความเร็วเฉพาะของแต่ละ QR
        # ------------------------------------------------------

        overrides = getattr(
            self.config,
            "QR_MOVEMENT_OVERRIDES",
            {}
        )

        if not qr_id:
            return {}

        return overrides.get(
            qr_id,
            {}
        ) or {}

    def _resolve_distance_speed(
        self,
        source,
        default_distance,
        default_speed
    ):

        qr_id = self._get_qr_id_from_source(
            source
        )

        override = self._get_qr_movement_override(
            qr_id
        )

        distance = override.get(
            "distance",
            default_distance
        )

        speed = override.get(
            "speed",
            default_speed
        )

        return distance, speed

    def _get_focus_point(self):

        point = getattr(
            self.config,
            "QR_FOCUS_POINT",
            None
        )

        if point is None:

            return None

        try:

            if isinstance(
                point,
                dict
            ):

                return (
                    float(point["x"]),
                    float(point["y"])
                )

            return (
                float(point[0]),
                float(point[1])
            )

        except (
            KeyError,
            IndexError,
            TypeError,
            ValueError
        ):

            print(
                "Invalid QR_FOCUS_POINT:",
                point
            )

            return None

    # ==========================================================
    # GET FOCUS TOLERANCE
    # ==========================================================

    def _get_focus_tolerance(self):

        return float(
            getattr(
                self.config,
                "FOCUS_TOLERANCE",
                50.0
            )
        )

    # ==========================================================
    # GET FOCUS DIFFERENCE
    # ==========================================================

    def _get_focus_diff(
        self,
        center_x,
        center_y
    ):

        if (
            self.focus_x is None
            or self.focus_y is None
        ):

            return None

        diff_x = (
            float(center_x)
            - self.focus_x
        )

        diff_y = (
            float(center_y)
            - self.focus_y
        )

        return (
            diff_x,
            diff_y
        )

    # ==========================================================
    # CHECK FOCUS
    # ==========================================================

    def _check_focus(
        self,
        center_x,
        center_y
    ):

        diff = self._get_focus_diff(
            center_x,
            center_y
        )

        if diff is None:
            return False

        diff_x, diff_y = diff

        tolerance = (
            self._get_focus_tolerance()
        )

        distance = (
            (
                diff_x ** 2
            )
            +
            (
                diff_y ** 2
            )
        ) ** 0.5

        return (
            distance
            <=
            tolerance
        )

    # ==========================================================
    # HANDLE QR
    # ==========================================================

    def handle_qr(
        self,
        qr_id,
        center_x=None,
        center_y=None
    ):

        if not self.running:
            return

        if self.mode != "AUTO":
            return

        action = self.config.QR_ACTIONS.get(
            qr_id
        )

        if action is None:
            return

        # ======================================================
        # QR POST COUNTDOWN COOLDOWN
        # ======================================================

        if self.is_qr_cooldown_active():

            return

        # ======================================================
        # GLOBAL FOCUS
        # ======================================================

        focus_point = (
            self._get_focus_point()
        )

        # ------------------------------------------------------
        # ถ้าไม่กำหนด Global Focus Point
        # ใช้ center ของภาพจากตำแหน่ง QR
        # ------------------------------------------------------

        if focus_point is None:

            if (
                center_x is not None
                and center_y is not None
            ):

                self.last_center_x = float(
                    center_x
                )

                self.last_center_y = float(
                    center_y
                )

                self.focus_qr_id = qr_id
                self.target_qr_id = qr_id
                self.target_action = action

                self.focus_x = float(
                    center_x
                )

                self.focus_y = float(
                    center_y
                )

                self.qr_inside = True
                self.focus_locked = True

                self._set_mission_state(
                    "QR_LOCKED"
                )

                if not self.qr_triggered_this_entry:

                    self._trigger_qr(
                        qr_id,
                        action
                    )

            return

        # ======================================================
        # NEED CENTER
        # ======================================================

        if (
            center_x is None
            or center_y is None
        ):

            self._set_mission_state(
                "SEARCHING_QR"
            )

            return

        self.last_center_x = float(
            center_x
        )

        self.last_center_y = float(
            center_y
        )

        # ======================================================
        # CHECK FOCUS
        # ======================================================

        qr_inside_focus = (
            self._check_position_against_focus(
                center_x,
                center_y,
                focus_point[0],
                focus_point[1]
            )
        )

        # ======================================================
        # QR INSIDE FOCUS
        # ======================================================

        if qr_inside_focus:

            if (
                self.correction_active
                and
                self.target_qr_id == qr_id
            ):

                self.correction_active = False
                self.correction_count = 0

                self.focus_qr_id = qr_id

                self.focus_x = focus_point[0]
                self.focus_y = focus_point[1]

                self.qr_inside = True
                self.focus_locked = True

                self._set_mission_state(
                    "QR_LOCKED"
                )

                print()
                print("========================================")
                print("QR RETURNED TO FOCUS")
                print("========================================")

                print(
                    "QR:",
                    qr_id
                )

                print(
                    "Focus:",
                    (
                        self.focus_x,
                        self.focus_y
                    )
                )

                self.qr_triggered_this_entry = False

                self._trigger_qr(
                    qr_id,
                    action
                )

                return

            if self.focus_qr_id != qr_id:

                self.focus_qr_id = qr_id

                self.target_qr_id = qr_id
                self.target_action = action

                self.focus_x = focus_point[0]
                self.focus_y = focus_point[1]

                self.qr_inside = False
                self.focus_locked = False

                self.qr_triggered_this_entry = False

                self.correction_active = False
                self.correction_count = 0

            else:

                self.target_qr_id = qr_id
                self.target_action = action

                self.focus_x = focus_point[0]
                self.focus_y = focus_point[1]

            if not self.qr_inside:

                self.qr_inside = True
                self.focus_locked = True

                self.correction_active = False
                self.correction_count = 0

                self._set_mission_state(
                    "QR_LOCKED"
                )

                print()
                print("========================================")
                print("QR FOCUS LOCKED")
                print("========================================")

                print(
                    "QR:",
                    qr_id
                )

                print(
                    "Focus:",
                    (
                        self.focus_x,
                        self.focus_y
                    )
                )

                print(
                    "Drone:",
                    (
                        round(center_x, 1),
                        round(center_y, 1)
                    )
                )

            if not self.qr_triggered_this_entry:

                self._trigger_qr(
                    qr_id,
                    action
                )

            return

        # ======================================================
        # QR OUTSIDE FOCUS
        # ======================================================

        target_changed = (
            self.focus_qr_id
            !=
            qr_id
        )

        if target_changed:

            self.focus_qr_id = qr_id

            self.target_qr_id = qr_id
            self.target_action = action

            self.focus_x = focus_point[0]
            self.focus_y = focus_point[1]

            self.qr_inside = False
            self.focus_locked = False

            self.qr_triggered_this_entry = False

            self.correction_count = 0

            if self.correction_active:

                self.correction_started_at = (
                    time.monotonic()
                )

                self.last_correction_at = 0.0

                print()
                print("========================================")
                print("CORRECTION TARGET CHANGED")
                print("========================================")

                print(
                    "QR:",
                    qr_id
                )

                print(
                    "Action:",
                    action
                )

            else:

                self._start_correction()

            return

        self.target_qr_id = qr_id
        self.target_action = action

        self.focus_x = focus_point[0]
        self.focus_y = focus_point[1]

        self.qr_inside = False
        self.focus_locked = False

        if not self.correction_active:

            self._start_correction()

    # ==========================================================
    # CHECK POSITION AGAINST SPECIFIC FOCUS
    # ==========================================================

    def _check_position_against_focus(
        self,
        center_x,
        center_y,
        focus_x,
        focus_y
    ):

        diff_x = (
            float(center_x)
            - float(focus_x)
        )

        diff_y = (
            float(center_y)
            - float(focus_y)
        )

        tolerance = (
            self._get_focus_tolerance()
        )

        distance = (
            (
                diff_x ** 2
                +
                diff_y ** 2
            ) ** 0.5
        )

        return (
            distance
            <=
            tolerance
        )

    # ==========================================================
    # TRIGGER QR
    # ==========================================================

    def _trigger_qr(
        self,
        qr_id,
        action
    ):

        if self.qr_triggered_this_entry:
            return

        if self.is_qr_cooldown_active():
            return

        # ------------------------------------------------------
        # ถ้ามี QR command countdown อยู่
        # command ที่ lock ไว้ต้องคงเดิม
        # ------------------------------------------------------

        if self.is_command_countdown_active():

            print(
                "QR ignored: "
                "another QR command is counting down."
            )

            return

        now = time.monotonic()

        cooldown = float(
            getattr(
                self.config,
                "QR_COOLDOWN",
                0.0
            )
        )

        if (
            self.last_qr == qr_id
            and
            (
                now
                - self.last_qr_time
            ) < cooldown
        ):

            return

        self.qr_triggered_this_entry = True

        self.last_qr = qr_id
        self.last_qr_time = now

        self.target_qr_id = qr_id
        self.target_action = action

        print()
        print("========================================")
        print("QR TRIGGER")
        print("========================================")

        print(
            "QR:",
            qr_id
        )

        print(
            "Action:",
            action
        )

        self._set_mission_state(
            "EXECUTING"
        )

        self._request_action(
            action,
            source=f"QR {qr_id}"
        )

    # ==========================================================
    # COMMAND DELAY CONFIG
    # ==========================================================

    def _get_command_delay(self):

        return float(
            getattr(
                self.config,
                "COMMAND_DELAY",
                10.0
            )
        )

    def _get_command_warning_time(self):

        return float(
            getattr(
                self.config,
                "COMMAND_WARNING_TIME",
                5.0
            )
        )

    def _get_command_warning_interval(self):

        return float(
            getattr(
                self.config,
                "COMMAND_WARNING_INTERVAL",
                1.0
            )
        )

    def _get_command_warning_frequency(self):

        return int(
            getattr(
                self.config,
                "COMMAND_WARNING_FREQUENCY",
                1000
            )
        )

    def _get_command_warning_duration(self):

        return int(
            getattr(
                self.config,
                "COMMAND_WARNING_DURATION",
                150
            )
        )

    # ==========================================================
    # CLEAR COMMAND DELAY
    # ==========================================================

    def _clear_command_delay(self):

        self.command_wait_until = 0.0
        self.command_warning_next_at = 0.0
        self.command_warning_count = 0
        self.command_wait_source = None

    # ==========================================================
    # START COMMAND DELAY
    # ==========================================================

    def _start_command_delay(
        self,
        source=None
    ):

        if not self._is_qr_source(source):

            self._clear_command_delay()

            return

        delay = self._get_command_delay()

        if delay <= 0.0:

            self._clear_command_delay()

            return

        now = time.monotonic()

        self.command_wait_until = (
            now + delay
        )

        self.command_wait_source = source

        warning_time = (
            self._get_command_warning_time()
        )

        self.command_warning_next_at = (
            self.command_wait_until
            - warning_time
        )

        self.command_warning_count = 0

        print()
        print("========================================")
        print("QR COMMAND COUNTDOWN START")
        print("========================================")

        print(
            "Command received from:",
            source
        )

        print(
            f"Executing in {delay:.1f}s"
        )

        print(
            f"Warning starts with "
            f"{warning_time:.1f}s remaining."
        )

        if (
            self._get_command_warning_interval()
            <= 0.0
        ):

            self.command_warning_next_at = (
                self.command_wait_until
            )

    # ==========================================================
    # CHECK COMMAND DELAY
    # ==========================================================

    def _is_command_waiting(self):

        if self.command_wait_until <= 0.0:
            return False

        if not self._is_qr_source(
            self.command_wait_source
        ):

            self._clear_command_delay()

            return False

        if not self._is_qr_source(
            self.pending_source
        ):

            self._clear_command_delay()

            return False

        return (
            time.monotonic()
            <
            self.command_wait_until
        )

    # ==========================================================
    # COMMAND DELAY UPDATE
    # ==========================================================

    def _update_command_delay(self):

        if self.command_wait_until <= 0.0:
            return

        if not self._is_qr_source(
            self.command_wait_source
        ):

            self._clear_command_delay()

            return

        if not self._is_qr_source(
            self.pending_source
        ):

            self._clear_command_delay()

            return

        now = time.monotonic()

        if now >= self.command_wait_until:

            print()
            print("========================================")
            print("QR COUNTDOWN FINISHED")
            print("========================================")

            print(
                "QR command execution allowed."
            )

            qr_id = self.target_qr_id
            source = self.command_wait_source

            # ==================================================
            # LOCKED COMMAND
            # ==================================================

            action = self.pending_action

            self._clear_command_delay()

            # ==================================================
            # POST COUNTDOWN QR COOLDOWN
            # ==================================================

            self._start_qr_cooldown(
                qr_id=qr_id,
                source=source
            )

            # ==================================================
            # EXECUTE LOCKED QR COMMAND
            # ==================================================

            if (
                action is not None
                and
                source is not None
            ):

                self.pending_action = None
                self.pending_source = None

                print()
                print("========================================")
                print("EXECUTE LOCKED QR COMMAND")
                print("========================================")

                print(
                    "Action:",
                    action
                )

                print(
                    "Source:",
                    source
                )

                self._submit_action(
                    action,
                    source
                )

            return

        # ======================================================
        # WARNING SOUND
        # ======================================================

        if (
            self.command_warning_next_at > 0.0
            and
            now >= self.command_warning_next_at
        ):

            remaining = (
                self.command_wait_until
                - now
            )

            if remaining < 0.0:

                remaining = 0.0

            seconds = int(
                remaining + 0.999
            )

            if seconds > 5:

                seconds = 5

            if seconds < 1:

                seconds = 1

            print(
                f"QR COMMAND WARNING: {seconds}s"
            )

            try:

                winsound.Beep(
                    self._get_command_warning_frequency(),
                    self._get_command_warning_duration()
                )

            except Exception as e:

                print(
                    "Warning sound error:",
                    repr(e)
                )

            self.command_warning_count += 1

            interval = (
                self._get_command_warning_interval()
            )

            if interval > 0.0:

                self.command_warning_next_at += (
                    interval
                )

            else:

                self.command_warning_next_at = 0.0

    # ==========================================================
    # UPDATE
    # ==========================================================

    def update(self):

        if not self.running:
            return

        # ======================================================
        # UPDATE QR COUNTDOWN
        # ======================================================

        self._update_command_delay()

        # ======================================================
        # CURRENT ACTION FINISHED
        # ======================================================

        if (
            self.current_action is not None
            and
            not self.bridge.is_busy()
        ):

            self._finish_current_action()

        # ======================================================
        # AUTO CORRECTION
        # ======================================================

        if self.mode == "AUTO":

            self._update_correction()

        # ======================================================
        # PENDING ACTION
        # ======================================================

        if (
            self.current_action is None
            and
            self.pending_action is not None
        ):

            if self._is_command_waiting():

                return

            action = self.pending_action
            source = self.pending_source

            if action in (
                "take_off",
                "manual_take_off"
            ):

                now = time.monotonic()

                if now < self.takeoff_ready_at:

                    return

            self.pending_action = None
            self.pending_source = None

            if action in (
                "take_off",
                "manual_take_off"
            ):

                self.pending_takeoff = False

            self._submit_action(
                action,
                source
            )

    # ==========================================================
    # START CORRECTION
    # ==========================================================

    def _start_correction(self):

        if self.mode != "AUTO":
            return

        if self.focus_qr_id is None:
            return

        if self.correction_active:
            return

        self.correction_active = True

        self.correction_count = 0

        self.correction_started_at = (
            time.monotonic()
        )

        self.last_correction_at = 0.0

        self._set_mission_state(
            "CORRECTING"
        )

        print()
        print("========================================")
        print("START CORRECTION")
        print("========================================")

        print(
            "Target QR:",
            self.focus_qr_id
        )

        print(
            "Target Action:",
            self.target_action
        )

        print(
            "Focus:",
            (
                self.focus_x,
                self.focus_y
            )
        )

    # ==========================================================
    # CORRECTION CONFIG
    # ==========================================================

    def _get_correction_distance(self):

        return float(
            getattr(
                self.config,
                "CORRECTION_DISTANCE",
                5.0
            )
        )

    def _get_correction_speed(self):

        return float(
            getattr(
                self.config,
                "CORRECTION_SPEED",
                10.0
            )
        )

    def _get_correction_interval(self):

        return float(
            getattr(
                self.config,
                "CORRECTION_INTERVAL",
                0.3
            )
        )

    def _get_correction_max_count(self):

        return int(
            getattr(
                self.config,
                "CORRECTION_MAX_COUNT",
                10
            )
        )

    def _get_correction_timeout(self):

        return float(
            getattr(
                self.config,
                "CORRECTION_TIMEOUT",
                10.0
            )
        )

    # ==========================================================
    # CALCULATE CORRECTION
    # ==========================================================

    def _calculate_correction_action(self):

        if (
            self.last_center_x is None
            or self.last_center_y is None
            or self.focus_x is None
            or self.focus_y is None
        ):

            return None

        diff_x = (
            self.last_center_x
            - self.focus_x
        )

        diff_y = (
            self.last_center_y
            - self.focus_y
        )

        tolerance = (
            self._get_focus_tolerance()
        )

        if (
            (
                diff_x ** 2
                +
                diff_y ** 2
            ) ** 0.5
            <= tolerance
        ):

            return None

        if abs(diff_x) >= abs(diff_y):

            if diff_x > tolerance:
                return "right"

            if diff_x < -tolerance:
                return "left"

        else:

            if diff_y > tolerance:
                return "backward"

            if diff_y < -tolerance:
                return "forward"

        return None

    # ==========================================================
    # UPDATE CORRECTION
    # ==========================================================

    def _update_correction(self):

        if not self.correction_active:
            return

        # ======================================================
        # STOP CORRECTION NEAR QR COMMAND EXECUTION
        # ======================================================

        if self.is_command_countdown_active():

            remaining = (
                self.get_command_countdown()
            )

            if (
                remaining
                <=
                self.get_command_correction_stop_time()
            ):

                return

        if self.current_action is not None:

            return

        if (
            self.last_center_x is None
            or self.last_center_y is None
        ):

            return

        if self._check_focus(
            self.last_center_x,
            self.last_center_y
        ):

            target_qr = self.target_qr_id
            target_action = self.target_action

            self.correction_active = False
            self.correction_count = 0

            self.qr_inside = True
            self.focus_locked = True

            self._set_mission_state(
                "QR_LOCKED"
            )

            print()
            print("========================================")
            print("FOCUS REACHED")
            print("========================================")

            print(
                "QR:",
                target_qr
            )

            print(
                "Action:",
                target_action
            )

            self.qr_triggered_this_entry = False

            if target_qr is not None:

                self._trigger_qr(
                    target_qr,
                    target_action
                )

            return

        if (
            time.monotonic()
            - self.correction_started_at
        ) >= self._get_correction_timeout():

            self.correction_active = False

            print(
                "Correction timeout."
            )

            self._set_mission_state(
                "SEARCHING_QR"
            )

            return

        if (
            self.correction_count
            >= self._get_correction_max_count()
        ):

            self.correction_active = False

            print(
                "Correction limit reached."
            )

            self._set_mission_state(
                "SEARCHING_QR"
            )

            return

        now = time.monotonic()

        if (
            self.last_correction_at > 0.0
            and
            (
                now
                - self.last_correction_at
            ) < self._get_correction_interval()
        ):

            return

        action = (
            self._calculate_correction_action()
        )

        if action is None:
            return

        print()
        print(
            "CORRECTION",
            self.correction_count + 1
        )

        print(
            "Target QR:",
            self.target_qr_id
        )

        print(
            "Target Action:",
            self.target_action
        )

        print(
            "Action:",
            action
        )

        print(
            "Current:",
            (
                round(
                    self.last_center_x,
                    1
                ),
                round(
                    self.last_center_y,
                    1
                )
            )
        )

        print(
            "Focus:",
            (
                round(
                    self.focus_x,
                    1
                ),
                round(
                    self.focus_y,
                    1
                )
            )
        )

        print(
            "Distance:",
            self._get_correction_distance(),
            "cm"
        )

        accepted = (
            self._request_correction_action(
                action
            )
        )

        if accepted:

            self.correction_count += 1

            self.last_correction_at = now

    # ==========================================================
    # REQUEST CORRECTION
    # ==========================================================

    def _request_correction_action(
        self,
        action
    ):

        distance = (
            self._get_correction_distance()
        )

        speed = (
            self._get_correction_speed()
        )

        if action in (
            "left",
            "right",
            "forward",
            "backward"
        ):

            accepted = self.bridge.submit(
                action,
                distance=distance,
                speed=speed
            )

        else:

            return False

        if not accepted:

            print(
                "Correction could not be submitted."
            )

            return False

        self.current_action = action

        self.current_source = (
            "AUTO CORRECTION"
        )

        return True

    # ==========================================================
    # REQUEST ACTION
    # ==========================================================

    def _request_action(
        self,
        action,
        source="MANUAL"
    ):

        if not self.running:
            return

        is_qr_command = (
            self._is_qr_source(
                source
            )
        )

        # ======================================================
        # QR COUNTDOWN LOCK
        # ======================================================

        if self.is_command_countdown_active():

            print()
            print(
                "COMMAND IGNORED:"
            )

            print(
                "QR command countdown is active."
            )

            print(
                "Current command:",
                self.pending_action
            )

            print(
                "Current source:",
                self.pending_source
            )

            print(
                f"Remaining:"
                f" {self.get_command_countdown():.1f}s"
            )

            return

        # ======================================================
        # QR POST COUNTDOWN COOLDOWN
        # ======================================================

        if (
            is_qr_command
            and
            self.is_qr_cooldown_active()
        ):

            print()
            print(
                "QR COMMAND IGNORED:"
            )

            print(
                "QR cooldown active."
            )

            print(
                f"Remaining:"
                f" {self.get_qr_cooldown_remaining():.1f}s"
            )

            return

        if not is_qr_command:

            self._clear_command_delay()

        # ======================================================
        # TAKEOFF SAFETY
        # ======================================================

        if action in (
            "take_off",
            "manual_take_off"
        ):

            if self.pending_takeoff:

                print(
                    "TAKEOFF ignored: "
                    "takeoff is already queued."
                )

                return

            if self.flight_state in (
                "TAKING_OFF",
                "FLYING"
            ):

                print(
                    "TAKEOFF ignored: "
                    "drone is already flying."
                )

                return

            if self.flight_state == "LANDING":

                self.pending_takeoff = True

                self._queue_action(
                    action,
                    source,
                    reason="waiting for landing"
                )

                return

            now = time.monotonic()

            if now < self.takeoff_ready_at:

                self.pending_takeoff = True

                self._queue_action(
                    action,
                    source,
                    reason="waiting after landing"
                )

                return

        # ======================================================
        # LANDING SAFETY
        # ======================================================

        if action in (
            "landing",
            "manual_landing"
        ):

            if self.flight_state in (
                "LANDED",
                "LANDING"
            ):

                print(
                    "LANDING ignored: "
                    "drone is already landed."
                )

                return

        # ======================================================
        # CURRENT COMMAND
        # ======================================================

        if self.current_action is not None:

            # --------------------------------------------------
            # ถ้ามีคำสั่งอื่นเข้าคิวรออยู่แล้ว
            # (เช่น correction คิวไว้ก่อนหน้า)
            # ไม่สามารถเข้าคิวซ้ำได้ ต้องทิ้งจริง ๆ
            # --------------------------------------------------

            if self.pending_action is not None:

                print()
                print(
                    "COMMAND IGNORED:"
                )

                print(
                    "Current command is still running "
                    "and another command is already queued."
                )

                print(
                    "Current action:",
                    self.current_action
                )

                print(
                    "Current source:",
                    self.current_source
                )

                return

            # --------------------------------------------------
            # เก็บคำสั่งนี้เข้าคิวแทนการทิ้ง
            #
            # เดิม: ถ้า current_action ไม่ว่าง (เช่น correction
            # left/right ยังทำอยู่) คำสั่งจาก QR trigger
            # (เช่น forward) จะถูกทิ้งไปเลย ไม่มีการเก็บคิว
            # ทำให้เมื่อ correction จบแล้ว ไม่มีใครไปสั่ง
            # action ที่ QR ต้องการต่อ กลายเป็นวนแก้ตำแหน่ง
            # (correction) ซ้ำไปเรื่อย ๆ โดย action จริงไม่เคย
            # ถูกส่งออกไปสักที
            #
            # ใหม่: เก็บ action ไว้ใน pending_action แทน
            # เมื่อ current_action ว่างลง (correction จบ)
            # ลูป update() ที่มีอยู่แล้วจะไปส่ง pending_action
            # ต่อให้อัตโนมัติ
            # --------------------------------------------------

            self.pending_action = action
            self.pending_source = source

            print()
            print("========================================")
            print("COMMAND QUEUED")
            print("========================================")

            print(
                "Action:",
                action
            )

            print(
                "Source:",
                source
            )

            print(
                "Waiting for current action to finish:",
                self.current_action
            )

            if is_qr_command:

                self._start_command_delay(
                    source
                )

            return

        # ======================================================
        # COMMAND ALREADY QUEUED
        # ======================================================

        if self.pending_action is not None:

            print()
            print(
                "COMMAND IGNORED:"
            )

            print(
                "Another command is already queued."
            )

            print(
                "Queued action:",
                self.pending_action
            )

            print(
                "Queued source:",
                self.pending_source
            )

            if self.is_command_countdown_active():

                print(
                    f"Remaining:"
                    f" {self.get_command_countdown():.1f}s"
                )

            return

        # ======================================================
        # QUEUE COMMAND
        # ======================================================

        self.pending_action = action
        self.pending_source = source

        print()
        print("========================================")
        print("COMMAND RECEIVED")
        print("========================================")

        print(
            "Action:",
            action
        )

        print(
            "Source:",
            source
        )

        if is_qr_command:

            self._start_command_delay(
                source
            )

        else:

            print(
                "Manual command: "
                "NO COUNTDOWN / NO BEEP"
            )

    # ==========================================================
    # QUEUE ACTION
    # ==========================================================

    def _queue_action(
        self,
        action,
        source,
        reason=""
    ):

        if self.is_command_countdown_active():

            print()
            print(
                "COMMAND QUEUE IGNORED:"
            )

            print(
                "QR countdown is active."
            )

            return

        if (
            self._is_qr_source(source)
            and
            self.is_qr_cooldown_active()
        ):

            print()
            print(
                "QR COMMAND QUEUE IGNORED:"
            )

            print(
                "QR cooldown is active."
            )

            return

        old_action = self.pending_action
        old_source = self.pending_source

        self.pending_action = action
        self.pending_source = source

        if not self._is_qr_source(source):

            self._clear_command_delay()

        print()
        print("========================================")
        print("COMMAND QUEUED")
        print("========================================")

        print(
            "New:",
            action,
            f"({source})"
        )

        if reason:

            print(
                "Reason:",
                reason
            )

        if (
            old_action is not None
            and
            old_action != action
        ):

            print(
                "Replaced:",
                old_action
            )

            print(
                "Previous source:",
                old_source
            )

    # ==========================================================
    # SUBMIT ACTION
    # ==========================================================

    def _submit_action(
        self,
        action,
        source="MANUAL"
    ):

        accepted = False

        # ======================================================
        # TAKEOFF
        # ======================================================

        if action in (
            "take_off",
            "manual_take_off"
        ):

            if self.flight_state in (
                "TAKING_OFF",
                "FLYING"
            ):

                print(
                    "TAKEOFF not submitted: "
                    f"flight state = {self.flight_state}"
                )

                self.pending_takeoff = False

                return

            if self.flight_state == "LANDING":

                self.pending_takeoff = True
                self.pending_action = action
                self.pending_source = source

                return

            if time.monotonic() < self.takeoff_ready_at:

                self.pending_takeoff = True
                self.pending_action = action
                self.pending_source = source

                return

            self.flight_state = "TAKING_OFF"

            accepted = self.bridge.submit(
                "take_off"
            )

            if not accepted:

                self.flight_state = "LANDED"
                self.pending_takeoff = False

                print(
                    "TAKEOFF could not be submitted."
                )

                return

        # ======================================================
        # LANDING
        # ======================================================

        elif action in (
            "landing",
            "manual_landing"
        ):

            if self.flight_state in (
                "LANDED",
                "LANDING"
            ):

                print(
                    "LANDING not submitted: "
                    "drone is already landed."
                )

                return

            self.flight_state = "LANDING"

            accepted = self.bridge.submit(
                "landing"
            )

            if not accepted:

                self.flight_state = "FLYING"

                print(
                    "LANDING could not be submitted."
                )

                return

        # ======================================================
        # FORWARD
        # ======================================================

        elif action == "forward":

            distance, speed = self._resolve_distance_speed(
                source,
                self.config.FORWARD_DISTANCE,
                self.config.FORWARD_SPEED
            )

            accepted = self.bridge.submit(
                "forward",
                distance=distance,
                speed=speed
            )

        # ======================================================
        # BACKWARD
        # ======================================================

        elif action == "backward":

            distance, speed = self._resolve_distance_speed(
                source,
                self.config.BACKWARD_DISTANCE,
                self.config.BACKWARD_SPEED
            )

            accepted = self.bridge.submit(
                "backward",
                distance=distance,
                speed=speed
            )

        # ======================================================
        # LEFT
        # ======================================================

        elif action == "left":

            distance, speed = self._resolve_distance_speed(
                source,
                self.config.LEFT_DISTANCE,
                self.config.LEFT_SPEED
            )

            accepted = self.bridge.submit(
                "left",
                distance=distance,
                speed=speed
            )

        # ======================================================
        # RIGHT
        # ======================================================

        elif action == "right":

            distance, speed = self._resolve_distance_speed(
                source,
                self.config.RIGHT_DISTANCE,
                self.config.RIGHT_SPEED
            )

            accepted = self.bridge.submit(
                "right",
                distance=distance,
                speed=speed
            )

        # ======================================================
        # MANUAL FORWARD
        # ======================================================

        elif action == "manual_forward":

            accepted = self.bridge.submit(
                "forward",
                distance=self.config.MANUAL_MOVE_DISTANCE,
                speed=self.config.MANUAL_MOVE_SPEED
            )

        # ======================================================
        # MANUAL BACKWARD
        # ======================================================

        elif action == "manual_backward":

            accepted = self.bridge.submit(
                "backward",
                distance=self.config.MANUAL_MOVE_DISTANCE,
                speed=self.config.MANUAL_MOVE_SPEED
            )

        # ======================================================
        # MANUAL LEFT
        # ======================================================

        elif action == "manual_left":

            accepted = self.bridge.submit(
                "left",
                distance=self.config.MANUAL_MOVE_DISTANCE,
                speed=self.config.MANUAL_MOVE_SPEED
            )

        # ======================================================
        # MANUAL RIGHT
        # ======================================================

        elif action == "manual_right":

            accepted = self.bridge.submit(
                "right",
                distance=self.config.MANUAL_MOVE_DISTANCE,
                speed=self.config.MANUAL_MOVE_SPEED
            )

        # ======================================================
        # ROTATE LEFT
        # ======================================================

        elif action == "manual_rotate_left":

            accepted = self.bridge.submit(
                "rotate_left",
                angle=self.config.MANUAL_ROTATE_ANGLE
            )

        # ======================================================
        # ROTATE RIGHT
        # ======================================================

        elif action == "manual_rotate_right":

            accepted = self.bridge.submit(
                "rotate_right",
                angle=self.config.MANUAL_ROTATE_ANGLE
            )

        # ======================================================
        # UP
        # ======================================================

        elif action == "manual_up":

            accepted = self.bridge.submit(
                "up",
                distance=self.config.MANUAL_VERTICAL_DISTANCE,
                speed=self.config.MANUAL_VERTICAL_SPEED
            )

        # ======================================================
        # DOWN
        # ======================================================

        elif action == "manual_down":

            accepted = self.bridge.submit(
                "down",
                distance=self.config.MANUAL_VERTICAL_DISTANCE,
                speed=self.config.MANUAL_VERTICAL_SPEED
            )

        # ======================================================
        # UNKNOWN
        # ======================================================

        else:

            print(
                "Unknown action:",
                action
            )

            return

        # ======================================================
        # SUBMIT FAILED
        # ======================================================

        if not accepted:

            print(
                "Action could not be submitted:",
                action
            )

            if action in (
                "take_off",
                "manual_take_off"
            ):

                self.flight_state = "LANDED"
                self.pending_takeoff = False

            return

        # ======================================================
        # CURRENT COMMAND
        # ======================================================

        self.current_action = action
        self.current_source = source

        print()
        print(
            "ACTION SUBMITTED:",
            action
        )

        print(
            "SOURCE:",
            source
        )

    # ==========================================================
    # FINISH CURRENT ACTION
    # ==========================================================

    def _finish_current_action(self):

        action = self.current_action
        source = self.current_source

        result = self.bridge.get_last_result()

        # ======================================================
        # AUTO CORRECTION
        # ======================================================

        if source == "AUTO CORRECTION":

            if result:

                print(
                    "Correction completed:",
                    action
                )

            else:

                print(
                    "Correction failed:",
                    action
                )

            self.current_action = None
            self.current_source = None

            return

        # ======================================================
        # TAKEOFF
        # ======================================================

        if action in (
            "take_off",
            "manual_take_off"
        ):

            if result:

                self.flight_state = "FLYING"

                print(
                    "Flight state: FLYING"
                )

            else:

                self.flight_state = "LANDED"
                self.pending_takeoff = False

                print(
                    "TAKEOFF failed"
                )

        # ======================================================
        # LANDING
        # ======================================================

        elif action in (
            "landing",
            "manual_landing"
        ):

            if result:

                self.flight_state = "LANDED"

                settle_time = float(
                    getattr(
                        self.config,
                        "LANDING_SETTLE_TIME",
                        5.0
                    )
                )

                self.takeoff_ready_at = (
                    time.monotonic()
                    + settle_time
                )

                print(
                    "Flight state: LANDED"
                )

                print(
                    f"Takeoff locked for "
                    f"{settle_time:.1f}s"
                )

            else:

                self.flight_state = "FLYING"
                self.pending_takeoff = False

                if self.pending_action in (
                    "take_off",
                    "manual_take_off"
                ):

                    self.pending_action = None
                    self.pending_source = None

                print(
                    "LANDING failed."
                )

        # ======================================================
        # QR / MOVEMENT ACTION
        # ======================================================

        else:

            if result:

                if (
                    self.mode == "AUTO"
                    and source is not None
                    and str(source).startswith("QR ")
                ):

                    print(
                        "Mission action completed:",
                        action
                    )

                    if self.correction_active:

                        self._set_mission_state(
                            "CORRECTING"
                        )

                    elif self.qr_inside:

                        self._set_mission_state(
                            "QR_LOCKED"
                        )

                    else:

                        self._set_mission_state(
                            "SEARCHING_QR"
                        )

            else:

                print(
                    "Action failed:",
                    action
                )

                if self.mode == "AUTO":

                    self.correction_active = False

                    self._set_mission_state(
                        "SEARCHING_QR"
                    )

        # ======================================================
        # CLEAR CURRENT
        # ======================================================

        self.current_action = None
        self.current_source = None

    # ==========================================================
    # RESET FLIGHT STATE
    # ==========================================================

    def reset_state(
        self,
        flight_state="LANDED"
    ):

        flight_state = str(
            flight_state
        ).upper()

        if flight_state not in (
            "FLYING",
            "LANDED"
        ):

            print(
                "Invalid reset flight state:",
                flight_state
            )

            return False

        print()
        print("========================================")
        print("RESET FLIGHT STATE")
        print("========================================")

        print(
            "Selected physical state:",
            flight_state
        )

        self.pending_action = None
        self.pending_source = None
        self.pending_takeoff = False

        self.current_action = None
        self.current_source = None

        self.takeoff_ready_at = 0.0

        self._clear_command_delay()
        self._clear_qr_cooldown()

        self.flight_state = flight_state

        self._reset_focus_state()

        if self.mode == "AUTO":

            self.mission_state = (
                "SEARCHING_QR"
            )

        else:

            self.mission_state = (
                "WAITING"
            )

        print(
            "Flight state reset to:",
            self.flight_state
        )

        print(
            "Command queue cleared"
        )

        print(
            "TAKEOFF lock cleared"
        )

        print(
            "Command countdown cleared"
        )

        print(
            "QR cooldown cleared"
        )

        print(
            "Mission state:",
            self.mission_state
        )

        print(
            "WARNING: Use RESET only when "
            "the selected state matches the "
            "drone's actual physical condition."
        )

        return True

    # ==========================================================
    # MANUAL
    # ==========================================================

    def manual_forward(self):

        self._request_action(
            "manual_forward",
            "MANUAL FORWARD"
        )

    def manual_backward(self):

        self._request_action(
            "manual_backward",
            "MANUAL BACKWARD"
        )

    def manual_left(self):

        self._request_action(
            "manual_left",
            "MANUAL LEFT"
        )

    def manual_right(self):

        self._request_action(
            "manual_right",
            "MANUAL RIGHT"
        )

    def manual_rotate_left(self):

        self._request_action(
            "manual_rotate_left",
            "MANUAL ROTATE LEFT"
        )

    def manual_rotate_right(self):

        self._request_action(
            "manual_rotate_right",
            "MANUAL ROTATE RIGHT"
        )

    def manual_up(self):

        self._request_action(
            "manual_up",
            "MANUAL UP"
        )

    def manual_down(self):

        self._request_action(
            "manual_down",
            "MANUAL DOWN"
        )

    def manual_take_off(self):

        self._request_action(
            "manual_take_off",
            "MANUAL TAKE OFF"
        )

    def manual_landing(self):

        self._request_action(
            "manual_landing",
            "MANUAL LANDING"
        )

    # ==========================================================
    # STOP
    # ==========================================================

    def stop(self):

        print()
        print(
            "Stopping Mission Controller..."
        )

        self.running = False

        self.pending_action = None
        self.pending_source = None
        self.pending_takeoff = False

        self.current_action = None
        self.current_source = None

        self._clear_command_delay()
        self._clear_qr_cooldown()
        self._reset_focus_state()

        print(
            "Mission Controller stopped"
        )