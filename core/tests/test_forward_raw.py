import time
import pyhula


def main():

    print()
    print("========================================")
    print("       RAW FORWARD TEST")
    print("========================================")

    print()
    print("[1] Creating Hula API...")

    api = pyhula.UserApi()

    print("[2] Connecting...")

    if not api.connect():

        print("Connection failed")

        return

    print("[OK] Connected")

    # ==================================================
    # TAKEOFF
    # ==================================================

    print()
    print("========================================")
    print("TAKEOFF")
    print("========================================")

    result = api.single_fly_takeoff()

    print("TAKEOFF returned:", result)

    if not result:

        print("TAKEOFF FAILED")

        return

    time.sleep(2)

    # ==================================================
    # FORWARD
    # ==================================================

    print()
    print("========================================")
    print("BACK 50 CM")
    print("========================================")

    print("BEFORE single_fly_back")

    result = api.single_fly_back(
        50,
        50
    )

    print("AFTER single_fly_back")
    print("single_fly_back returned:", result)

    # ==================================================
    # LAND
    # ==================================================

    print()
    print("========================================")
    print("LAND")
    print("========================================")

    result = api.single_fly_touchdown()

    print("LAND returned:", result)

    print()
    print("========================================")
    print("TEST COMPLETE")
    print("========================================")


if __name__ == "__main__":

    main()