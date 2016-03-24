[app]
title = Drone Roll
version = 0.0.1
package.name = droneroll
package.domain = org.kivy

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

android.add_src = java
android.permissions = BLUETOOTH, BLUETOOTH_ADMIN

android.private_storage = False

requirements = kivy

orientation = landscape
fullscreen = 1

[buildozer]
warn_on_root = 1
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2
