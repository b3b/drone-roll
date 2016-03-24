package org.kivy.ble;

import org.renpy.android.PythonActivity;
import android.util.Log;
import android.content.Intent;
import android.content.Context;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothManager;
import android.bluetooth.BluetoothDevice;
import android.os.Handler;

import org.kivy.ble.PythonBluetooth;

public class BLE {
        private String TAG = "BLE for Kivy";
        private PythonBluetooth mPython;
        private Context mContext;
        private BluetoothAdapter mBluetoothAdapter;
        private Handler mHandler;
        private boolean mScanning;

        public BLE(PythonBluetooth python) {
                mPython = python;
                mContext = (Context) PythonActivity.mActivity;

                final BluetoothManager bluetoothManager =
                        (BluetoothManager) mContext.getSystemService(Context.BLUETOOTH_SERVICE);
                mBluetoothAdapter = bluetoothManager.getAdapter();
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
 }
