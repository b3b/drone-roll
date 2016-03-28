package org.kivy.ble;

import java.util.List;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothGattService;
import android.bluetooth.BluetoothGattCharacteristic;

interface PythonBluetooth
{
        public void on_device(BluetoothDevice device, int rssi, byte[] record);
        public void on_scan_completed();
        public void on_services(List<BluetoothGattService> services);
        public void on_characteristic_changed(BluetoothGattCharacteristic characteristic);
}
