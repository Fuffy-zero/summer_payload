import sys
import math

import cv2

from PySide6.QtCore import (
    Qt,
    QPointF,
    QTimer,
)
from PySide6.QtGui import (
    QImage,
    QPixmap,
    QKeySequence,
    QShortcut,
    QPainter,
    QColor,
    QPen,
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
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)


class JoystickPad(QWidget):
    """
    Draggable analog-style joystick.

    Reports single-axis cardinal directions (up/down/left/right)
    matching the discrete "manual_*" move commands used by the
    mission controller. Dragging the knob past the deadzone in a
    direction fires that command immediately, then repeats it on
    a timer for as long as the stick stays deflected that way —
    releasing snaps the knob back to center and stops sending.
    """

    def __init__(
        self,
        parent=None
    ):

        super().__init__(
            parent
        )

        self._pad_radius = 40
        self._knob_radius = 15

        self.setFixedSize(
            (self._pad_radius + self._knob_radius) * 2,
            (self._pad_radius + self._knob_radius) * 2
        )

        self.setFocusPolicy(
            Qt.NoFocus
        )

        self.setCursor(
            Qt.PointingHandCursor
        )

        self._knob_offset = QPointF(
            0,
            0
        )

        self._dragging = False
        self._active_direction = None

        self._direction_callbacks = {
            "up": None,
            "down": None,
            "left": None,
            "right": None,
        }

        self._repeat_timer = QTimer(
            self
        )

        self._repeat_timer.setInterval(
            260
        )

        self._repeat_timer.timeout.connect(
            self._fire_active_direction
        )

    # ==========================================================
    # CALLBACKS
    # ==========================================================

    def set_callbacks(
        self,
        up=None,
        down=None,
        left=None,
        right=None
    ):

        self._direction_callbacks = {
            "up": up,
            "down": down,
            "left": left,
            "right": right,
        }

        self._set_active_direction(
            None
        )

    # ==========================================================
    # MOUSE EVENTS
    # ==========================================================

    def mousePressEvent(
        self,
        event
    ):

        self._dragging = True

        self._update_from_point(
            event.position()
        )

        event.accept()

    def mouseMoveEvent(
        self,
        event
    ):

        if not self._dragging:

            return

        self._update_from_point(
            event.position()
        )

        event.accept()

    def mouseReleaseEvent(
        self,
        event
    ):

        self._release()

        event.accept()

    def _release(self):

        self._dragging = False

        self._knob_offset = QPointF(
            0,
            0
        )

        self._set_active_direction(
            None
        )

        self.update()

    # ==========================================================
    # KNOB POSITION / DIRECTION
    # ==========================================================

    def _update_from_point(
        self,
        point
    ):

        center = QPointF(
            self.width() / 2,
            self.height() / 2
        )

        delta = point - center

        max_dist = float(
            self._pad_radius
        )

        distance = math.hypot(
            delta.x(),
            delta.y()
        )

        if distance > max_dist and distance > 0:

            scale = max_dist / distance

            delta = QPointF(
                delta.x() * scale,
                delta.y() * scale
            )

        self._knob_offset = delta

        self._evaluate_direction(
            delta,
            max_dist
        )

        self.update()

    def _evaluate_direction(
        self,
        delta,
        max_dist
    ):

        deadzone = max_dist * 0.4

        dx = delta.x()
        dy = delta.y()

        if (
            abs(dx) < deadzone
            and abs(dy) < deadzone
        ):

            self._set_active_direction(
                None
            )

            return

        if abs(dx) >= abs(dy):

            direction = (
                "right"
                if dx > 0
                else "left"
            )

        else:

            direction = (
                "down"
                if dy > 0
                else "up"
            )

        self._set_active_direction(
            direction
        )

    def _set_active_direction(
        self,
        direction
    ):

        if direction == self._active_direction:

            return

        self._active_direction = direction

        if direction is None:

            self._repeat_timer.stop()

            return

        # Fire once immediately on crossing the deadzone, then
        # let the timer keep firing while held.

        self._fire_active_direction()

        self._repeat_timer.start()

    def _fire_active_direction(self):

        callback = self._direction_callbacks.get(
            self._active_direction
        )

        if callback is not None:

            callback()

    # ==========================================================
    # PAINT
    # ==========================================================

    def paintEvent(
        self,
        event
    ):

        painter = QPainter(
            self
        )

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        center = QPointF(
            self.width() / 2,
            self.height() / 2
        )

        # --------------------------------------------------
        # TRACK
        # --------------------------------------------------

        painter.setPen(
            QPen(
                QColor(
                    34,
                    48,
                    58
                ),
                2
            )
        )

        painter.setBrush(
            QColor(
                0,
                0,
                0,
                90
            )
        )

        painter.drawEllipse(
            center,
            self._pad_radius,
            self._pad_radius
        )

        # --------------------------------------------------
        # KNOB
        # --------------------------------------------------

        knob_center = QPointF(
            center.x() + self._knob_offset.x(),
            center.y() + self._knob_offset.y()
        )

        if self._active_direction is not None:

            fill = QColor(
                0,
                229,
                255,
                230
            )

        else:

            fill = QColor(
                0,
                229,
                255,
                140
            )

        painter.setPen(
            QPen(
                QColor(
                    0,
                    229,
                    255
                ),
                2
            )
        )

        painter.setBrush(
            fill
        )

        painter.drawEllipse(
            knob_center,
            self._knob_radius,
            self._knob_radius
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

        # Keep reset handler alive
        self._reset_handler = None

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
        # HEADER
        # ======================================================

        header_frame = QFrame()

        header_frame.setObjectName(
            "headerBar"
        )

        header_layout = QHBoxLayout(
            header_frame
        )

        header_layout.setContentsMargins(
            14,
            6,
            14,
            6
        )

        title = QLabel(
            "Payload Carrier"
        )

        title.setObjectName(
            "title"
        )

        header_layout.addWidget(
            title
        )

        header_layout.addStretch(
            1
        )

        main_layout.addWidget(
            header_frame,
            0,
            0,
            1,
            2
        )

        # ======================================================
        # VIDEO AREA (LEFT COLUMN) — SINGLE VIDEO WITH
        # CONTROLS OVERLAID ON TOP OF IT
        # ======================================================

        video_stack_frame = QFrame()

        video_stack_frame.setObjectName(
            "videoContainer"
        )

        video_stack = QStackedLayout(
            video_stack_frame
        )

        video_stack.setStackingMode(
            QStackedLayout.StackAll
        )

        video_stack.setContentsMargins(
            0,
            0,
            0,
            0
        )

        # ------------------------------------------------------
        # LIVE VIDEO (BASE LAYER)
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

        video_stack.addWidget(
            self.live_video
        )

        # ------------------------------------------------------
        # DEBUG VIDEO — KEPT ALIVE FOR update_video() BUT NOT
        # SHOWN, SINCE ONLY ONE VIDEO SHOULD BE VISIBLE
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

        self.debug_video.hide()

        main_layout.addWidget(
            video_stack_frame,
            1,
            0
        )

        # ======================================================
        # RIGHT SIDEBAR — ALL INFORMATION PANELS
        # ======================================================

        sidebar = QWidget()

        sidebar.setObjectName(
            "sidebar"
        )

        sidebar_layout = QVBoxLayout(
            sidebar
        )

        sidebar_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        sidebar_layout.setSpacing(
            8
        )

        # ------------------------------------------------------
        # STATUS / BATTERY PANEL
        # ------------------------------------------------------

        status_frame = self._create_panel(
            "STATUS"
        )

        status_layout = (
            status_frame.layout()
        )

        status_row = QHBoxLayout()

        status_row.setSpacing(
            10
        )

        self.battery_label = QLabel(
            "BAT: --%"
        )

        self.battery_label.setObjectName(
            "batteryValue"
        )

        self.link_label = QLabel(
            "OFFLINE"
        )

        self.link_label.setObjectName(
            "linkValue"
        )

        status_row.addWidget(
            self.battery_label
        )

        status_row.addWidget(
            self.link_label
        )

        status_row.addStretch(
            1
        )

        status_layout.addLayout(
            status_row
        )

        # ------------------------------------------------------
        # COMMAND COUNTDOWN PANEL (BIG NUMBER DISPLAY)
        # ------------------------------------------------------

        countdown_frame = self._create_panel(
            "COMMAND COUNTDOWN"
        )

        countdown_layout = (
            countdown_frame.layout()
        )

        self.countdown_value_label = QLabel(
            "-"
        )

        self.countdown_value_label.setObjectName(
            "countdownValue"
        )

        self.countdown_value_label.setAlignment(
            Qt.AlignCenter
        )

        self.countdown_source_label = QLabel(
            " "
        )

        self.countdown_source_label.setObjectName(
            "countdownSource"
        )

        self.countdown_source_label.setAlignment(
            Qt.AlignCenter
        )

        countdown_layout.addWidget(
            self.countdown_value_label
        )

        countdown_layout.addWidget(
            self.countdown_source_label
        )

        # ------------------------------------------------------
        # SYSTEM PANEL
        # ------------------------------------------------------

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

        # ------------------------------------------------------
        # QR / FOCUS PANEL
        # ------------------------------------------------------

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

        # ------------------------------------------------------
        # CORRECTION PANEL
        # ------------------------------------------------------

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

        # ------------------------------------------------------
        # ADD PANELS TO SIDEBAR (ALL ON THE RIGHT)
        # ------------------------------------------------------

        sidebar_layout.addWidget(
            status_frame
        )

        sidebar_layout.addWidget(
            countdown_frame
        )

        sidebar_layout.addWidget(
            system_frame
        )

        sidebar_layout.addWidget(
            qr_frame
        )

        sidebar_layout.addWidget(
            correction_frame
        )

        sidebar_layout.addStretch(
            1
        )

        main_layout.addWidget(
            sidebar,
            1,
            1
        )

        # ======================================================
        # CONTROL BAR — NOW AN OVERLAY DOCKED TO THE BOTTOM
        # OF THE VIDEO AREA (NOT A SEPARATE ROW)
        # ======================================================

        control_frame = QFrame()

        control_frame.setObjectName(
            "controlFrame"
        )

        control_layout = QHBoxLayout(
            control_frame
        )

        control_layout.setContentsMargins(
            16,
            10,
            16,
            10
        )

        control_layout.setSpacing(
            20
        )

        # ------------------------------------------------------
        # LEFT STICK — THROTTLE / YAW
        # (UP/DOWN = ALTITUDE, LEFT/RIGHT = ROTATE)
        # ------------------------------------------------------

        left_stick_frame, self.left_joystick = (
            self._create_joystick_control(
                "THROTTLE · YAW"
            )
        )

        # ------------------------------------------------------
        # CENTER — MODE / FLIGHT / CAMERA / RESET / QUIT
        # ------------------------------------------------------

        center_column = QVBoxLayout()

        center_column.setSpacing(
            5
        )

        top_row = QHBoxLayout()

        top_row.setSpacing(
            8
        )

        self.mode_button = QPushButton(
            "M  AUTO"
        )

        self.reset_button = QPushButton(
            "R  RESET"
        )

        self.quit_button = QPushButton(
            "Q  QUIT"
        )

        self.mode_button.setObjectName(
            "neutralBtn"
        )

        self.reset_button.setObjectName(
            "neutralBtn"
        )

        self.quit_button.setObjectName(
            "dangerNeutralBtn"
        )

        top_row.addWidget(
            self.mode_button
        )

        top_row.addWidget(
            self.reset_button
        )

        top_row.addWidget(
            self.quit_button
        )

        fly_row = QHBoxLayout()

        fly_row.setSpacing(
            10
        )

        self.takeoff_button = QPushButton(
            "TAKEOFF"
        )

        self.landing_button = QPushButton(
            "LAND"
        )

        self.takeoff_button.setObjectName(
            "takeoffBtn"
        )

        self.landing_button.setObjectName(
            "landBtn"
        )

        fly_row.addWidget(
            self.takeoff_button
        )

        fly_row.addWidget(
            self.landing_button
        )

        cam_row = QHBoxLayout()

        cam_row.setSpacing(
            8
        )

        self.camera_down_button = QPushButton(
            "[  CAM DOWN"
        )

        self.camera_up_button = QPushButton(
            "CAM UP  ]"
        )

        self.camera_down_button.setObjectName(
            "neutralBtn"
        )

        self.camera_up_button.setObjectName(
            "neutralBtn"
        )

        cam_row.addWidget(
            self.camera_down_button
        )

        cam_row.addWidget(
            self.camera_up_button
        )

        center_column.addLayout(
            top_row
        )

        center_column.addLayout(
            fly_row
        )

        center_column.addLayout(
            cam_row
        )

        # ------------------------------------------------------
        # RIGHT STICK — PITCH / ROLL
        # (UP/DOWN = FORWARD/BACKWARD, LEFT/RIGHT = STRAFE)
        # ------------------------------------------------------

        right_stick_frame, self.right_joystick = (
            self._create_joystick_control(
                "PITCH · ROLL"
            )
        )

        # ------------------------------------------------------
        # ASSEMBLE CONTROL BAR
        # ------------------------------------------------------

        control_layout.addWidget(
            left_stick_frame
        )

        control_layout.addStretch(
            1
        )

        control_layout.addLayout(
            center_column
        )

        control_layout.addStretch(
            1
        )

        control_layout.addWidget(
            right_stick_frame
        )

        # ------------------------------------------------------
        # OVERLAY WRAPPER — TRANSPARENT LAYER PLACED ON TOP OF
        # THE VIDEO. STRETCH ABOVE PUSHES THE CONTROL BAR TO
        # THE BOTTOM EDGE OF THE VIDEO.
        # ------------------------------------------------------

        video_overlay = QWidget()

        video_overlay.setObjectName(
            "videoOverlay"
        )

        overlay_layout = QVBoxLayout(
            video_overlay
        )

        overlay_layout.setContentsMargins(
            14,
            14,
            14,
            14
        )

        overlay_layout.addStretch(
            1
        )

        overlay_layout.addWidget(
            control_frame
        )

        video_stack.addWidget(
            video_overlay
        )

        # --------------------------------------------------
        # RAISE THE CONTROL OVERLAY ABOVE THE VIDEO LAYER.
        # StackAll KEEPS BOTH WIDGETS VISIBLE, BUT THE
        # "current" WIDGET IS THE ONE DRAWN ON TOP — WITHOUT
        # THIS, THE VIDEO LAYER (INDEX 0) STAYS ON TOP AND
        # COMPLETELY HIDES THE BUTTONS BEHIND IT.
        # --------------------------------------------------

        video_stack.setCurrentWidget(
            video_overlay
        )

        # ======================================================
        # BUTTON SIZING
        # ======================================================

        other_buttons = [

            self.mode_button,

            self.takeoff_button,
            self.landing_button,

            self.camera_down_button,
            self.camera_up_button,

            self.reset_button,
            self.quit_button,

        ]

        for button in other_buttons:

            button.setMinimumHeight(
                38
            )

            # Prevent buttons from stealing keyboard focus
            button.setFocusPolicy(
                Qt.NoFocus
            )

        # ======================================================
        # STRETCH
        # ======================================================

        main_layout.setColumnStretch(
            0,
            3
        )

        main_layout.setColumnStretch(
            1,
            1
        )

        main_layout.setRowStretch(
            1,
            1
        )

        # ======================================================
        # STYLE
        # ======================================================

        self.setStyleSheet(
            """
            QMainWindow {
                background: #0A0F14;
            }

            QLabel {
                color: #E8EDF2;
                font-size: 13px;
            }

            QFrame#headerBar {
                background: #0D141B;
                border: 1px solid #1C2731;
                border-radius: 6px;
            }

            QLabel#title {
                color: #00E5FF;
                font-size: 20px;
                font-weight: 900;
                padding: 2px;
            }

            QLabel#video {
                background: #05070A;
                border: 1px solid #1C2731;
                border-radius: 4px;
                color: #55636E;
                font-size: 20px;
            }

            QLabel#sectionTitle {
                color: #00E5FF;
                font-size: 12px;
                font-weight: bold;
                padding-bottom: 3px;
            }

            QLabel#batteryValue {
                color: #F39C12;
                font-size: 15px;
                font-weight: bold;
            }

            QLabel#batteryValue[level="low"] {
                color: #FF2D55;
            }

            QLabel#batteryValue[level="unknown"] {
                color: #7C8892;
            }

            QLabel#linkValue {
                color: #FF2D55;
                font-size: 12px;
                font-weight: bold;
            }

            QLabel#linkValue[state="live"] {
                color: #00FF88;
            }

            QLabel#countdownValue {
                color: #00E5FF;
                font-size: 56px;
                font-weight: 900;
                padding: 4px 0px;
            }

            QLabel#countdownValue[active="true"] {
                color: #FF2D55;
            }

            QLabel#countdownSource {
                color: #8AA0AC;
                font-size: 12px;
                font-weight: bold;
                padding-bottom: 2px;
            }

            QFrame {
                background: #10161C;
                border: 1px solid #22303A;
                border-radius: 6px;
            }

            QFrame#panel {
                background: rgba(15, 22, 28, 0.92);
                border: 1px solid #22303A;
                border-radius: 6px;
            }

            QFrame#videoContainer {
                background: #05080B;
                border-radius: 6px;
            }

            QWidget#videoOverlay {
                background: transparent;
            }

            QFrame#controlFrame {
                background: transparent;
                border: none;
            }

            QFrame#stickPad {
                background: rgba(0, 0, 0, 0.35);
                border: 2px solid #22303A;
                border-radius: 18px;
            }

            QLabel#stickLabel {
                color: #8AA0AC;
                font-size: 10px;
                font-weight: bold;
                background: transparent;
                border: none;
            }

            QPushButton {
                background: #182028;
                color: #E8EDF2;
                border: 1px solid #2C3944;
                border-radius: 6px;
                padding: 7px 10px;
                font-size: 12px;
                font-weight: bold;
            }

            QPushButton:hover {
                background: #22303A;
            }

            QPushButton:pressed {
                background: #101820;
            }

            QPushButton:disabled {
                background: #12181D;
                color: #556069;
                border: 1px solid #1E262D;
            }

            QPushButton#takeoffBtn {
                border-radius: 19px;
                border: 2px solid #00FF88;
                color: #00FF88;
                padding: 9px 20px;
            }

            QPushButton#takeoffBtn:hover {
                background: rgba(0, 255, 136, 0.15);
            }

            QPushButton#landBtn {
                border-radius: 19px;
                border: 2px solid #FF2D55;
                color: #FF2D55;
                padding: 9px 20px;
            }

            QPushButton#landBtn:hover {
                background: rgba(255, 45, 85, 0.15);
            }

            QPushButton#neutralBtn {
                border-radius: 15px;
                border: 1px solid #3A4652;
                color: #CFD8DE;
            }

            QPushButton#dangerNeutralBtn {
                border-radius: 15px;
                border: 1px solid #FF2D55;
                color: #FF2D55;
            }
            """
        )

    # ==========================================================
    # RESIZE EVENT
    # ==========================================================

    def resizeEvent(
        self,
        event
    ):

        super().resizeEvent(
            event
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

            # ==================================================
            # COPY FRAME
            # ==================================================

            display_frame = (
                frame.copy()
            )

            # ==================================================
            # BGR -> QIMAGE
            # ==================================================

            bytes_per_line = int(
                display_frame.strides[0]
            )

            image = QImage(
                display_frame.data,
                width,
                height,
                bytes_per_line,
                QImage.Format_BGR888
            ).copy()

            pixmap = QPixmap.fromImage(
                image
            )

            # ==================================================
            # SCALE VIDEO
            # ==================================================

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
    # UPDATE BATTERY / LINK STATUS
    # ==========================================================

    def _update_battery_status(
        self,
        bridge
    ):

        value = (
            bridge.get_battery()
        )

        level = "unknown"

        if value in (None, "--"):

            text = "BAT: --%"

        else:

            try:

                percent = int(
                    float(value)
                )

                text = f"BAT: {percent}%"

                level = (
                    "low"
                    if percent <= 20
                    else "normal"
                )

            except (TypeError, ValueError):

                text = f"BAT: {value}"

                level = "unknown"

        self.battery_label.setText(
            text
        )

        self.battery_label.setProperty(
            "level",
            level
        )

        self.battery_label.style().unpolish(
            self.battery_label
        )

        self.battery_label.style().polish(
            self.battery_label
        )

        # ------------------------------------------------------
        # LINK STATE
        # ------------------------------------------------------

        if bridge.connected:

            self.link_label.setText(
                "LINK ACTIVE"
            )

            self.link_label.setProperty(
                "state",
                "live"
            )

        else:

            self.link_label.setText(
                "OFFLINE"
            )

            self.link_label.setProperty(
                "state",
                "offline"
            )

        self.link_label.style().unpolish(
            self.link_label
        )

        self.link_label.style().polish(
            self.link_label
        )

    # ==========================================================
    # UPDATE STATUS
    # ==========================================================

    def update_status(
        self,
        mission,
        camera,
        bridge=None
    ):

        # ======================================================
        # BATTERY / LINK (RIGHT-SIDE STATUS PANEL)
        # ======================================================

        if bridge is not None:

            self._update_battery_status(
                bridge
            )

        # ======================================================
        # BUTTON STATE
        # ======================================================

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

        # ======================================================
        # SYSTEM
        # ======================================================

        self.mode_label.setText(
            f"Mode: {mission.get_mode()}"
        )

        self.flight_label.setText(
            f"Flight: {mission.get_flight_state()}"
        )

        # ------------------------------------------------------
        # CAMERA
        # ------------------------------------------------------

        angle = camera.get_angle()

        if angle is None:

            angle_text = "-"

        else:

            angle_text = f"{angle}°"

        self.camera_label.setText(
            f"Camera: {angle_text}"
        )

        # ------------------------------------------------------
        # MISSION
        # ------------------------------------------------------

        self.mission_label.setText(
            f"Mission: {mission.get_mission_state()}"
        )

        # ======================================================
        # COMMAND COUNTDOWN
        # ======================================================

        if mission.is_command_countdown_active():

            seconds = (
                mission.get_command_countdown_seconds()
            )

            source = (
                mission.get_command_countdown_source()
            )

            if source is None:

                source_text = "QR"

            else:

                source_text = str(
                    source
                )

            # --------------------------------------------------
            # BIG COUNTDOWN NUMBER (SIDEBAR ONLY)
            # --------------------------------------------------

            self.countdown_value_label.setText(
                str(seconds)
            )

            self.countdown_source_label.setText(
                source_text
            )

            self.countdown_value_label.setProperty(
                "active",
                "true"
            )

            self.countdown_value_label.style().unpolish(
                self.countdown_value_label
            )

            self.countdown_value_label.style().polish(
                self.countdown_value_label
            )

        else:

            # --------------------------------------------------
            # NO ACTIVE COMMAND
            # --------------------------------------------------

            self.countdown_value_label.setText(
                "-"
            )

            self.countdown_source_label.setText(
                " "
            )

            self.countdown_value_label.setProperty(
                "active",
                "false"
            )

            self.countdown_value_label.style().unpolish(
                self.countdown_value_label
            )

            self.countdown_value_label.style().polish(
                self.countdown_value_label
            )

        # ======================================================
        # QR / FOCUS
        # ======================================================

        target_qr = (
            mission.get_target_qr()
        )

        if target_qr is None:

            target_text = "-"

        else:

            target_text = str(
                target_qr
            )

        self.target_label.setText(
            f"Target: {target_text}"
        )

        # ------------------------------------------------------
        # ACTION
        # ------------------------------------------------------

        action = (
            mission.get_target_action()
        )

        if action is None:

            action_text = "-"

        else:

            action_text = str(
                action
            ).upper()

        self.action_label.setText(
            f"Action: {action_text}"
        )

        # ------------------------------------------------------
        # POSITION
        # ------------------------------------------------------

        position = (
            mission.get_position()
        )

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

        # ------------------------------------------------------
        # FOCUS
        # ------------------------------------------------------

        focus = (
            mission.get_focus_position()
        )

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

        # ======================================================
        # CORRECTION
        # ======================================================

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

        self.direction_label.setText(
            f"Direction: {direction_text}"
        )

        # ------------------------------------------------------
        # DISTANCE
        # ------------------------------------------------------

        self.distance_label.setText(
            f"Distance: "
            f"{mission.get_correction_distance():.0f} cm"
        )

        # ------------------------------------------------------
        # SPEED
        # ------------------------------------------------------

        self.speed_label.setText(
            f"Speed: "
            f"{mission.get_correction_speed():.0f} cm/s"
        )

        # ------------------------------------------------------
        # STATUS
        # ------------------------------------------------------

        status_text = (
            mission.get_correction_status()
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
        # DISCONNECT PREVIOUS BUTTON SIGNALS
        # ======================================================

        self._disconnect_button_callbacks()

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

        if any(
            value is not None
            for value in (forward, backward, left, right)
        ):

            self.right_joystick.set_callbacks(
                up=forward,
                down=backward,
                left=left,
                right=right
            )

        if any(
            value is not None
            for value in (up, down, rotate_left, rotate_right)
        ):

            self.left_joystick.set_callbacks(
                up=up,
                down=down,
                left=rotate_left,
                right=rotate_right
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

            self._reset_handler = (
                self._confirm_reset(
                    reset
                )
            )

            self.reset_button.clicked.connect(
                self._reset_handler
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
    # DISCONNECT BUTTON CALLBACKS
    # ==========================================================

    def _disconnect_button_callbacks(self):

        buttons = [

            self.mode_button,
            self.takeoff_button,
            self.landing_button,

            self.camera_down_button,
            self.camera_up_button,

            self.reset_button,
            self.quit_button,

        ]

        for button in buttons:

            try:

                button.clicked.disconnect()

            except (TypeError, RuntimeError):

                pass

        self.left_joystick.set_callbacks()
        self.right_joystick.set_callbacks()

        self._reset_handler = None

    # ==========================================================
    # KEYBOARD SHORTCUTS
    # ==========================================================

    def _setup_keyboard_shortcuts(self):

        # ------------------------------------------------------
        # CLEAR PREVIOUS SHORTCUTS
        # ------------------------------------------------------

        for shortcut in self._shortcuts:

            shortcut.setEnabled(
                False
            )

            shortcut.deleteLater()

        self._shortcuts.clear()

        # ======================================================
        # KEY -> CALLBACK
        # ======================================================

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

        # ======================================================
        # RESET
        # ======================================================

        if action == "reset":

            handler = (
                self._confirm_reset(
                    callback
                )
            )

            handler()

            return

        # ======================================================
        # QUIT
        # ======================================================

        if action == "quit":

            callback()

            return

        # ======================================================
        # CAMERA
        # ======================================================

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

        # ======================================================
        # NORMAL CALLBACK
        # ======================================================

        callback()

    # ==========================================================
    # RESET CONFIRMATION
    # ==========================================================

    def _confirm_reset(
        self,
        callback
    ):

        def handler():

            if callback is None:

                return

            message_box = QMessageBox(
                self
            )

            message_box.setWindowTitle(
                "Reset Flight State"
            )

            message_box.setText(
                "Select the current physical flight state:"
            )

            message_box.setInformativeText(
                "Choose the state that matches "
                "the drone's actual physical condition."
            )

            flying_button = message_box.addButton(
                "FLYING",
                QMessageBox.AcceptRole
            )

            landed_button = message_box.addButton(
                "LANDED",
                QMessageBox.AcceptRole
            )

            cancel_button = message_box.addButton(
                "CANCEL",
                QMessageBox.RejectRole
            )

            message_box.setDefaultButton(
            cancel_button
            )

            message_box.exec()

            clicked = (
                message_box.clickedButton()
            )

            if clicked == flying_button:

                print(
                    "RESET selected: FLYING"
                )

                callback(
                    "FLYING"
                )

            elif clicked == landed_button:

                print(
                    "RESET selected: LANDED"
                )

                callback(
                    "LANDED"
                )

            else:

                print(
                    "RESET cancelled."
                )

        return handler

    # ==========================================================
    # CREATE PANEL
    # ==========================================================

    def _create_panel(
        self,
        title
    ):

        frame = QFrame()

        frame.setObjectName(
            "panel"
        )

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
    # CREATE JOYSTICK CONTROL
    #
    # Small rounded HUD-style pad hosting a single draggable
    # JoystickPad, in the same visual language used elsewhere
    # (throttle/yaw on the left, pitch/roll on the right).
    # ==========================================================

    def _create_joystick_control(
        self,
        label_text
    ):

        frame = QFrame()

        frame.setObjectName(
            "stickPad"
        )

        outer_layout = QVBoxLayout(
            frame
        )

        outer_layout.setContentsMargins(
            10,
            10,
            10,
            6
        )

        outer_layout.setSpacing(
            6
        )

        joystick = JoystickPad()

        outer_layout.addWidget(
            joystick,
            0,
            Qt.AlignCenter
        )

        label = QLabel(
            label_text
        )

        label.setAlignment(
            Qt.AlignCenter
        )

        label.setObjectName(
            "stickLabel"
        )

        outer_layout.addWidget(
            label
        )

        return frame, joystick

    # ==========================================================
    # CLOSE
    # ==========================================================

    def closeEvent(
        self,
        event
    ):

        self.closed = True

        # ------------------------------------------------------
        # DISABLE SHORTCUTS
        # ------------------------------------------------------

        for shortcut in self._shortcuts:

            shortcut.setEnabled(
                False
            )

        self._shortcuts.clear()

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