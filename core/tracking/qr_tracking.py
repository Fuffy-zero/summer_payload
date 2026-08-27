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
        # ALL DETECTED QR
        # ======================================================

        self.all_qr = []

        # ======================================================
        # DETECTOR
        # ======================================================

        self.detector = cv2.QRCodeDetector()

    # ==========================================================
    # GET ALLOWED QR IDS
    # ==========================================================

    def _get_allowed_qr_ids(self):

        if self.config is None:

            return set()

        # ------------------------------------------------------
        # OPTION 1
        # QR_ALLOWED_IDS
        # ------------------------------------------------------

        allowed = getattr(
            self.config,
            "QR_ALLOWED_IDS",
            None
        )

        if allowed is not None:

            try:

                return {
                    str(x).strip()
                    for x in allowed
                }

            except TypeError:

                pass

        # ------------------------------------------------------
        # OPTION 2
        # QR_IDS
        # ------------------------------------------------------

        allowed = getattr(
            self.config,
            "QR_IDS",
            None
        )

        if allowed is not None:

            try:

                return {
                    str(x).strip()
                    for x in allowed
                }

            except TypeError:

                pass

        # ------------------------------------------------------
        # OPTION 3
        # QR_ACTIONS
        #
        # ใช้ key ของ QR_ACTIONS เป็นรายการ QR
        # ที่ระบบอนุญาต
        #
        # ตัวอย่าง:
        #
        # QR_ACTIONS = {
        #     "qr1": "take_off",
        #     "qr2": "left",
        #     "qr3": "forward",
        #     ...
        # }
        #
        # ดังนั้นเพิ่ม QR ใหม่ใน config ได้เลย
        # โดยไม่ต้องแก้ QRTracker
        # ------------------------------------------------------

        actions = getattr(
            self.config,
            "QR_ACTIONS",
            {}
        )

        if isinstance(
            actions,
            dict
        ):

            return {
                str(x).strip()
                for x in actions.keys()
            }

        # ------------------------------------------------------
        # ไม่มีการกำหนด QR
        # ------------------------------------------------------

        return set()

    # ==========================================================
    # CHECK ALLOWED QR
    # ==========================================================

    def _is_allowed_qr(
        self,
        qr_data
    ):

        if qr_data is None:

            return False

        qr_data = str(
            qr_data
        ).strip()

        if not qr_data:

            return False

        allowed_ids = (
            self._get_allowed_qr_ids()
        )

        # ------------------------------------------------------
        # ไม่มี allowed list
        #
        # เพื่อความปลอดภัย:
        # ไม่รับ QR ที่ไม่ได้กำหนดไว้
        # ------------------------------------------------------

        if not allowed_ids:

            return False

        return qr_data in allowed_ids

    # ==========================================================
    # GET FOCUS POINT
    # ==========================================================

    def _get_focus_point(
        self,
        qr_id,
        frame
    ):

        # ======================================================
        # GLOBAL QR FOCUS POINT
        #
        # ทุก QR ใช้จุดเดียวกัน
        #
        # config:
        #
        # QR_FOCUS_POINT = (640, 360)
        # ======================================================

        if self.config is not None:

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
        # ถ้าไม่มี global focus point
        # ใช้กลางภาพ
        # ------------------------------------------------------

        if frame is not None:

            height = frame.shape[0]
            width = frame.shape[1]

            return (
                width / 2.0,
                height / 2.0
            )

        return None

    # ==========================================================
    # GET TOLERANCE
    # ==========================================================

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

    # ==========================================================
    # UPDATE
    # ==========================================================

    def update(
        self,
        frame
    ):

        if frame is None:

            self._set_not_detected()

            return self.get_state()

        # ------------------------------------------------------
        # RESET CURRENT STATE
        # ------------------------------------------------------

        self.detected = False
        self.data = None
        self.points = None
        self.center_x = None
        self.center_y = None
        self.all_qr = []

        # ======================================================
        # DETECT MULTIPLE QR
        # ======================================================

        try:

            result = (
                self.detector.detectAndDecodeMulti(
                    frame
                )
            )

        except cv2.error:

            self._set_not_detected()

            return self.get_state()

        # ======================================================
        # HANDLE RESULT
        # ======================================================

        try:

            retval = result[0]
            decoded_info = result[1]
            points = result[2]

        except (
            IndexError,
            TypeError
        ):

            self._set_not_detected()

            return self.get_state()

        # ------------------------------------------------------
        # ไม่มี QR
        # ------------------------------------------------------

        if (
            not retval
            or points is None
            or decoded_info is None
        ):

            self._set_not_detected()

            return self.get_state()

        # ======================================================
        # PROCESS ALL QR
        # ======================================================

        valid_qrs = []

        try:

            for index, raw_data in enumerate(
                decoded_info
            ):

                # --------------------------------------------------
                # ต้องมี points ตรงกับ data
                # --------------------------------------------------

                if index >= len(points):

                    continue

                qr_points = points[index]

                if qr_points is None:

                    continue

                # --------------------------------------------------
                # DATA
                # --------------------------------------------------

                data = str(
                    raw_data
                ).strip()

                # --------------------------------------------------
                # CENTER
                # --------------------------------------------------

                try:

                    pts = qr_points

                    center_x = float(
                        pts[:, 0].mean()
                    )

                    center_y = float(
                        pts[:, 1].mean()
                    )

                except (
                    IndexError,
                    ValueError,
                    TypeError
                ):

                    continue

                # --------------------------------------------------
                # SAVE ALL DETECTED QR
                #
                # เก็บทุก QR ที่กล้องอ่านได้
                # ทั้งที่ allowed และ ignored
                # --------------------------------------------------

                qr_info = {

                    "data": data,

                    "center_x": center_x,

                    "center_y": center_y,

                    "points": qr_points,

                    "allowed":
                        self._is_allowed_qr(
                            data
                        )

                }

                self.all_qr.append(
                    qr_info
                )

                # --------------------------------------------------
                # FILTER
                # --------------------------------------------------

                if not qr_info["allowed"]:

                    continue

                # --------------------------------------------------
                # VALID QR
                # --------------------------------------------------

                valid_qrs.append(
                    qr_info
                )

        except (
            IndexError,
            ValueError,
            TypeError
        ):

            pass

        # ======================================================
        # NO VALID QR
        # ======================================================

        if not valid_qrs:

            self._set_not_detected(
                keep_all_qr=True
            )

            return self.get_state()

        # ======================================================
        # SELECT QR
        #
        # ถ้ามีหลายตัว:
        # เลือกตัวที่ใกล้ Global Focus Point ที่สุด
        # ======================================================

        best_qr = None
        best_distance = None

        frame_height = frame.shape[0]
        frame_width = frame.shape[1]

        frame_center_x = (
            frame_width / 2.0
        )

        frame_center_y = (
            frame_height / 2.0
        )

        focus_point = (
            self._get_focus_point(
                None,
                frame
            )
        )

        if focus_point is None:

            focus_x = frame_center_x
            focus_y = frame_center_y

        else:

            focus_x = focus_point[0]
            focus_y = focus_point[1]

        for qr in valid_qrs:

            diff_x = (
                qr["center_x"]
                - focus_x
            )

            diff_y = (
                qr["center_y"]
                - focus_y
            )

            distance = (
                diff_x ** 2
                +
                diff_y ** 2
            ) ** 0.5

            if (
                best_distance is None
                or distance < best_distance
            ):

                best_distance = distance

                best_qr = qr

        # ======================================================
        # SAVE SELECTED QR
        # ======================================================

        if best_qr is None:

            self._set_not_detected(
                keep_all_qr=True
            )

            return self.get_state()

        self.detected = True

        self.data = (
            best_qr["data"]
        )

        self.center_x = (
            best_qr["center_x"]
        )

        self.center_y = (
            best_qr["center_y"]
        )

        self.points = (
            best_qr["points"]
        )

        return self.get_state()

    # ==========================================================
    # SET NOT DETECTED
    # ==========================================================

    def _set_not_detected(
        self,
        keep_all_qr=False
    ):

        self.detected = False
        self.data = None
        self.points = None

        self.center_x = None
        self.center_y = None

        if not keep_all_qr:

            self.all_qr = []

    # ==========================================================
    # STATE
    # ==========================================================

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
                self.points,

            "all_qr":
                self.all_qr

        }

    # ==========================================================
    # RESET
    # ==========================================================

    def reset(self):

        self._set_not_detected()

    # ==========================================================
    # DEBUG
    # ==========================================================

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

            frame_center_x = (
                width / 2.0
            )

            frame_center_y = (
                height / 2.0
            )

            # ==================================================
            # DRAW ALL DETECTED QR
            # ==================================================

            all_qr = state.get(
                "all_qr",
                []
            )

            for qr in all_qr:

                points = qr.get(
                    "points"
                )

                if points is None:

                    continue

                points_int = (
                    points.astype(int)
                )

                # --------------------------------------------------
                # VALID / INVALID COLOR
                # --------------------------------------------------

                if qr.get("allowed"):

                    color = (
                        0,
                        255,
                        0
                    )

                else:

                    color = (
                        0,
                        0,
                        255
                    )

                # --------------------------------------------------
                # BOUNDARY
                # --------------------------------------------------

                for i in range(4):

                    cv2.line(

                        frame,

                        tuple(
                            points_int[i]
                        ),

                        tuple(
                            points_int[
                                (i + 1) % 4
                            ]
                        ),

                        color,

                        2

                    )

                # --------------------------------------------------
                # CENTER
                # --------------------------------------------------

                x = int(
                    qr["center_x"]
                )

                y = int(
                    qr["center_y"]
                )

                cv2.circle(

                    frame,

                    (
                        x,
                        y
                    ),

                    6,

                    color,

                    -1

                )

                # --------------------------------------------------
                # QR NAME
                # --------------------------------------------------

                if qr["data"]:

                    qr_text = (
                        f"QR: {qr['data']}"
                    )

                else:

                    qr_text = (
                        "QR: decode failed"
                    )

                cv2.putText(

                    frame,

                    qr_text,

                    (
                        x + 12,
                        y - 12
                    ),

                    cv2.FONT_HERSHEY_SIMPLEX,

                    0.6,

                    color,

                    2

                )

                # --------------------------------------------------
                # INVALID QR LABEL
                # --------------------------------------------------

                if not qr.get(
                    "allowed"
                ):

                    cv2.putText(

                        frame,

                        "IGNORED",

                        (
                            x + 12,
                            y + 15
                        ),

                        cv2.FONT_HERSHEY_SIMPLEX,

                        0.5,

                        (
                            0,
                            0,
                            255
                        ),

                        2

                    )

            # ==================================================
            # SELECTED QR
            # ==================================================

            center_x = (
                state.get(
                    "center_x"
                )
            )

            center_y = (
                state.get(
                    "center_y"
                )
            )

            selected_data = (
                state.get(
                    "data"
                )
            )

            if (
                center_x is not None
                and center_y is not None
                and selected_data is not None
            ):

                x = int(
                    center_x
                )

                y = int(
                    center_y
                )

                cv2.circle(

                    frame,

                    (
                        x,
                        y
                    ),

                    12,

                    (
                        255,
                        0,
                        0
                    ),

                    3

                )

                cv2.putText(

                    frame,

                    "SELECTED",

                    (
                        x + 15,
                        y + 40
                    ),

                    cv2.FONT_HERSHEY_SIMPLEX,

                    0.6,

                    (
                        255,
                        0,
                        0
                    ),

                    2

                )

            # ==================================================
            # GLOBAL FOCUS
            # ==================================================

            focus_point = (
                self._get_focus_point(
                    selected_data,
                    frame
                )
            )

            if focus_point is None:

                focus_x = (
                    frame_center_x
                )

                focus_y = (
                    frame_center_y
                )

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

                (
                    left,
                    top
                ),

                (
                    right,
                    bottom
                ),

                (
                    255,
                    255,
                    0
                ),

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

                (
                    255,
                    255,
                    0
                ),

                -1

            )

            # ==================================================
            # FOCUS TEXT
            # ==================================================

            cv2.putText(

                frame,

                (
                    f"FOCUS "
                    f"({int(focus_x)}, "
                    f"{int(focus_y)}) "
                    f"TOL={int(tolerance)}"
                ),

                (
                    max(
                        5,
                        left
                    ),
                    max(
                        25,
                        top - 10
                    )
                ),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.6,

                (
                    255,
                    255,
                    0
                ),

                2

            )

            # ==================================================
            # SELECTED QR DISTANCE
            # ==================================================

            if (
                center_x is not None
                and center_y is not None
            ):

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

                status = (
                    "IN FOCUS"
                    if inside
                    else "OUT OF FOCUS"
                )

                cv2.putText(

                    frame,

                    (
                        f"{status} "
                        f"diff=("
                        f"{diff_x:.0f},"
                        f"{diff_y:.0f}) "
                        f"d={distance:.0f}"
                    ),

                    (
                        20,
                        30
                    ),

                    cv2.FONT_HERSHEY_SIMPLEX,

                    0.65,

                    (
                        0,
                        255,
                        0
                    ),

                    2

                )

            else:

                cv2.putText(

                    frame,

                    "NO VALID QR",

                    (
                        20,
                        30
                    ),

                    cv2.FONT_HERSHEY_SIMPLEX,

                    0.65,

                    (
                        0,
                        0,
                        255
                    ),

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

                (
                    255,
                    255,
                    255
                ),

                2

            )

        except (
            IndexError,
            ValueError,
            TypeError
        ):

            pass

        return frame