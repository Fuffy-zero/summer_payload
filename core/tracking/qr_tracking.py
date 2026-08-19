import cv2


class QRTracker:

    def __init__(
        self,
        config=None
    ):

        self.config = config

        # ======================================================
        # QR STATE
        # ======================================================

        self.detected = False
        self.data = None

        # ======================================================
        # QR CENTER
        # ======================================================

        self.center_x = None
        self.center_y = None

        # ======================================================
        # QR POINTS
        # ======================================================

        self.points = None

        # ======================================================
        # DETECTOR
        # ======================================================

        self.detector = cv2.QRCodeDetector()

    # ======================================================
    # UPDATE
    # ======================================================

    def update(
        self,
        frame
    ):

        if frame is None:

            self._set_not_detected()

            return self.get_state()

        try:

            data, points, _ = (
                self.detector.detectAndDecode(
                    frame
                )
            )

        except cv2.error:

            self._set_not_detected()

            return self.get_state()

        # ==================================================
        # QR FOUND
        # ==================================================

        if points is not None:

            try:

                self.points = points

                pts = points[0]

                self.center_x = float(
                    pts[:, 0].mean()
                )

                self.center_y = float(
                    pts[:, 1].mean()
                )

                # ------------------------------------------
                # DECODE SUCCESS
                # ------------------------------------------

                if data:

                    self.detected = True

                    # QR data ต้องตรงกับ config เช่น:
                    # qr1
                    # qr2
                    # qr3

                    self.data = str(
                        data
                    ).strip()

                # ------------------------------------------
                # QR FOUND BUT DECODE FAILED
                # ------------------------------------------

                else:

                    self.detected = False
                    self.data = None

            except (
                IndexError,
                ValueError,
                TypeError
            ):

                self._set_not_detected()

        # ==================================================
        # NO QR
        # ==================================================

        else:

            self._set_not_detected()

        return self.get_state()

    # ======================================================
    # SET NOT DETECTED
    # ======================================================

    def _set_not_detected(self):

        self.detected = False

        self.data = None

        self.points = None

        self.center_x = None
        self.center_y = None

    # ======================================================
    # STATE
    # ======================================================

    def get_state(self):

        return {

            "detected":
                self.detected,

            "data":
                self.data,

            "center_x":
                self.center_x,

            "center_y":
                self.center_y,

            "points":
                self.points

        }

    # ======================================================
    # RESET
    # ======================================================

    def reset(self):

        self._set_not_detected()

    # ======================================================
    # GET FOCUS POINT
    # ======================================================

    def _get_focus_point(
        self,
        qr_id,
        frame
    ):

        # --------------------------------------------------
        # ถ้ามี config และมี Focus Point ของ QR นี้
        # --------------------------------------------------

        if self.config is not None:

            focus_points = getattr(
                self.config,
                "QR_FOCUS_POINTS",
                {}
            )

            if isinstance(
                focus_points,
                dict
            ):

                point = focus_points.get(
                    qr_id
                )

                if point is None:

                    point = focus_points.get(
                        str(qr_id)
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

        # --------------------------------------------------
        # ถ้าไม่มี config point
        # ใช้กลางภาพจริง
        # --------------------------------------------------

        if frame is not None:

            height = frame.shape[0]
            width = frame.shape[1]

            return (
                width / 2.0,
                height / 2.0
            )

        return None

    # ======================================================
    # GET TOLERANCE
    # ======================================================

    def _get_focus_tolerance(self):

        if self.config is None:

            return 50.0

        try:

            return float(
                getattr(
                    self.config,
                    "FOCUS_TOLERANCE",
                    50.0
                )
            )

        except (
            TypeError,
            ValueError
        ):

            return 50.0

    # ======================================================
    # DEBUG
    # ======================================================

    def draw_debug(
        self,
        frame,
        state
    ):

        if frame is None:

            return frame

        try:

            height = frame.shape[0]
            width = frame.shape[1]

            # ==================================================
            # FRAME CENTER
            # ==================================================

            frame_center_x = width / 2.0
            frame_center_y = height / 2.0

            # ==================================================
            # FOCUS
            # ==================================================

            focus_point = self._get_focus_point(
                state["data"],
                frame
            )

            if focus_point is None:

                focus_x = frame_center_x
                focus_y = frame_center_y

            else:

                focus_x = focus_point[0]
                focus_y = focus_point[1]

            tolerance = (
                self._get_focus_tolerance()
            )

            # ==================================================
            # FOCUS RECTANGLE
            # ==================================================

            left = int(
                focus_x - tolerance
            )

            top = int(
                focus_y - tolerance
            )

            right = int(
                focus_x + tolerance
            )

            bottom = int(
                focus_y + tolerance
            )

            cv2.rectangle(

                frame,

                (left, top),

                (right, bottom),

                (255, 255, 0),

                2

            )

            # ==================================================
            # FOCUS CENTER
            # ==================================================

            cv2.circle(

                frame,

                (
                    int(focus_x),
                    int(focus_y)
                ),

                7,

                (255, 255, 0),

                -1

            )

            # ==================================================
            # FRAME CENTER
            # ==================================================

            cv2.drawMarker(

                frame,

                (
                    int(frame_center_x),
                    int(frame_center_y)
                ),

                (255, 0, 255),

                cv2.MARKER_CROSS,

                20,

                2

            )

            # ==================================================
            # FOCUS TEXT
            # ==================================================

            cv2.putText(

                frame,

                (
                    f"FOCUS "
                    f"({int(focus_x)}, {int(focus_y)}) "
                    f"TOL={int(tolerance)}"
                ),

                (
                    max(5, left),
                    max(25, top - 10)
                ),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.6,

                (255, 255, 0),

                2

            )

            # ==================================================
            # QR BOUNDARY
            # ==================================================

            points = state["points"]

            if points is not None:

                points = points.astype(int)

                for i in range(4):

                    cv2.line(

                        frame,

                        tuple(
                            points[0][i]
                        ),

                        tuple(
                            points[0][
                                (i + 1) % 4
                            ]
                        ),

                        (0, 255, 0),

                        3

                    )

            # ==================================================
            # QR CENTER
            # ==================================================

            center_x = state["center_x"]
            center_y = state["center_y"]

            if (
                center_x is not None
                and
                center_y is not None
            ):

                x = int(
                    center_x
                )

                y = int(
                    center_y
                )

                cv2.circle(

                    frame,

                    (x, y),

                    8,

                    (255, 0, 0),

                    -1

                )

                # ==================================================
                # DISTANCE FROM FOCUS
                # ==================================================

                diff_x = (
                    center_x
                    -
                    focus_x
                )

                diff_y = (
                    center_y
                    -
                    focus_y
                )

                distance = (
                    diff_x ** 2
                    +
                    diff_y ** 2
                ) ** 0.5

                inside = (
                    distance <= tolerance
                )

                # ==================================================
                # QR TEXT
                # ==================================================

                if state["detected"]:

                    text = (
                        f"QR: {state['data']}"
                    )

                else:

                    text = (
                        "QR: decode failed"
                    )

                cv2.putText(

                    frame,

                    text,

                    (
                        x + 15,
                        y - 15
                    ),

                    cv2.FONT_HERSHEY_SIMPLEX,

                    0.7,

                    (0, 255, 0),

                    2

                )

                # ==================================================
                # FOCUS STATUS
                # ==================================================

                status = (
                    "IN FOCUS"
                    if inside
                    else "OUT OF FOCUS"
                )

                cv2.putText(

                    frame,

                    (
                        f"{status} "
                        f"diff=({diff_x:.0f},"
                        f"{diff_y:.0f}) "
                        f"d={distance:.0f}"
                    ),

                    (
                        20,
                        30
                    ),

                    cv2.FONT_HERSHEY_SIMPLEX,

                    0.65,

                    (0, 255, 0),

                    2

                )

            # ==================================================
            # FRAME INFO
            # ==================================================

            cv2.putText(

                frame,

                (
                    f"FRAME "
                    f"{width}x{height}"
                ),

                (
                    20,
                    height - 20
                ),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.6,

                (255, 255, 255),

                2

            )

        except (
            IndexError,
            ValueError,
            TypeError
        ):

            pass

        return frame