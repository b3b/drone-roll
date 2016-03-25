from collections import namedtuple
from kivy.logger import Logger
from kivy.event import EventDispatcher
from jnius import autoclass, PythonJavaClass, java_method
from kivy.utils import platform

if platform == 'android':
    BLE = autoclass('org.kivy.ble.BLE')

class BluetoothEventsListener(PythonJavaClass):
    __javainterfaces__ = ['org.kivy.ble.PythonBluetooth']
    __javacontext__ = 'app'

    def __init__(self):
        super(BluetoothEventsListener, self).__init__()

    @java_method('(Landroid/bluetooth/BluetoothDevice;I[B)V')
    def on_device(self, device, rssi, record):
        Logger.debug("on_device name: {}, signal: {}".format(device.getName(), rssi))

    @java_method('()V')
    def on_scan_completed(self):
        Logger.debug("on_scan_completed")

class BluetoothLowEnergy(EventDispatcher):

    enable_bluetooth_code = 1024

    def __init__(self):
        self._listener = BluetoothEventsListener()
        self._ble = BLE(self._listener)

    def start_scan(self, period):
        return self._ble.startScan(period, self.enable_bluetooth_code)

class Advertisement(object):
    """Advertisement data record parser

    >>> for ad in Advertisement([2, 1, 0x6, 6, 255, 82, 83, 95, 82, 48]):
    ...     ad
    AD(ad_type=1, data=bytearray(b'\\x06'))
    AD(ad_type=255, data=bytearray(b'RS_R0'))
    >>> Advertisement.ad_types.flags
    1
    """

    AD = namedtuple("AD", ['ad_type', 'data'])

    class ad_types:
        # https://www.bluetooth.org/en-us/specification/assigned-numbers/generic-access-profile
        flags = 0x01
        complete_local_name = 0x09
        manufacturer_specific_data = 0xff

    def __init__(self, data):
        self.data = data

    def __iter__(self):
        return Advertisement.parse(self.data)

    @classmethod
    def parse(cls, data):
        pos = 0
        while pos < len(data):
            length = data[pos]
            if length < 2:
                return
            try:
                ad_type = data[pos + 1]
            except IndexError:
                return
            next_pos = pos + length + 1
            if ad_type:
                segment = slice(pos + 2, next_pos)
                yield Advertisement.AD(ad_type, bytearray(data[segment]))
            pos = next_pos
