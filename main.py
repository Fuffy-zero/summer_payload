import time
import sys

import config

from PySide6.QtWidgets import QApplication

from core.bridge.hula_bridge import HulaBridge
from core.camera.camera import Camera
from core.camera.camera_controller import CameraController
from core.tracking.qr_tracking import QRTracker
from core.mission.mission_controller import MissionController
from core.ui.main_window import MainWindow


def main():

    print()
    print("========================================")
    print("          PAYLOAD CARRIER")
    print("========================================")

    bridge = None
    camera = None
    camera_controller = None
    tracker = None
    mission = None

    app = None
    window = None

    try:

        # ==================================================
        # QT APPLICATION
        # ==================================================

        app = QApplication.instance()

        if app is None:

            app = QApplication(
                sys.argv
            )

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
        # CAMERA CONTROLLER
        # ==================================================

        camera_controller = CameraController(
            bridge,
            config
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
        # UI
        # ==================================================

        window = MainWindow()

        window.show()

        app.processEvents()

        # ==================================================
        # SYNC CAMERA WITH START MODE
        # ==================================================

        print()
        print(
            "Setting camera to mission mode..."
        )

        if not camera_controller.set_mode(
            mission.get_mode()
        ):

            print(
                "Camera mode initialization failed"
            )

            return

        # ==================================================
        # UI CONTROL CALLBACKS
        # ==================================================

        def toggle_mode():

            print()
            print("========================================")
            print("TOGGLE MODE")
            print("========================================")

            current_mode = (
                mission.get_mode()
            )

            if current_mode == "MANUAL":

                target_mode = "AUTO"

            else:

                target_mode = "MANUAL"

            print(
                "Target mode:",
                target_mode
            )

            # --------------------------------------------------
            # CAMERA FIRST
            # --------------------------------------------------

            camera_result = (
                camera_controller.set_mode(
                    target_mode
                )
            )

            if not camera_result:

                print()
                print(
                    "Mode change cancelled."
                )

                print(
                    "Camera could not change mode."
                )

                return

            # --------------------------------------------------
            # MISSION MODE
            # --------------------------------------------------

            mission_result = (
                mission.set_mode(
                    target_mode
                )
            )

            if not mission_result:

                print()
                print(
                    "WARNING:"
                )

                print(
                    "Camera changed but mission mode "
                    "could not change."
                )

                return

            print()
            print("========================================")
            print("MODE CHANGE COMPLETE")
            print("========================================")

            print(
                "Mission mode:",
                mission.get_mode()
            )

            print(
                "Camera mode:",
                camera_controller.get_mode()
            )

            print(
                "Camera angle:",
                camera_controller.get_angle()
            )

            print(
                "Mission state:",
                mission.get_mission_state()
            )

        # ==================================================
        # TAKE OFF
        # ==================================================

        def takeoff():

            print(
                "UI: TAKE OFF"
            )

            mission.manual_take_off()

        # ==================================================
        # LANDING
        # ==================================================

        def landing():

            print(
                "UI: LANDING"
            )

            mission.manual_landing()

        # ==================================================
        # FORWARD
        # ==================================================

        def forward():

            print(
                "UI: FORWARD"
            )

            mission.manual_forward()

        # ==================================================
        # BACKWARD
        # ==================================================

        def backward():

            print(
                "UI: BACKWARD"
            )

            mission.manual_backward()

        # ==================================================
        # LEFT
        # ==================================================

        def left():

            print(
                "UI: LEFT"
            )

            mission.manual_left()

        # ==================================================
        # RIGHT
        # ==================================================

        def right():

            print(
                "UI: RIGHT"
            )

            mission.manual_right()

        # ==================================================
        # ROTATE LEFT
        # ==================================================

        def rotate_left():

            print(
                "UI: ROTATE LEFT"
            )

            mission.manual_rotate_left()

        # ==================================================
        # ROTATE RIGHT
        # ==================================================

        def rotate_right():

            print(
                "UI: ROTATE RIGHT"
            )

            mission.manual_rotate_right()

        # ==================================================
        # UP
        # ==================================================

        def up():

            print(
                "UI: UP"
            )

            mission.manual_up()

        # ==================================================
        # DOWN
        # ==================================================

        def down():

            print(
                "UI: DOWN"
            )

            mission.manual_down()

        # ==================================================
        # CAMERA DOWN
        # ==================================================

        def camera_down():

            if not mission.is_manual():

                print(
                    "Camera manual control disabled in AUTO mode."
                )

                return

            current_angle = (
                camera_controller.get_angle()
            )

            if current_angle is None:

                current_angle = (
                    config.CAMERA_MANUAL_ANGLE
                )

            step = int(
                getattr(
                    config,
                    "CAMERA_MANUAL_STEP",
                    5
                )
            )

            new_angle = (
                current_angle
                -
                step
            )

            print()
            print(
                "UI: CAMERA DOWN"
            )

            print(
                "Step:",
                step
            )

            print(
                "Angle:",
                new_angle
            )

            camera_controller.manual_angle(
                new_angle
            )

        # ==================================================
        # CAMERA UP
        # ==================================================

        def camera_up():

            if not mission.is_manual():

                print(
                    "Camera manual control disabled in AUTO mode."
                )

                return

            current_angle = (
                camera_controller.get_angle()
            )

            if current_angle is None:

                current_angle = (
                    config.CAMERA_MANUAL_ANGLE
                )

            step = int(
                getattr(
                    config,
                    "CAMERA_MANUAL_STEP",
                    5
                )
            )

            new_angle = (
                current_angle
                +
                step
            )

            print()
            print(
                "UI: CAMERA UP"
            )

            print(
                "Step:",
                step
            )

            print(
                "Angle:",
                new_angle
            )

            camera_controller.manual_angle(
                new_angle
            )

        # ==================================================
        # RESET
        # ==================================================

        def reset(flight_state=None):

            print()
            print(
                "UI: RESET"
            )

            if flight_state is None:

                print(
                    "RESET cancelled."
                )

                return

            print(
                "Selected flight state:",
                flight_state
            )

            mission.reset_state(
                flight_state
            )

        # ==================================================
        # QUIT
        # ==================================================

        def quit_program():

            print()
            print(
                "UI: QUIT"
            )

            window.close()

        # ==================================================
        # CONNECT BUTTONS
        # ==================================================

        window.set_control_callbacks(

            mode=toggle_mode,

            takeoff=takeoff,
            landing=landing,

            forward=forward,
            backward=backward,

            left=left,
            right=right,

            rotate_left=rotate_left,
            rotate_right=rotate_right,

            up=up,
            down=down,

            camera_down=camera_down,
            camera_up=camera_up,

            reset=reset,

            quit=quit_program

        )

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

        print(
            "Camera mode:",
            camera_controller.get_mode()
        )

        print(
            "Camera angle:",
            camera_controller.get_angle()
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

        print(
            "UI CONTROL READY"
        )

        print()

        # ==================================================
        # FRAME INFO
        # ==================================================

        frame_info_printed = False

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
                # LIVE VIDEO
                # ==================================================

                live_frame = frame.copy()

                # ==================================================
                # DEBUG VIDEO
                # ==================================================

                if config.SHOW_DEBUG:

                    debug_frame = (
                        tracker.draw_debug(
                            frame.copy(),
                            state
                        )
                    )

                else:

                    debug_frame = frame.copy()

                # ==================================================
                # UI VIDEO
                # ==================================================

                window.update_video(
                    live_frame,
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
            # UPDATE UI STATUS
            # ==================================================

            window.update_status(
                mission,
                camera_controller,
                bridge
            )

            # ==================================================
            # PROCESS UI
            # ==================================================

            app.processEvents()

            if window.closed:

                print()
                print(
                    "UI window closed"
                )

                break

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
            repr(e)
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
        # UI
        # ==================================================

        if window is not None:

            try:

                window.close()

            except Exception:

                pass

        print(
            "[SHUTDOWN 7] UI closed"
        )

        print()
        print(
            "[SHUTDOWN 8] Program finishing"
        )


if __name__ == "__main__":

    main()