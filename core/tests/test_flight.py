import time

from core.bridge.hula_bridge import HulaBridge


# ==========================================================
# TEST CONFIG
# ==========================================================

DISTANCE = 50
SPEED = 50


# ==========================================================
# MAIN
# ==========================================================

def main():

    print()
    print("========================================")
    print("       PAYLOAD CARRIER")
    print("          FLIGHT TEST")
    print("========================================")

    bridge = HulaBridge()

    try:

        # ==================================================
        # CONNECT
        # ==================================================

        print()
        print("[1] CONNECT")

        if not bridge.connect():

            print("Connection failed")

            return

        print("[OK] Connected")

        # ==================================================
        # TAKE OFF
        # ==================================================

        print()
        print("========================================")
        print("TAKEOFF")
        print("========================================")

        result = bridge.take_off()

        print(
            "TAKEOFF returned:",
            result
        )

        if not result:

            print("TAKEOFF FAILED")

            return

        time.sleep(2)

        # ==================================================
        # FORWARD
        # ==================================================

        print()
        print("========================================")
        print("FORWARD 50 CM")
        print("========================================")

        result = bridge.forward(
            DISTANCE,
            SPEED
        )

        print(
            "FORWARD returned:",
            result
        )

        if not result:

            print("FORWARD FAILED")

            print("Emergency landing...")

            bridge.landing()

            return

        time.sleep(1)

        # ==================================================
        # BACKWARD
        # ==================================================

        print()
        print("========================================")
        print("BACKWARD 50 CM")
        print("========================================")

        result = bridge.backward(
            DISTANCE,
            SPEED
        )

        print(
            "BACKWARD returned:",
            result
        )

        if not result:

            print("BACKWARD FAILED")

            print("Emergency landing...")

            bridge.landing()

            return

        time.sleep(1)

        # ==================================================
        # LEFT
        # ==================================================

        print()
        print("========================================")
        print("LEFT 50 CM")
        print("========================================")

        result = bridge.left(
            DISTANCE,
            SPEED
        )

        print(
            "LEFT returned:",
            result
        )

        if not result:

            print("LEFT FAILED")

            print("Emergency landing...")

            bridge.landing()

            return

        time.sleep(1)

        # ==================================================
        # RIGHT
        # ==================================================

        print()
        print("========================================")
        print("RIGHT 50 CM")
        print("========================================")

        result = bridge.right(
            DISTANCE,
            SPEED
        )

        print(
            "RIGHT returned:",
            result
        )

        if not result:

            print("RIGHT FAILED")

            print("Emergency landing...")

            bridge.landing()

            return

        time.sleep(1)

        # ==================================================
        # LAND
        # ==================================================

        print()
        print("========================================")
        print("LAND")
        print("========================================")

        result = bridge.landing()

        print(
            "LAND returned:",
            result
        )

        # ==================================================
        # COMPLETE
        # ==================================================

        print()
        print("========================================")
        print("       FLIGHT TEST COMPLETE")
        print("========================================")

    except KeyboardInterrupt:

        print()
        print("Ctrl+C detected")

        try:

            bridge.landing()

        except Exception:

            pass

    except Exception as e:

        print()
        print("TEST ERROR:")
        print(e)

        try:

            bridge.landing()

        except Exception:

            pass


if __name__ == "__main__":

    main()