import arsdk
from able import GATT_SUCCESS, Advertisement, BluetoothDispatcher
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.properties import ObjectProperty

from .drone import DroneBehavior


class Drone(DroneBehavior, BluetoothDispatcher):

    ble_device = ObjectProperty(None)

    identity = bytearray([
        0x43, 0x00,  # Parrot Bluetooth ID
        0xcf, 0x19,  # Parrot USB ID
        0x00, 0x09   # Rolling Spider USB Product ID
    ])

    def discover(self):
        self.start_scan()
        self.state = 'scan'

    def on_device(self, device, rssi, advertisement):
        if self.state != 'scan':
            return
        Logger.debug("on_device event {}".format(list(advertisement)))
        drone_found = False
        name = ''
        for ad in advertisement:
            if ad.ad_type == Advertisement.ad_types.manufacturer_specific_data:
                if ad.data.startswith(self.identity):
                    drone_found = True
                else:
                    break
            elif ad.ad_type == Advertisement.ad_types.complete_local_name:
                name = str(ad.data)
        if drone_found:
            self.state = 'found'
            self.ble_device = device
            Logger.debug("Drone detected: {}".format(name))
            self.stop_scan()

    def on_scan_completed(self):
        if self.ble_device:
            self.connect_gatt(self.ble_device)

    def on_connection_state_change(self, status, state):
        if status == GATT_SUCCESS and state:
            self.discover_services()
        else:
            self.alert_characteristic = None
            self.close_gatt()
            self.services = None

    def on_services(self, status, services):
        self.services = services
        for short_uuid in arsdk.Characteristic.receive_ids.values():
            characteristic = self.services.search(short_uuid)
            self.enable_notifications(characteristic)

        self.wheels_on()
        Clock.schedule_once(self.emergency, 7)
        Clock.schedule_once(self.flat_trim, 1)
        # Clock.schedule_once(self.take_off, 2)

    def on_characteristic_changed(self, characteristic):
        uuid = characteristic.getUuid().toString()
        data = characteristic.getValue()
        Logger.debug("Characteristic {} changed value: {}".format(
            uuid, str(data).encode('hex')))
        packet = arsdk.Packet.unpack(data)
        Logger.debug("Characteristic {} changed decoded: {}".format(
            uuid, packet))
