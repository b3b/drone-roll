from kivy.logger import Logger
from kivy.properties import StringProperty
from ble import BluetoothLowEnergy

class Drone(BluetoothLowEnergy):

    state = StringProperty()

    def start_scan(self, period):
        started = super(Drone, self).start_scan(period)
        if started:
            self.state = 'scan'
            return True
        return False
