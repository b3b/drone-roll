from kivy.logger import Logger
from kivy.properties import StringProperty, ObjectProperty
from ble import BluetoothLowEnergy, Advertisement

class Drone(BluetoothLowEnergy):

    state = StringProperty()
    device = ObjectProperty(None)

    identity = bytearray([
        0x43, 0x00, # Parrot Bluetooth ID
        0xcf, 0x19, # Parrot USB ID
        0x00, 0x09  # Rolling Spider USB Product ID
    ])

    def start_scan(self, period):
        started = super(Drone, self).start_scan(period)
        if started:
            self.state = 'scan'
            return True
        return False

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
            self.device = device
            Logger.debug("Drone detected: {}".format(name))
            self.stop_scan()

    def on_scan_completed(self):
        if self.device:
            self.connect_gatt(self.device)
