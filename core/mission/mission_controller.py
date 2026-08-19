import time


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

        if self.mode not in ("MANUAL", "AUTO"):

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

        # QR รอบ Focus ปัจจุบันถูก Trigger แล้วหรือยัง
        #
        # False = ยังไม่ Trigger
        # True  = Trigger ไปแล้ว
        #
        # เมื่อ QR ออกจาก Focus:
        #     False
        #
        # เมื่อ QR กลับเข้า Focus:
        #     Trigger ใหม่ได้ 1 ครั้ง
        #
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

        if self.mode == "AUTO":

            self.mission_state = "SEARCHING_QR"

        else:

            self.mission_state = "WAITING"

        print()
        print("========================================")
        print("MISSION CONTROLLER STARTED")
        print("========================================")

        print(
            "Mode:",
            self.mode
        )

        print(
            "Mission state:",
            self.mission_state
        )

    # ==========================================================
    # MODE CONTROL
    # ==========================================================

    def set_mode(
        self,
        mode
    ):

        mode = str(
            mode
        ).upper()

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

        if mode == "AUTO":

            self._set_mission_state(
                "SEARCHING_QR"
            )

        else:

            self._set_mission_state(
                "WAITING"
            )

        print()
        print("========================================")
        print("MODE CHANGED")
        print("========================================")

        print(
            "Mode:",
            self.mode
        )

        print(
            "Mission state:",
            self.mission_state
        )

        return True

    # ==========================================================
    # TOGGLE MODE
    # ==========================================================

    def toggle_mode(self):

        if self.mode == "MANUAL":

            return self.set_mode(
                "AUTO"
            )

        return self.set_mode(
            "MANUAL"
        )

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
    # GET FOCUS POINT
    # ==========================================================

    def _get_focus_point(
        self,
        qr_id
    ):

        focus_points = getattr(
            self.config,
            "QR_FOCUS_POINTS",
            {}
        )

        if not isinstance(
            focus_points,
            dict
        ):

            return None

        point = focus_points.get(
            qr_id
        )

        if point is None:

            point = focus_points.get(
                str(qr_id)
            )

        if point is None:

            return None

        try:

            if isinstance(
                point,
                dict
            ):

                x = point["x"]
                y = point["y"]

            else:

                x = point[0]
                y = point[1]

            return (
                float(x),
                float(y)
            )

        except (
            KeyError,
            IndexError,
            TypeError,
            ValueError
        ):

            print(
                "Invalid QR focus point:",
                qr_id,
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
            or
            self.focus_y is None
        ):

            return None

        diff_x = (
            float(center_x)
            -
            self.focus_x
        )

        diff_y = (
            float(center_y)
            -
            self.focus_y
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
            distance <= tolerance
        )

    # ==========================================================
    # HANDLE QR
    # ==========================================================
    #
    # Known QR
    #     |
    #     +-- inside focus --> execute once
    #     |
    #     +-- outside focus
    #              |
    #              v
    #         correction target
    #              |
    #              v
    #          correction
    #              |
    #              v
    #         back to focus
    #              |
    #              v
    #         execute once again
    #
    # ANY recognized QR can become the current target.
    # ==========================================================

    def handle_qr(
        self,
        qr_id,
        center_x=None,
        center_y=None
    ):

        if not self.running:

            return

        # ======================================================
        # MANUAL MODE
        # ======================================================

        if self.mode != "AUTO":

            return

        # ======================================================
        # GET ACTION
        # ======================================================

        action = self.config.QR_ACTIONS.get(
            qr_id
        )

        if action is None:

            return

        # ======================================================
        # GET FOCUS POINT
        # ======================================================

        focus_point = self._get_focus_point(
            qr_id
        )

        if focus_point is None:

            print(
                f"QR {qr_id}: "
                "no focus point configured."
            )

            self._trigger_qr(
                qr_id,
                action
            )

            return

        # ======================================================
        # POSITION REQUIRED
        # ======================================================

        if (
            center_x is None
            or
            center_y is None
        ):

            self._set_mission_state(
                "SEARCHING_QR"
            )

            return

        # ======================================================
        # STORE POSITION
        # ======================================================

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

            # --------------------------------------------------
            # QR IS CURRENT CORRECTION TARGET
            # AND HAS JUST RETURNED
            # --------------------------------------------------

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

                # --------------------------------------------------
                # สำคัญ:
                #
                # กลับเข้า Focus = เริ่ม Focus entry รอบใหม่
                #
                # เปิดสิทธิ์ Trigger อีกครั้ง
                # --------------------------------------------------

                self.qr_triggered_this_entry = False

                self._trigger_qr(
                    qr_id,
                    action
                )

                return

            # --------------------------------------------------
            # NORMAL QR
            # --------------------------------------------------

            if self.focus_qr_id != qr_id:

                # QR ตัวใหม่
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

                # QR ตัวเดิม
                self.target_qr_id = qr_id
                self.target_action = action

                self.focus_x = focus_point[0]
                self.focus_y = focus_point[1]

            # --------------------------------------------------
            # ENTER FOCUS
            # --------------------------------------------------

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
                        round(
                            center_x,
                            1
                        ),
                        round(
                            center_y,
                            1
                        )
                    )
                )

            # --------------------------------------------------
            # TRIGGER ONLY ONCE THIS ENTRY
            # --------------------------------------------------

            if not self.qr_triggered_this_entry:

                self._trigger_qr(
                    qr_id,
                    action
                )

            return

        # ======================================================
        # QR OUTSIDE FOCUS
        # ======================================================

        # ------------------------------------------------------
        # CHECK TARGET CHANGE
        # ------------------------------------------------------

        target_changed = (
            self.focus_qr_id != qr_id
        )

        # ------------------------------------------------------
        # NEW TARGET QR
        # ------------------------------------------------------

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

        # ------------------------------------------------------
        # SAME TARGET STILL OUTSIDE
        # ------------------------------------------------------

        self.target_qr_id = qr_id
        self.target_action = action

        self.focus_x = focus_point[0]
        self.focus_y = focus_point[1]

        self.qr_inside = False
        self.focus_locked = False

        # ------------------------------------------------------
        # START CORRECTION
        # ------------------------------------------------------

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
            -
            float(focus_x)
        )

        diff_y = (
            float(center_y)
            -
            float(focus_y)
        )

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
            distance <= tolerance
        )

    # ==========================================================
    # TRIGGER QR
    # ==========================================================

    def _trigger_qr(
        self,
        qr_id,
        action
    ):

        # ======================================================
        # ALREADY TRIGGERED THIS FOCUS ENTRY
        # ======================================================

        if self.qr_triggered_this_entry:

            return

        # ======================================================
        # COOLDOWN
        # ======================================================

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
                -
                self.last_qr_time
            ) < cooldown
        ):

            return

        # ======================================================
        # MARK THIS ENTRY AS TRIGGERED
        # ======================================================

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
    # UPDATE
    # ==========================================================

    def update(self):

        if not self.running:

            return

        # ======================================================
        # CURRENT COMMAND FINISHED
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
        # PROCESS PENDING COMMAND
        # ======================================================

        if (
            self.current_action is None
            and
            self.pending_action is not None
        ):

            action = self.pending_action
            source = self.pending_source

            # --------------------------------------------------
            # TAKEOFF WAIT
            # --------------------------------------------------

            if action in (
                "take_off",
                "manual_take_off"
            ):

                now = time.monotonic()

                if now < self.takeoff_ready_at:

                    return

            # --------------------------------------------------
            # REMOVE QUEUE
            # --------------------------------------------------

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
            or
            self.last_center_y is None
            or
            self.focus_x is None
            or
            self.focus_y is None
        ):

            return None

        diff_x = (
            self.last_center_x
            -
            self.focus_x
        )

        diff_y = (
            self.last_center_y
            -
            self.focus_y
        )

        tolerance = (
            self._get_focus_tolerance()
        )

        # ======================================================
        # ALREADY INSIDE
        # ======================================================

        if (
            (
                diff_x ** 2
                +
                diff_y ** 2
            ) ** 0.5
            <= tolerance
        ):

            return None

        # ======================================================
        # X AXIS
        # ======================================================

        if abs(diff_x) >= abs(diff_y):

            if diff_x > tolerance:

                return "right"

            if diff_x < -tolerance:

                return "left"

        # ======================================================
        # Y AXIS
        # ======================================================

        else:

            if diff_y > tolerance:

                return "down"

            if diff_y < -tolerance:

                return "up"

        return None

    # ==========================================================
    # UPDATE CORRECTION
    # ==========================================================

    def _update_correction(self):

        if not self.correction_active:

            return

        # ======================================================
        # CURRENT COMMAND
        # ======================================================

        if self.current_action is not None:

            return

        # ======================================================
        # POSITION REQUIRED
        # ======================================================

        if (
            self.last_center_x is None
            or
            self.last_center_y is None
        ):

            return

        # ======================================================
        # CHECK FOCUS
        # ======================================================

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

            # ==================================================
            # กลับ Focus = รอบใหม่
            # ==================================================

            self.qr_triggered_this_entry = False

            if target_qr is not None:

                self._trigger_qr(
                    target_qr,
                    target_action
                )

            return

        # ======================================================
        # TIMEOUT
        # ======================================================

        if (
            time.monotonic()
            -
            self.correction_started_at
        ) >= self._get_correction_timeout():

            self.correction_active = False

            print(
                "Correction timeout."
            )

            self._set_mission_state(
                "SEARCHING_QR"
            )

            return

        # ======================================================
        # MAX COUNT
        # ======================================================

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

        # ======================================================
        # INTERVAL
        # ======================================================

        now = time.monotonic()

        if (
            self.last_correction_at > 0.0
            and
            (
                now
                -
                self.last_correction_at
            ) < self._get_correction_interval()
        ):

            return

        # ======================================================
        # CALCULATE
        # ======================================================

        action = (
            self._calculate_correction_action()
        )

        if action is None:

            return

        # ======================================================
        # SEND CORRECTION
        # ======================================================

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
            "up",
            "down"
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

            self._queue_action(
                action,
                source,
                reason="current command running"
            )

            return

        # ======================================================
        # EXECUTE
        # ======================================================

        self._submit_action(
            action,
            source
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

        old_action = self.pending_action

        self.pending_action = action
        self.pending_source = source

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

            accepted = self.bridge.submit(
                "forward",
                distance=self.config.FORWARD_DISTANCE,
                speed=self.config.FORWARD_SPEED
            )

        # ======================================================
        # BACKWARD
        # ======================================================

        elif action == "backward":

            accepted = self.bridge.submit(
                "backward",
                distance=self.config.BACKWARD_DISTANCE,
                speed=self.config.BACKWARD_SPEED
            )

        # ======================================================
        # LEFT
        # ======================================================

        elif action == "left":

            accepted = self.bridge.submit(
                "left",
                distance=self.config.LEFT_DISTANCE,
                speed=self.config.LEFT_SPEED
            )

        # ======================================================
        # RIGHT
        # ======================================================

        elif action == "right":

            accepted = self.bridge.submit(
                "right",
                distance=self.config.RIGHT_DISTANCE,
                speed=self.config.RIGHT_SPEED
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
                    +
                    settle_time
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
                    and
                    source is not None
                    and
                    str(source).startswith("QR ")
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

    def reset_state(self):

        print()
        print("========================================")
        print("RESET FLIGHT STATE")
        print("========================================")

        self.pending_action = None
        self.pending_source = None
        self.pending_takeoff = False

        self.current_action = None
        self.current_source = None

        self.takeoff_ready_at = 0.0

        self.flight_state = "LANDED"

        self._reset_focus_state()

        if self.mode == "AUTO":

            self.mission_state = "SEARCHING_QR"

        else:

            self.mission_state = "WAITING"

        print(
            "Flight state reset to LANDED"
        )

        print(
            "Command queue cleared"
        )

        print(
            "TAKEOFF lock cleared"
        )

        print(
            "Mission state:",
            self.mission_state
        )

        print(
            "WARNING: Use RESET only when "
            "the drone is physically landed."
        )

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

        self._reset_focus_state()

        print(
            "Mission Controller stopped"
        )