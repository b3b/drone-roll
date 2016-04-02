from kivy.logger import Logger
from kivy.utils import platform
from kivy.properties import StringProperty, ObjectProperty
from kivy.clock import Clock
from jnius import autoclass
from ble import BluetoothLowEnergy, Advertisement
from collections import defaultdict, namedtuple
from itertools import count
import arsdk

if platform == 'android':
    BluetoothGattDescriptor = autoclass('android.bluetooth.BluetoothGattDescriptor')
    UUID = autoclass('java.util.UUID')

CommandData = namedtuple('CommandData', ['number', 'characteristic', 'data'])

class EnableNotificatiosException(Exception):
    pass

class Drone(BluetoothLowEnergy):

    state = StringProperty()
    ble_device = ObjectProperty(None)

    identity = bytearray([
        0x43, 0x00, # Parrot Bluetooth ID
        0xcf, 0x19, # Parrot USB ID
        0x00, 0x09  # Rolling Spider USB Product ID
    ])

    sequences = defaultdict(lambda: count(1))
    command_number = count(1)

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
            self.ble_device = device
            Logger.debug("Drone detected: {}".format(name))
            self.stop_scan()

    def on_scan_completed(self):
        if self.ble_device:
            self.connect_gatt(self.ble_device)

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

        self.wheels_on()
        Clock.schedule_once(self.emergency, 5)
        Clock.schedule_once(self.flat_trim, 1)
        #Clock.schedule_once(self.take_off, 2)

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
        Logger.debug("Characteristic {} changed decoded: {}".format(uuid, packet))

    def construct_command(self, class_name, command_name,
                          data_type='data', buffer_name='ack',
                          project_name='mini_drone', arguments=None):
        data_type = arsdk.data_types[data_type]
        buffer_id = arsdk.characteristic_ids[buffer_name]
        sequence_number = 255 & self.sequences[buffer_id].next()

        command_class = arsdk.projects[project_name]['classes'][class_name]
        project_id = arsdk.projects[project_name]['project_id']
        class_id = command_class['class_id']
        command_id = command_class['commands'].index(command_name)
        packet = arsdk.Packet(data_type, sequence_number,
                              project_id, class_id, command_id, arguments)
        characteristic = self.services.search(buffer_id)
        command_number = self.command_number.next()
        Logger.debug("Command<{n}> constructed: {packet}".format(
            n=command_number, packet=packet))
        return CommandData(command_number, characteristic, packet.pack())

    def write_command(self, *args, **kwargs):
        command = self.construct_command(*args, **kwargs)
        result = self._ble.writeCharacteristic(command.characteristic, command.data)
        Logger.debug("Write command<{n}> result: {result}".format(
            n=command.number, result=result))
        return result

    def wheels_on(self, *args):
        self.write_command('SpeedSettings', 'Wheels', arguments=[1])

    def flat_trim(self, *args):
        self.write_command('Piloting', 'FlatTrim')

    def take_off(self, *args):
        self.write_command('Piloting', 'TakeOff')

    def emergency(self, *args):
        self.write_command('Piloting', 'Emergency', buffer_name='emergency')
