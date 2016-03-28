data_types = {
    'ack': 1,
    'data': 2,
    'low_latency_data': 3,
    'data_with_ack': 4
}
data_type_names = {v:k for k, v in data_types.items()}

characteristic_ids = {
    'non_ack': 'fa0a',
    'ack': 'fa0b',
    'emergency': 'fa0c',
    'battery': 'fb0f'
}


# list is not complete
projects = {
    'common': {
        'project_id': 0,
        'classes': {
            'CommonState': {
                'class_id': 5,
                'commands': (
                    "AllStatesChanged", "BatteryStateChanged",
                    "MassStorageStateListChanged", "MassStorageInfoStateListChanged",
                    "CurrentDateChanged", "CurrentTimeChanged",
                    "MassStorageInfoRemainingListChanged", "WifiSignalChanged",
                    "SensorsStatesListChanged", "ProductModel",
                    "CountryListKnown"
                )
            }
        },
    },
    'mini_drone': {
        'project_id': 2,
        'classes': {
            'Piloting': {
                'class_id': 0,
                'commands': (
                    'FlatTrim', 'TakeOff',
                    'PCMD', 'Landing',
                    'Emergency', 'AutoTakeOffMode')
            },
            "SpeedSettings": {
                'class_id': 1,
                'commands': (
                    'MaxVerticalSpeed', 'MaxRotationSpeed',
                    'Wheels', 'MaxHorizontalSpeed',
                )
            },
        }
    },
}

project_names = {v['project_id']:k for k,v in projects.items()}
command_classes_names = {(v['project_id'], vv['class_id']):kk
                         for k,v in projects.items()
                         for kk,vv in v['classes'].items()}
command_names = {(v['project_id'], vv['class_id'], vv['commands'].index(cmd)):cmd
                 for k,v in projects.items()
                 for kk,vv in v['classes'].items()
                 for cmd in vv['commands']}

UPDATE_NOTIFICATION_DESCRIPTOR_UUID = "00002902-0000-1000-8000-00805f9b34fb"
