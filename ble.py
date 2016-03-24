from kivy.logger import Logger
from kivy.event import EventDispatcher
from jnius import autoclass, PythonJavaClass, java_method

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

