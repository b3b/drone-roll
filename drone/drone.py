from collections import defaultdict, namedtuple
from itertools import count

import arsdk
from kivy.logger import Logger
from kivy.properties import StringProperty


CommandData = namedtuple('CommandData', ['number', 'characteristic', 'data'])


class DroneBehavior(object):
    state = StringProperty()
    sequences = defaultdict(lambda: count(1))
    command_number = count(1)

    def construct_command(self, class_name, command_name,
                          data_type='data', buffer_name='ack',
                          project_name='mini_drone', arguments=None):
        data_type = arsdk.data_types[data_type]
        buffer_id = arsdk.Characteristic.send_ids[buffer_name]
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
        self.write_command('Piloting', 'Emergency',
                           buffer_name='high_priority')
