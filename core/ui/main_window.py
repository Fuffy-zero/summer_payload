import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QImage,
    QPixmap,
    QKeySequence,
    QShortcut,
)
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "Payload Carrier"
        )

        # ======================================================
        # WINDOW
        # ======================================================

        self.resize(
            1280,
            720
        )

        self.setMinimumSize(
            1000,
            600
        )

        self.closed = False

        # ======================================================
        # CALLBACKS
        # ======================================================

        self._callbacks = {}

        # Keep QShortcut objects alive
        self._shortcuts = []

        self._build_ui()

    # ==========================================================
    # BUILD UI
    # ==========================================================

    def _build_ui(self):

        central = QWidget()

        self.setCentralWidget(
            central
        )

        main_layout = QGridLayout(
            central
        )

        main_layout.setContentsMargins(
            10,
            8,
            10,
            8
        )

        main_layout.setSpacing(
            8
        )

        # ======================================================
        # TITLE
        # ======================================================

        title = QLabel(
            "PAYLOAD CARRIER"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setObjectName(
            "title"
        )

        main_layout.addWidget(
            title,
            0,
            0,
            1,
            3
        )

        # ======================================================
        # VIDEO AREA
        # ======================================================

        video_container = QFrame()

        video_container.setObjectName(
            "videoContainer"
        )

        video_layout = QHBoxLayout(
            video_container
        )

        video_layout.setContentsMargins(
            6,
            6,
            6,
            6
        )

        video_layout.setSpacing(
            6
        )

        # ------------------------------------------------------
        # LIVE VIDEO
        # ------------------------------------------------------

        self.live_video = QLabel(
            "LIVE VIDEO"
        )

        self.live_video.setAlignment(
            Qt.AlignCenter
        )

        self.live_video.setObjectName(
            "video"
        )

        self.live_video.setMinimumSize(
            300,
            200
        )

        # ------------------------------------------------------
        # DEBUG VIDEO
        # ------------------------------------------------------

        self.debug_video = QLabel(
            "DEBUG VIDEO"
        )

        self.debug_video.setAlignment(
            Qt.AlignCenter
        )

        self.debug_video.setObjectName(
            "video"
        )

        self.debug_video.setMinimumSize(
            300,
            200
        )

        video_layout.addWidget(
            self.live_video,
            1
        )

        video_layout.addWidget(
            self.debug_video,
            1
        )

        main_layout.addWidget(
            video_container,
            1,
            0,
            1,
            3
        )

        # ======================================================
        # SYSTEM
        # ======================================================

        system_frame = self._create_panel(
            "SYSTEM"
        )

        system_layout = (
            system_frame.layout()
        )

        self.mode_label = QLabel(
            "Mode: MANUAL"
        )

        self.flight_label = QLabel(
            "Flight: LANDED"
        )

        self.camera_label = QLabel(
            "Camera: 0°"
        )

        self.mission_label = QLabel(
            "Mission: WAITING"
        )

        system_layout.addWidget(
            self.mode_label
        )

        system_layout.addWidget(
            self.flight_label
        )

        system_layout.addWidget(
            self.camera_label
        )

        system_layout.addWidget(
            self.mission_label
        )

        # ======================================================
        # QR / FOCUS
        # ======================================================

        qr_frame = self._create_panel(
            "QR / FOCUS"
        )

        qr_layout = (
            qr_frame.layout()
        )

        self.target_label = QLabel(
            "Target: -"
        )

        self.action_label = QLabel(
            "Action: -"
        )

        self.position_label = QLabel(
            "Position: -"
        )

        self.focus_label = QLabel(
            "Focus: -"
        )

        qr_layout.addWidget(
            self.target_label
        )

        qr_layout.addWidget(
            self.action_label
        )

        qr_layout.addWidget(
            self.position_label
        )

        qr_layout.addWidget(
            self.focus_label
        )

        # ======================================================
        # CORRECTION
        # ======================================================

        correction_frame = self._create_panel(
            "CORRECTION"
        )

        correction_layout = (
            correction_frame.layout()
        )

        self.direction_label = QLabel(
            "Direction: -"
        )

        self.distance_label = QLabel(
            "Distance: -"
        )

        self.speed_label = QLabel(
            "Speed: -"
        )

        self.status_label = QLabel(
            "Status: READY"
        )

        correction_layout.addWidget(
            self.direction_label
        )

        correction_layout.addWidget(
            self.distance_label
        )

        correction_layout.addWidget(
            self.speed_label
        )

        correction_layout.addWidget(
            self.status_label
        )

        # ======================================================
        # ADD INFO PANELS
        # ======================================================

        main_layout.addWidget(
            system_frame,
            2,
            0
        )

        main_layout.addWidget(
            qr_frame,
            2,
            1
        )

        main_layout.addWidget(
            correction_frame,
            2,
            2
        )

        # ======================================================
        # CONTROL
        # ======================================================

        control_frame = QFrame()

        control_frame.setObjectName(
            "controlFrame"
        )

        control_layout = QVBoxLayout(
            control_frame
        )

        control_layout.setContentsMargins(
            8,
            6,
            8,
            6
        )

        control_layout.setSpacing(
            5
        )

        # ------------------------------------------------------
        # CONTROL TITLE
        # ------------------------------------------------------

        control_title = QLabel(
            "CONTROL"
        )

        control_title.setObjectName(
            "sectionTitle"
        )

        control_layout.addWidget(
            control_title
        )

        # ======================================================
        # CREATE BUTTONS
        # ======================================================

        # ------------------------------------------------------
        # MODE
        # ------------------------------------------------------

        self.mode_button = QPushButton(
            "M  AUTO"
        )

        # ------------------------------------------------------
        # FLIGHT
        # ------------------------------------------------------

        self.takeoff_button = QPushButton(
            "T  TAKE OFF"
        )

        self.landing_button = QPushButton(
            "L  LAND"
        )

        # ------------------------------------------------------
        # MOVEMENT
        # ------------------------------------------------------

        self.left_button = QPushButton(
            "←"
        )

        self.forward_button = QPushButton(
            "↑"
        )

        self.backward_button = QPushButton(
            "↓"
        )

        self.right_button = QPushButton(
            "→"
        )

        # ------------------------------------------------------
        # ROTATION
        # ------------------------------------------------------

        self.rotate_left_button = QPushButton(
            "A  ROTATE LEFT"
        )

        self.rotate_right_button = QPushButton(
            "D  ROTATE RIGHT"
        )

        # ------------------------------------------------------
        # VERTICAL
        # ------------------------------------------------------

        self.up_button = QPushButton(
            "W  UP"
        )

        self.down_button = QPushButton(
            "S  DOWN"
        )

        # ------------------------------------------------------
        # CAMERA
        # ------------------------------------------------------

        self.camera_down_button = QPushButton(
            "[  CAM DOWN"
        )

        self.camera_up_button = QPushButton(
            "CAM UP  ]"
        )

        # ------------------------------------------------------
        # RESET / QUIT
        # ------------------------------------------------------

        self.reset_button = QPushButton(
            "R  RESET"
        )

        self.quit_button = QPushButton(
            "Q  QUIT"
        )

        # ------------------------------------------------------
        # BUTTON HEIGHT
        # ------------------------------------------------------

        buttons = [

            self.mode_button,

            self.takeoff_button,
            self.landing_button,

            self.left_button,
            self.forward_button,
            self.backward_button,
            self.right_button,

            self.rotate_left_button,
            self.rotate_right_button,

            self.up_button,
            self.down_button,

            self.camera_down_button,
            self.camera_up_button,

            self.reset_button,
            self.quit_button,

        ]

        for button in buttons:

            button.setMinimumHeight(
                40
            )

            # Prevent buttons from stealing keyboard focus
            button.setFocusPolicy(
                Qt.NoFocus
            )

        # ======================================================
        # CONTROL GRID
        # ======================================================

        control_grid = QGridLayout()

        control_grid.setSpacing(
            6
        )

        # ======================================================
        # ROW 0
        # ======================================================

        control_grid.addWidget(
            self.mode_button,
            0,
            0
        )

        control_grid.addWidget(
            self.takeoff_button,
            0,
            1
        )

        control_grid.addWidget(
            self.landing_button,
            0,
            2
        )

        control_grid.addWidget(
            self.reset_button,
            0,
            3
        )

        control_grid.addWidget(
            self.quit_button,
            0,
            4
        )

        # ======================================================
        # MOVEMENT
        # ======================================================

        control_grid.addWidget(
            self.forward_button,
            1,
            1
        )

        control_grid.addWidget(
            self.left_button,
            2,
            0
        )

        control_grid.addWidget(
            self.backward_button,
            2,
            1
        )

        control_grid.addWidget(
            self.right_button,
            2,
            2
        )

        # ======================================================
        # VERTICAL
        # ======================================================

        control_grid.addWidget(
            self.up_button,
            1,
            3
        )

        control_grid.addWidget(
            self.down_button,
            2,
            3
        )

        # ======================================================
        # ROTATION
        # ======================================================

        control_grid.addWidget(
            self.rotate_left_button,
            1,
            4
        )

        control_grid.addWidget(
            self.rotate_right_button,
            2,
            4
        )

        # ======================================================
        # CAMERA
        # ======================================================

        control_grid.addWidget(
            self.camera_down_button,
            3,
            0,
            1,
            2
        )

        control_grid.addWidget(
            self.camera_up_button,
            3,
            2,
            1,
            2
        )

        control_layout.addLayout(
            control_grid
        )

        main_layout.addWidget(
            control_frame,
            3,
            0,
            1,
            3
        )

        # ======================================================
        # STRETCH
        # ======================================================

        main_layout.setColumnStretch(
            0,
            1
        )

        main_layout.setColumnStretch(
            1,
            1
        )

        main_layout.setColumnStretch(
            2,
            1
        )

        main_layout.setRowStretch(
            1,
            6
        )

        main_layout.setRowStretch(
            2,
            2
        )

        main_layout.setRowStretch(
            3,
            1
        )

        # ======================================================
        # STYLE
        # ======================================================

        self.setStyleSheet(
            """
            QMainWindow {
                background: #101418;
            }

            QLabel {
                color: #E8EDF2;
                font-size: 13px;
            }

            QLabel#title {
                color: #FFFFFF;
                font-size: 22px;
                font-weight: bold;
                padding: 2px;
            }

            QLabel#video {
                background: #050709;
                border: 1px solid #39424C;
                border-radius: 4px;
                color: #6F7B87;
                font-size: 20px;
            }

            QLabel#sectionTitle {
                color: #FFFFFF;
                font-size: 13px;
                font-weight: bold;
                padding-bottom: 3px;
            }

            QFrame {
                background: #171D23;
                border: 1px solid #303943;
                border-radius: 5px;
            }

            QFrame#videoContainer {
                background: #0B0F13;
            }

            QFrame#controlFrame {
                background: #171D23;
            }

            QPushButton {
                background: #242C34;
                color: #E8EDF2;
                border: 1px solid #3A4652;
                border-radius: 4px;
                padding: 7px 10px;
                font-size: 12px;
            }

            QPushButton:hover {
                background: #303A44;
            }

            QPushButton:pressed {
                background: #1D242B;
            }

            QPushButton:disabled {
                background: #171C21;
                color: #68737D;
                border: 1px solid #262D34;
            }
            """
        )

    # ==========================================================
    # VIDEO
    # ==========================================================

    def update_video(
        self,
        live_frame,
        debug_frame
    ):

        self._set_video_frame(
            self.live_video,
            live_frame
        )

        self._set_video_frame(
            self.debug_video,
            debug_frame
        )

    # ==========================================================
    # SET VIDEO FRAME
    # ==========================================================

    def _set_video_frame(
        self,
        label,
        frame
    ):

        if frame is None:

            return

        try:

            height = int(
                frame.shape[0]
            )

            width = int(
                frame.shape[1]
            )

            bytes_per_line = int(
                frame.strides[0]
            )

            image = QImage(
                frame.data,
                width,
                height,
                bytes_per_line,
                QImage.Format_BGR888
            ).copy()

            pixmap = QPixmap.fromImage(
                image
            )

            scaled = pixmap.scaled(
                label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            label.setPixmap(
                scaled
            )

        except Exception as e:

            print(
                "UI video error:",
                repr(e)
            )

    # ==========================================================
    # UPDATE STATUS
    # ==========================================================

    def update_status(
        self,
        mission,
        camera
    ):

        # ------------------------------------------------------
        # BUTTON STATE
        # ------------------------------------------------------

        manual_mode = (
            mission.is_manual()
        )

        self.camera_down_button.setEnabled(
            manual_mode
        )

        self.camera_up_button.setEnabled(
            manual_mode
        )

        if manual_mode:

            self.mode_button.setText(
                "M  AUTO"
            )

        else:

            self.mode_button.setText(
                "M  MANUAL"
            )

        # ------------------------------------------------------
        # SYSTEM
        # ------------------------------------------------------

        self.mode_label.setText(
            f"Mode: {mission.get_mode()}"
        )

        self.flight_label.setText(
            f"Flight: {mission.get_flight_state()}"
        )

        angle = camera.get_angle()

        if angle is None:

            angle_text = "-"

        else:

            angle_text = f"{angle}°"

        self.camera_label.setText(
            f"Camera: {angle_text}"
        )

        self.mission_label.setText(
            f"Mission: {mission.get_mission_state()}"
        )

        # ------------------------------------------------------
        # QR / FOCUS
        # ------------------------------------------------------

        target_qr = mission.get_target_qr()

        if target_qr is None:

            target_text = "-"

        else:

            target_text = str(
                target_qr
            )

        self.target_label.setText(
            f"Target: {target_text}"
        )

        action = mission.get_target_action()

        if action is None:

            action_text = "-"

        else:

            action_text = str(
                action
            ).upper()

        self.action_label.setText(
            f"Action: {action_text}"
        )

        position = mission.get_position()

        if position is None:

            position_text = "-"

        else:

            position_text = (
                f"({position[0]:.1f}, "
                f"{position[1]:.1f})"
            )

        self.position_label.setText(
            f"Position: {position_text}"
        )

        focus = mission.get_focus_position()

        if focus is None:

            focus_text = "-"

        else:

            focus_text = (
                f"({focus[0]:.1f}, "
                f"{focus[1]:.1f})"
            )

        self.focus_label.setText(
            f"Focus: {focus_text}"
        )

        # ------------------------------------------------------
        # CORRECTION
        # ------------------------------------------------------

        correction_active = (
            mission.is_correction_active()
        )

        current_action = (
            mission.get_current_action()
        )

        if correction_active:

            if current_action is None:

                direction_text = "-"

            else:

                direction_text = (
                    str(
                        current_action
                    ).upper()
                )

        else:

            direction_text = "-"

        status_text = (
            mission.get_correction_status()
        )

        self.direction_label.setText(
            f"Direction: {direction_text}"
        )

        self.distance_label.setText(
            f"Distance: "
            f"{mission.get_correction_distance():.0f} cm"
        )

        self.speed_label.setText(
            f"Speed: "
            f"{mission.get_correction_speed():.0f} cm/s"
        )

        self.status_label.setText(
            f"Status: {status_text}"
        )

    # ==========================================================
    # CONTROL CALLBACKS
    # ==========================================================

    def set_control_callbacks(
        self,
        mode=None,
        takeoff=None,
        landing=None,
        forward=None,
        backward=None,
        left=None,
        right=None,
        rotate_left=None,
        rotate_right=None,
        up=None,
        down=None,
        camera_down=None,
        camera_up=None,
        reset=None,
        quit=None
    ):

        # ======================================================
        # SAVE CALLBACKS
        # ======================================================

        self._callbacks = {

            "mode": mode,
            "takeoff": takeoff,
            "landing": landing,

            "forward": forward,
            "backward": backward,

            "left": left,
            "right": right,

            "rotate_left": rotate_left,
            "rotate_right": rotate_right,

            "up": up,
            "down": down,

            "camera_down": camera_down,
            "camera_up": camera_up,

            "reset": reset,
            "quit": quit,

        }

        # ======================================================
        # BUTTON CALLBACKS
        # ======================================================

        if mode is not None:

            self.mode_button.clicked.connect(
                mode
            )

        if takeoff is not None:

            self.takeoff_button.clicked.connect(
                takeoff
            )

        if landing is not None:

            self.landing_button.clicked.connect(
                landing
            )

        if forward is not None:

            self.forward_button.clicked.connect(
                forward
            )

        if backward is not None:

            self.backward_button.clicked.connect(
                backward
            )

        if left is not None:

            self.left_button.clicked.connect(
                left
            )

        if right is not None:

            self.right_button.clicked.connect(
                right
            )

        if rotate_left is not None:

            self.rotate_left_button.clicked.connect(
                rotate_left
            )

        if rotate_right is not None:

            self.rotate_right_button.clicked.connect(
                rotate_right
            )

        if up is not None:

            self.up_button.clicked.connect(
                up
            )

        if down is not None:

            self.down_button.clicked.connect(
                down
            )

        if camera_down is not None:

            self.camera_down_button.clicked.connect(
                camera_down
            )

        if camera_up is not None:

            self.camera_up_button.clicked.connect(
                camera_up
            )

        if reset is not None:

            self.reset_button.clicked.connect(
                self._confirm_reset(
                    reset
                )
            )

        if quit is not None:

            self.quit_button.clicked.connect(
                quit
            )

        # ======================================================
        # KEYBOARD SHORTCUTS
        # ======================================================

        self._setup_keyboard_shortcuts()

    # ==========================================================
    # KEYBOARD SHORTCUTS
    # ==========================================================

    def _setup_keyboard_shortcuts(self):

        # Clear previous shortcuts
        for shortcut in self._shortcuts:

            shortcut.setEnabled(
                False
            )

            shortcut.deleteLater()

        self._shortcuts.clear()

        # ------------------------------------------------------
        # KEY -> CALLBACK
        # ------------------------------------------------------

        key_map = {

            "M": "mode",

            "T": "takeoff",
            "L": "landing",

            "Up": "forward",
            "Down": "backward",
            "Left": "left",
            "Right": "right",

            "A": "rotate_left",
            "D": "rotate_right",

            "W": "up",
            "S": "down",

            "[": "camera_down",
            "]": "camera_up",

            "R": "reset",
            "Q": "quit",

        }

        for key, action in key_map.items():

            shortcut = QShortcut(
                QKeySequence(key),
                self
            )

            shortcut.setContext(
                Qt.WindowShortcut
            )

            shortcut.activated.connect(
                lambda action=action:
                self._keyboard_action(
                    action
                )
            )

            self._shortcuts.append(
                shortcut
            )

    # ==========================================================
    # KEYBOARD ACTION
    # ==========================================================

    def _keyboard_action(
        self,
        action
    ):

        callback = (
            self._callbacks.get(
                action
            )
        )

        if callback is None:

            return

        print(
            f"KEYBOARD: {action.upper()}"
        )

        # ------------------------------------------------------
        # RESET
        # ------------------------------------------------------

        if action == "reset":

            handler = self._confirm_reset(
                callback
            )

            handler()

            return

        # ------------------------------------------------------
        # QUIT
        # ------------------------------------------------------

        if action == "quit":

            callback()

            return

        # ------------------------------------------------------
        # CAMERA
        # ------------------------------------------------------

        if action in (
            "camera_down",
            "camera_up"
        ):

            button = getattr(
                self,
                f"{action}_button"
            )

            if not button.isEnabled():

                print(
                    "KEYBOARD:",
                    action.upper(),
                    "disabled"
                )

                return

        # ------------------------------------------------------
        # NORMAL CALLBACK
        # ------------------------------------------------------

        callback()

    # ==========================================================
    # RESET CONFIRMATION
    # ==========================================================

    def _confirm_reset(
        self,
        callback
    ):

        def handler():

            result = QMessageBox.question(
                self,
                "Reset Flight State",
                (
                    "Reset flight state?\n\n"
                    "Use RESET only when the drone "
                    "is physically landed."
                ),
                QMessageBox.Yes
                |
                QMessageBox.No,
                QMessageBox.No
            )

            if result == QMessageBox.Yes:

                callback()

        return handler

    # ==========================================================
    # CREATE PANEL
    # ==========================================================

    def _create_panel(
        self,
        title
    ):

        frame = QFrame()

        layout = QVBoxLayout(
            frame
        )

        layout.setContentsMargins(
            10,
            7,
            10,
            7
        )

        layout.setSpacing(
            2
        )

        title_label = QLabel(
            title
        )

        title_label.setObjectName(
            "sectionTitle"
        )

        layout.addWidget(
            title_label
        )

        return frame

    # ==========================================================
    # CLOSE
    # ==========================================================

    def closeEvent(
        self,
        event
    ):

        self.closed = True

        event.accept()


# ==============================================================
# TEST
# ==============================================================

def main():

    app = QApplication(
        sys.argv
    )

    window = MainWindow()

    window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":

    main()