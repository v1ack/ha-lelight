import time
from threading import Thread

from bluezero import advertisement
from bluezero.broadcaster import Beacon

from .encoder import Command, Encryptor, Message


class LeBeacon(Beacon):
    def start_beacon(self):
        if not self.dongle.powered:
            self.dongle.powered = True
        ad_manager = advertisement.AdvertisingManager(self.dongle.address)
        ad_manager.register_advertisement(self.broadcaster, {})

        thread = Thread(target=self.broadcaster.start)
        thread.start()
        time.sleep(0.5)

        self.broadcaster.stop()
        ad_manager.unregister_advertisement(self.broadcaster)


class App:
    def __init__(self, mac: str):
        _mac = list(
            map(
                lambda x: int.from_bytes(x, "big", signed=True),
                map(
                    lambda x: x.to_bytes(1, "little", signed=False),
                    bytearray.fromhex(mac),
                ),
            )
        )
        self.encryptor = Encryptor(_mac)
        self.beacon = LeBeacon()

    def _make_message(self, command: Command) -> Message:
        return self.encryptor.message(command)

    def _ble_send(self, msg: Message):
        self.beacon.add_manufacturer_data(msg.manufacturer_id, msg.manufacturer_data)

        for _ in range(2):
            self.beacon.start_beacon()

    def send(self, command: Command):
        # Send commands twice
        self._ble_send(self._make_message(command))
        self._ble_send(self._make_message(command))
