from openrazer.client import DeviceManager
import time
import subprocess
from datetime import datetime as dt
import datetime


class mouse:
    def __init__(self):
        # Replace with your device name(s) https://github.com/openrazer/openrazer#mice
        # NOTE: Only one device is supported right now. Some devices have multiple names
        self.mouse_names = [
            "Razer DeathAdder V3 Pro (Wireless)",
            "Razer DeathAdder V3 Pro (Wired)",
        ]

        try:
            self.device_manager = DeviceManager()
        except:
            pass

        self.is_charging = False
        self.battery_level = -1
        self.exists = False
        self.name = "Not Found"
        self.device_found = False
        self.initialized = True

    def check_device(self):
        try:
            print(self.device_manager.devices)
            self.device_manager = DeviceManager()
            for device in self.device_manager.devices:
                if device.name in self.mouse_names:
                    self.name = device.name
                    self.battery_level = device.battery_level
                    self.exists = True
                    self.is_charging = device.is_charging
                    self.device_found = True
                    if "(Wired)" in device.name:
                        return
            return
        except:
            pass

        self.__init__()


class notification:
    def __init__(self, recall=False):
        self.mouse_found = False
        self.battery_level = -1
        self.is_charging = False
        self.mouse_name = ""
        # don't reset values when called within class
        self.charging_notified = recall
        self.initial_log = recall
        self.message = ""
        self.frame_color = "#3bfc38"

    def send(self, message=None):
        self.message = message or f"Battery: {self.battery_level}%"

        if message:
            self.message += f" <b>({self.battery_level}%)</b>"
        elif self.is_charging:
            if self.charging_notified:
                return
            self.message = f"Charging: {self.battery_level}%"
        elif self.battery_level == 100:
            self.message = f"Fully Charged"

        if self.mouse_found:
            subprocess.Popen(
                [
                    "notify-send",
                    "-h",
                    f"string:hlcolor:{self.frame_color}",
                    "-h",
                    f"string:frcolor:{self.frame_color}",
                    "-h",
                    f"int:value:{self.battery_level}",
                    self.mouse_name,
                    self.message,
                ]
            )

        self.__init__(True)


def future_date():
    now = dt.now()
    return now + datetime.timedelta(minutes=30)


usb = mouse()
notify = notification()

log_lock: dict[int, dt] = {
    1: dt.now(),
    5: dt.now(),
    10: dt.now(),
    20: dt.now(),
    50: dt.now(),
}

while True:
    time.sleep(2)
    usb.check_device()

    # Reset when device disconnects
    if not usb.exists:
        log_lock = {
            1: dt.now(),
            5: dt.now(),
            10: dt.now(),
            20: dt.now(),
            50: dt.now(),
        }

    notify.battery_level = usb.battery_level
    notify.is_charging = usb.is_charging
    notify.mouse_found = usb.exists
    notify.mouse_name = usb.name

    # NOTE: Logging
    # print(f"Name: {notify.mouse_name or None}")
    # print(f"Charge Notified: {notify.charging_notified}")

    if not usb.exists:
        notify.__init__()
        continue

    # NOTE: Logging
    # if usb.is_charging:
    #     print(f"Is Charging: {usb.is_charging}")

    if usb.is_charging and not notify.charging_notified:
        notify.send()

    if not usb.is_charging:
        notify.charging_notified = False

    match usb.battery_level:
        case 1:
            if log_lock[1] < dt.now():
                notify.frame_color = "#ff0000"
                log_lock[1] = future_date()
                notify.send(f"\nBruh")
        case 5:
            if log_lock[5] < dt.now():
                notify.frame_color = "#fa2323"
                log_lock[5] = future_date()
                notify.send(f"\nYou gonna feed my dog ass?")
        case 10:
            if log_lock[10] < dt.now():
                notify.frame_color = "#f55742"
                log_lock[10] = future_date()
                notify.send("\nFeed me")
        case 20:
            if log_lock[20] < dt.now():
                notify.frame_color = "#f57e42"
                log_lock[20] = future_date()
                notify.send("\nDon't forget i exist")
        case 50:
            if log_lock[50] < dt.now():
                notify.frame_color = "#f5e642"
                log_lock[50] = future_date()
                notify.send("\nYou're clean")

    if not notify.initial_log:
        notify.send()
        continue
