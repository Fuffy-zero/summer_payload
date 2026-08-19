import time


class CameraController:

    # ==========================================================
    # INIT
    # ==========================================================

    def __init__(
        self,
        bridge,
        config
    ):

        self.bridge = bridge

        self.config = config

        self.current_mode = "MANUAL"

        # ------------------------------------------------------
        # มุมที่ระบบคิดว่ากล้องอยู่
        #
        # + = UP
        # 0 = CENTER
        # - = DOWN
        # ------------------------------------------------------

        self.current_angle = None

        self.moving = False

    # ==========================================================
    # CONFIG
    # ==========================================================

    def _get_auto_angle(self):

        return int(
            getattr(
                self.config,
                "CAMERA_AUTO_ANGLE",
                -90
            )
        )

    def _get_manual_angle(self):

        return int(
            getattr(
                self.config,
                "CAMERA_MANUAL_ANGLE",
                0
            )
        )

    def _get_mode_change_delay(self):

        return float(
            getattr(
                self.config,
                "CAMERA_MODE_CHANGE_DELAY",
                5.0
            )
        )

    # ==========================================================
    # SET MODE
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
                "Unknown camera mode:",
                mode
            )

            return False

        # ------------------------------------------------------
        # SAME MODE
        #
        # ถ้า mode ตรงกันแต่ยังไม่มี angle
        # ต้อง sync กล้องจริงก่อน
        # ------------------------------------------------------

        if (
            self.current_mode == mode
            and
            self.current_angle is not None
        ):

            print(
                "Camera already in:",
                mode
            )

            return True

        # ------------------------------------------------------
        # BLOCK DURING TRANSITION
        # ------------------------------------------------------

        if self.moving:

            print(
                "Camera transition still running."
            )

            return False

        # ------------------------------------------------------
        # TARGET
        # ------------------------------------------------------

        if mode == "AUTO":

            print()
            print(
                "Switching camera to AUTO..."
            )

            target_angle = (
                self._get_auto_angle()
            )

        else:

            print()
            print(
                "Switching camera to MANUAL..."
            )

            target_angle = (
                self._get_manual_angle()
            )

        # ------------------------------------------------------
        # SEND ABSOLUTE ANGLE
        # ------------------------------------------------------

        accepted = self._set_angle(
            target_angle
        )

        if not accepted:

            print(
                "Camera mode change rejected."
            )

            return False

        self.moving = True

        # ------------------------------------------------------
        # WAIT FOR HULA COMMAND
        # ------------------------------------------------------

        if not self._wait_for_command():

            self.moving = False

            print(
                "Camera command did not finish."
            )

            return False

        # ------------------------------------------------------
        # WAIT AFTER CAMERA MOVEMENT
        # ------------------------------------------------------

        delay = (
            self._get_mode_change_delay()
        )

        print()
        print(
            f"Waiting "
            f"{delay:.1f}s "
            f"for camera stabilization..."
        )

        time.sleep(
            delay
        )

        # ------------------------------------------------------
        # FINALIZE
        # ------------------------------------------------------

        self.current_mode = mode

        self.moving = False

        print()
        print(
            "========================================"
        )

        print(
            "CAMERA MODE READY"
        )

        print(
            "========================================"
        )

        print(
            "Mode:",
            self.current_mode
        )

        print(
            "Angle:",
            self.current_angle
        )

        return True

    # ==========================================================
    # SET ABSOLUTE ANGLE
    #
    # + = UP
    # 0 = CENTER
    # - = DOWN
    #
    # Hula command:
    #
    # angle < 0
    #     -> DOWN abs(angle)
    #
    # angle >= 0
    #     -> UP angle
    #
    # สำคัญ:
    # ค่า value ที่ส่ง Hula เป็น "absolute position"
    # ไม่ใช่ delta จากมุมปัจจุบัน
    # ==========================================================

    def _set_angle(
        self,
        angle
    ):

        try:

            angle = int(
                round(
                    float(angle)
                )
            )

        except (
            TypeError,
            ValueError
        ):

            print(
                "Invalid camera angle:",
                angle
            )

            return False

        # ------------------------------------------------------
        # LIMIT
        # ------------------------------------------------------

        angle = max(
            -90,
            min(
                90,
                angle
            )
        )

        # ------------------------------------------------------
        # DOWN
        # ------------------------------------------------------

        if angle < 0:

            value = abs(
                angle
            )

            accepted = (
                self.bridge.set_camera_angle(
                    "down",
                    value
                )
            )

            if not accepted:

                print(
                    "Camera DOWN command rejected."
                )

                return False

            print(
                "Camera target:",
                angle
            )

            print(
                "Camera DOWN:",
                value
            )

        # ------------------------------------------------------
        # UP / CENTER
        # ------------------------------------------------------

        else:

            value = angle

            accepted = (
                self.bridge.set_camera_angle(
                    "up",
                    value
                )
            )

            if not accepted:

                print(
                    "Camera UP command rejected."
                )

                return False

            print(
                "Camera target:",
                angle
            )

            print(
                "Camera UP:",
                value
            )

        # ------------------------------------------------------
        # UPDATE INTERNAL STATE
        # ------------------------------------------------------

        self.current_angle = angle

        return True

    # ==========================================================
    # WAIT HULA COMMAND
    # ==========================================================

    def _wait_for_command(self):

        while True:

            if not self.bridge.is_busy():

                result = (
                    self.bridge.get_last_result()
                )

                if result:

                    print(
                        "Camera command completed."
                    )

                    return True

                print(
                    "Camera command failed."
                )

                return False

            time.sleep(
                0.05
            )

    # ==========================================================
    # MANUAL CAMERA CONTROL
    # ==========================================================

    def manual_angle(
        self,
        angle
    ):

        if self.current_mode != "MANUAL":

            print(
                "Manual camera control disabled "
                "in AUTO mode."
            )

            return False

        if self.moving:

            print(
                "Camera transition still running."
            )

            return False

        # ------------------------------------------------------
        # SEND ABSOLUTE ANGLE
        # ------------------------------------------------------

        accepted = self._set_angle(
            angle
        )

        if not accepted:

            return False

        self.moving = True

        # ------------------------------------------------------
        # WAIT
        # ------------------------------------------------------

        if not self._wait_for_command():

            self.moving = False

            return False

        self.moving = False

        return True

    # ==========================================================
    # STATUS
    # ==========================================================

    def get_mode(self):

        return self.current_mode

    def get_angle(self):

        return self.current_angle

    def is_moving(self):

        return self.moving