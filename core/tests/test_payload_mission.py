from core.bridge.hula_bridge import HulaBridge

import config


def main():

    print()
    print("========================================")
    print("     PAYLOAD CARRIER - BRIDGE TEST")
    print("========================================")
    print()

    bridge = HulaBridge()

    # ======================================
    # CONNECT
    # ======================================

    print("[1] Connecting...")

    if not bridge.connect():

        print("Connection failed")

        return

    print("[OK] Connected")

    # ======================================
    # TAKEOFF
    # ======================================

    print()
    print("[2] TAKEOFF")

    result = bridge.takeoff()

    print(
        f"TAKEOFF returned: {result}"
    )

    input(
        "\nPress ENTER after drone is stable..."
    )

    # ======================================
    # FORWARD
    # ======================================

    print()
    print("[3] FORWARD")

    result = bridge.forward(
        config.MOVE_DISTANCE,
        config.FLIGHT_SPEED
    )

    print(
        f"FORWARD returned: {result}"
    )

    input(
        "\nPress ENTER after movement is complete..."
    )

    # ======================================
    # BACK
    # ======================================

    print()
    print("[4] BACK")

    result = bridge.back(
        config.MOVE_DISTANCE,
        config.FLIGHT_SPEED
    )

    print(
        f"BACK returned: {result}"
    )

    input(
        "\nPress ENTER before landing..."
    )

    # ======================================
    # LAND
    # ======================================

    print()
    print("[5] LAND")

    result = bridge.land()

    print(
        f"LAND returned: {result}"
    )

    print()
    print("========================================")
    print("TEST COMPLETE")
    print("========================================")


if __name__ == "__main__":

    main()