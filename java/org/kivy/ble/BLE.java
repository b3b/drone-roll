package org.kivy.ble;

import org.renpy.android.PythonActivity;
import android.util.Log;
import android.content.Intent;
import android.content.Context;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothManager;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothProfile;
import android.bluetooth.BluetoothGatt;
import android.bluetooth.BluetoothGattCallback;
import android.bluetooth.BluetoothGattCharacteristic;
import android.os.Handler;

import org.kivy.ble.PythonBluetooth;

public class BLE {
        private String TAG = "BLE for Kivy";
        private PythonBluetooth mPython;
        private Context mContext;
        private BluetoothAdapter mBluetoothAdapter;
        private BluetoothGatt mBluetoothGatt;
        private Handler mHandler;
        private boolean mScanning;

        public BLE(PythonBluetooth python) {
                mPython = python;
                mContext = (Context) PythonActivity.mActivity;
                mBluetoothGatt = null;

                final BluetoothManager bluetoothManager =
                        (BluetoothManager) mContext.getSystemService(Context.BLUETOOTH_SERVICE);
                mBluetoothAdapter = bluetoothManager.getAdapter();
        }

        public BluetoothGatt getGatt() {
                return mBluetoothGatt;
        }

        public Boolean startScan(long scanPeriod, int requestEnableBtCode) {
                Log.d(TAG, "startScan for period:" + scanPeriod);
                mHandler = new Handler();

                if (mBluetoothAdapter == null || !mBluetoothAdapter.isEnabled()) {
                        Intent enableBtIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
                        PythonActivity.mActivity.startActivityForResult(enableBtIntent, requestEnableBtCode);
                        return false;
                }
                scanLeDevice(scanPeriod);
                return true;
        }

        public void stopScan() {
                if (mScanning == true) {
                        Log.d(TAG, "stopScan");
                        mScanning = false;
                        mBluetoothAdapter.stopLeScan(mLeScanCallback);
                        mPython.on_scan_completed();
                }
        }

        private void scanLeDevice(long scanPeriod) {
                mHandler.postDelayed(new Runnable() {
                                @Override
                                public void run() {
                                        Log.d(TAG, "scan time over");
                                        stopScan();
                                }
                        }, scanPeriod);
                mScanning = true;
                mBluetoothAdapter.startLeScan(mLeScanCallback);
        }

        private BluetoothAdapter.LeScanCallback mLeScanCallback =
                new BluetoothAdapter.LeScanCallback() {
                        @Override
                        public void onLeScan(final BluetoothDevice device, final int rssi, final byte[] scanRecord) {
                                PythonActivity.mActivity.runOnUiThread(new Runnable() {
                                                @Override
                                                public void run() {
                                                        mPython.on_device(device, rssi, scanRecord);
                                                }
                                        });
                        }
                };

        public void connectGatt(BluetoothDevice device) {
                Log.d(TAG, "connectGatt");
                if (mBluetoothGatt == null) {
                        mBluetoothGatt = device.connectGatt(mContext, false, mGattCallback);
                }
        }

        public void closeGatt() {
                Log.d(TAG, "closeGatt");
                if (mBluetoothGatt != null) {
                        mBluetoothGatt.close();
                        mBluetoothGatt = null;
                }
        }

        private final BluetoothGattCallback mGattCallback =
                new BluetoothGattCallback() {
                        @Override
                        public void onConnectionStateChange(BluetoothGatt gatt, int status, int newState) {
                                if (newState == BluetoothProfile.STATE_CONNECTED) {
                                        Log.d(TAG, "Connected to GATT server");
                                        mBluetoothGatt.discoverServices();
                                } else if (newState == BluetoothProfile.STATE_DISCONNECTED) {
                                        Log.d(TAG, "Disconnected from GATT server");
                                }
                        }

                        @Override
                        public void onServicesDiscovered(BluetoothGatt gatt, int status) {
                                if (status == BluetoothGatt.GATT_SUCCESS) {
                                        Log.d(TAG, "onServicesDiscovered - success");
                                        mPython.on_services(mBluetoothGatt.getServices());
                                } else {
                                        Log.d(TAG, "onServicesDiscovered status:" + status);
                                }
                        }

                        @Override
                        public void onCharacteristicChanged(BluetoothGatt gatt,
                                                            BluetoothGattCharacteristic characteristic) {
                                Log.d(TAG, "onCharacteristicChanged");
                                mPython.on_characteristic_changed(characteristic);
                        }
                };

        public boolean writeCharacteristic(BluetoothGattCharacteristic characteristic, byte[] data) {
                if (characteristic.setValue(data)) {
                        return mBluetoothGatt.writeCharacteristic(characteristic);
                }
                return false;
        }

        public boolean writeCharacteristicNoResponse(BluetoothGattCharacteristic characteristic, byte[] data) {
                if (characteristic.setValue(data)) {
                        characteristic.setWriteType(BluetoothGattCharacteristic.WRITE_TYPE_NO_RESPONSE);
                        return mBluetoothGatt.writeCharacteristic(characteristic);
                }
                return false;
        }
}
