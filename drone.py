from kivy.logger import Logger
from kivy.utils import platform
from kivy.properties import StringProperty, ObjectProperty
from jnius import autoclass
from ble import BluetoothLowEnergy, Advertisement
import arsdk

if platform == 'android':
    BluetoothGattDescriptor = autoclass('android.bluetooth.BluetoothGattDescriptor')
    UUID = autoclass('java.util.UUID')

class EnableNotificatiosException(Exception):
    pass

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

    def on_services(self, services):
        self.services = services
        for name in ['battery']:
            short_uuid = arsdk.characteristic_ids[name]
            try:
                self.enable_notifications(short_uuid)
            except EnableNotificatiosException, e:
                Logger.exception("Error enabling notifications: {}".format(': '.join(e.args)))
            else:
                Logger.debug("Notifications enabled: {}".format(short_uuid))

    def enable_notifications(self, short_uuid):
        characteristic = self.services.search(short_uuid)
        if not characteristic:
            raise EnableNotificatiosException(short_uuid, "can't find characteristic")

        gatt = self._ble.getGatt()
        if not gatt:
            raise EnableNotificatiosException(short_uuid, "can't get GATT")

        if not gatt.setCharacteristicNotification(characteristic, True):
            raise EnableNotificatiosException(short_uuid, "can't enable notifications")

        #descriptors = characteristic.getDescriptors().toArray()
        #if descriptors and (len(descriptors) == 1):
        #    descriptor = descriptors[0]

        descriptor = characteristic.getDescriptor(UUID.fromString(arsdk.UPDATE_NOTIFICATION_DESCRIPTOR_UUID))
        if not descriptor:
            raise EnableNotificatiosException(short_uuid, "can't find descriptor")

        if not descriptor.setValue(BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE):
            raise EnableNotificatiosException(short_uuid, "can't set ENABLE_NOTIFICATION_VALUE")

        if not gatt.writeDescriptor(descriptor):
            raise EnableNotificatiosException(short_uuid, "can't write descriptor")

    def on_characteristic_changed(self, characteristic):
        uuid = characteristic.getUuid().toString()
        data = characteristic.getValue()
        Logger.debug("Characteristic {} changed value: {}".format(uuid, str(data).encode('hex')))
        packet = arsdk.Packet.unpack(data)
        Logger.debug("Characteristic {} changed decoded: {}".format(packet))
