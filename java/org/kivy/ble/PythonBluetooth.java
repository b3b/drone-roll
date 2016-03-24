package org.kivy.ble;

import android.bluetooth.BluetoothDevice;

interface PythonBluetooth
{
        public void on_device(BluetoothDevice device, int rssi, byte[] record);
        public void on_scan_completed();
}
