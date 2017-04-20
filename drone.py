from collections import defaultdict, namedtuple
from itertools import count

import arsdk
from able import GATT_SUCCESS, Advertisement, BluetoothDispatcher
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.properties import ObjectProperty, StringProperty


CommandData = namedtuple('CommandData', ['number', 'characteristic', 'data'])


class Drone(BluetoothDispatcher):

    state = StringProperty()
    ble_device = ObjectProperty(None)

    identity = bytearray([
        0x43, 0x00,  # Parrot Bluetooth ID
        0xcf, 0x19,  # Parrot USB ID
        0x00, 0x09   # Rolling Spider USB Product ID
    ])

    sequences = defaultdict(lambda: count(1))
    command_number = count(1)

    def start_scan(self):
        super(Drone, self).start_scan()
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
        Clock.schedule_once(self.emergency, 5)
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
        self.write_characteristic(command.characteristic, command.data)
        Logger.debug("Write command<{n}>".format(n=command.number))

    def wheels_on(self, *args):
        self.write_command('SpeedSettings', 'Wheels', arguments=[1])

    def flat_trim(self, *args):
        self.write_command('Piloting', 'FlatTrim')

    def take_off(self, *args):
        self.write_command('Piloting', 'TakeOff')

    def emergency(self, *args):
        self.write_command('Piloting', 'Emergency', buffer_name='emergency')
