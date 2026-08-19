import cv2
import time

import config

from core.bridge.hula_bridge import HulaBridge
from core.camera.camera import Camera
from core.tracking.qr_tracking import QRTracker
from core.mission.mission_controller import MissionController


def main():

    print()
    print("========================================")
    print("          PAYLOAD CARRIER")
    print("========================================")

    bridge = None
    camera = None
    tracker = None
    mission = None

    # ==================================================
    # RESET CONFIRMATION
    # ==================================================

    reset_confirm = False

    # ==================================================
    # FRAME INFO
    # ==================================================

    frame_info_printed = False

    try:

        # ==================================================
        # BRIDGE
        # ==================================================

        print()
        print("[1] Connecting Hula...")

        bridge = HulaBridge()

        if not bridge.connect():

            print(
                "Hula connection failed"
            )

            return

        print(
            "[OK] Hula connected"
        )

        # ==================================================
        # CAMERA
        # ==================================================

        print()
        print("[2] Starting camera...")

        camera = Camera()

        if not camera.connect(
            bridge
        ):

            print(
                "Camera connect failed"
            )

            return

        if not camera.start():

            print(
                "Camera start failed"
            )

            return

        print(
            "[OK] Camera started"
        )

        # ==================================================
        # QR TRACKER
        # ==================================================

        tracker = QRTracker(
            config
        )

        # ==================================================
        # MISSION
        # ==================================================

        mission = MissionController(
            bridge,
            config
        )

        mission.start()

        # ==================================================
        # SYSTEM READY
        # ==================================================

        print()
        print("========================================")
        print("SYSTEM READY")
        print("========================================")

        print()

        print(
            "Mode:",
            mission.get_mode()
        )

        print()

        print("QR actions:")

        for qr_id, action in (
            config.QR_ACTIONS.items()
        ):

            print(
                f"  {qr_id} -> {action}"
            )

        print()

        print("MANUAL CONTROL")

        print(
            "  M           = Toggle Manual / Auto"
        )

        print(
            "  T           = Take Off"
        )

        print(
            "  L           = Landing"
        )

        print(
            "  Arrow Up    = Forward"
        )

        print(
            "  Arrow Down  = Backward"
        )

        print(
            "  Arrow Left  = Fly Left"
        )

        print(
            "  Arrow Right = Fly Right"
        )

        print(
            "  A           = Rotate Left"
        )

        print(
            "  D           = Rotate Right"
        )

        print(
            "  W           = Up"
        )

        print(
            "  S           = Down"
        )

        print(
            "  R           = Reset Flight State"
        )

        print(
            "  Q           = Quit"
        )

        print()

        # ==================================================
        # MAIN LOOP
        # ==================================================

        while True:

            # ==================================================
            # FRAME
            # ==================================================

            frame = camera.get_frame()

            if frame is not None:

                # ==================================================
                # FRAME SIZE INFO
                # ==================================================

                if not frame_info_printed:

                    frame_height = frame.shape[0]
                    frame_width = frame.shape[1]

                    center_x = (
                        frame_width / 2.0
                    )

                    center_y = (
                        frame_height / 2.0
                    )

                    print()
                    print("========================================")
                    print("CAMERA FRAME")
                    print("========================================")

                    print(
                        f"Resolution: "
                        f"{frame_width} x {frame_height}"
                    )

                    print(
                        f"Frame center: "
                        f"({center_x:.1f}, {center_y:.1f})"
                    )

                    print(
                        "========================================"
                    )

                    frame_info_printed = True

                # ==================================================
                # QR TRACKER
                # ==================================================

                state = tracker.update(
                    frame
                )

                # ==================================================
                # DEBUG
                # ==================================================

                if config.SHOW_DEBUG:

                    debug_frame = (
                        tracker.draw_debug(
                            frame,
                            state
                        )
                    )

                    cv2.imshow(
                        config.WINDOW_NAME,
                        debug_frame
                    )

                # ==================================================
                # QR
                # ==================================================

                if state["detected"]:

                    mission.handle_qr(
                        state["data"],
                        state["center_x"],
                        state["center_y"]
                    )

            # ==================================================
            # PROCESS MISSION
            # ==================================================

            mission.update()

            # ==================================================
            # KEYBOARD
            # ==================================================

            key = cv2.waitKeyEx(1)

            # ==================================================
            # RESET CONFIRMATION MODE
            # ==================================================

            if reset_confirm:

                # ------------------------------------------
                # ENTER = CONFIRM
                # ------------------------------------------

                if key in (
                    10,
                    13
                ):

                    print()
                    print("========================================")
                    print("RESET CONFIRMED")
                    print("========================================")

                    mission.reset_state()

                    reset_confirm = False

                # ------------------------------------------
                # Q = CANCEL
                # ------------------------------------------

                elif key in (
                    ord("q"),
                    ord("Q")
                ):

                    print()
                    print(
                        "Reset cancelled"
                    )

                    reset_confirm = False

                time.sleep(
                    0.01
                )

                continue

            # ==================================================
            # Q = QUIT
            # ==================================================

            if key in (
                ord("q"),
                ord("Q")
            ):

                print()
                print(
                    "Q pressed"
                )

                break

            # ==================================================
            # M = TOGGLE MODE
            # ==================================================

            elif key in (
                ord("m"),
                ord("M")
            ):

                print()
                print("========================================")
                print("TOGGLE MODE")
                print("========================================")

                mission.toggle_mode()

                print(
                    "Current mode:",
                    mission.get_mode()
                )

                print(
                    "Mission state:",
                    mission.get_mission_state()
                )

            # ==================================================
            # R = RESET REQUEST
            # ==================================================

            elif key in (
                ord("r"),
                ord("R")
            ):

                print()
                print("========================================")
                print("RESET FLIGHT STATE?")
                print("========================================")

                print(
                    "Press ENTER to confirm"
                )

                print(
                    "Press Q to cancel"
                )

                reset_confirm = True

            # ==================================================
            # W = UP
            # ==================================================

            elif key in (
                ord("w"),
                ord("W")
            ):

                print(
                    "MANUAL: UP"
                )

                mission.manual_up()

            # ==================================================
            # S = DOWN
            # ==================================================

            elif key in (
                ord("s"),
                ord("S")
            ):

                print(
                    "MANUAL: DOWN"
                )

                mission.manual_down()

            # ==================================================
            # A = ROTATE LEFT
            # ==================================================

            elif key in (
                ord("a"),
                ord("A")
            ):

                print(
                    "MANUAL: ROTATE LEFT"
                )

                mission.manual_rotate_left()

            # ==================================================
            # D = ROTATE RIGHT
            # ==================================================

            elif key in (
                ord("d"),
                ord("D")
            ):

                print(
                    "MANUAL: ROTATE RIGHT"
                )

                mission.manual_rotate_right()

            # ==================================================
            # T = TAKE OFF
            # ==================================================

            elif key in (
                ord("t"),
                ord("T")
            ):

                print(
                    "MANUAL: TAKE OFF"
                )

                mission.manual_take_off()

            # ==================================================
            # L = LANDING
            # ==================================================

            elif key in (
                ord("l"),
                ord("L")
            ):

                print(
                    "MANUAL: LANDING"
                )

                mission.manual_landing()

            # ==================================================
            # ARROW UP
            # ==================================================

            elif key == 2490368:

                print(
                    "MANUAL: FORWARD"
                )

                mission.manual_forward()

            # ==================================================
            # ARROW DOWN
            # ==================================================

            elif key == 2621440:

                print(
                    "MANUAL: BACKWARD"
                )

                mission.manual_backward()

            # ==================================================
            # ARROW LEFT
            # ==================================================

            elif key == 2424832:

                print(
                    "MANUAL: LEFT"
                )

                mission.manual_left()

            # ==================================================
            # ARROW RIGHT
            # ==================================================

            elif key == 2555904:

                print(
                    "MANUAL: RIGHT"
                )

                mission.manual_right()

            time.sleep(
                0.01
            )

    except KeyboardInterrupt:

        print()
        print(
            "Ctrl+C detected"
        )

    except Exception as e:

        print()
        print(
            "MAIN ERROR:"
        )

        print(
            e
        )

    finally:

        print()
        print("========================================")
        print("SHUTDOWN")
        print("========================================")

        # ==================================================
        # STOP MISSION
        # ==================================================

        print(
            "[SHUTDOWN 1] Stopping Mission"
        )

        if mission is not None:

            try:

                mission.stop()

            except Exception as e:

                print(
                    "Mission stop error:",
                    e
                )

        print(
            "[SHUTDOWN 2] Mission stopped"
        )

        # ==================================================
        # STOP CAMERA
        # ==================================================

        print(
            "[SHUTDOWN 3] Stopping Camera"
        )

        if camera is not None:

            try:

                camera.stop()

            except Exception as e:

                print(
                    "Camera stop error:",
                    e
                )

        print(
            "[SHUTDOWN 4] Camera stopped"
        )

        # ==================================================
        # STOP HULA
        # ==================================================

        print(
            "[SHUTDOWN 5] Stopping Hula"
        )

        if bridge is not None:

            try:

                bridge.stop()

            except Exception as e:

                print(
                    "Hula stop error:",
                    e
                )

        print(
            "[SHUTDOWN 6] Hula stopped"
        )

        # ==================================================
        # OPENCV
        # ==================================================

        print(
            "[SHUTDOWN 7] Skip OpenCV destroy"
        )

        print()
        print(
            "[SHUTDOWN 8] Program finishing"
        )


if __name__ == "__main__":

    main()