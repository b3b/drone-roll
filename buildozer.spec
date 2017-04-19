[app]
title = Drone Roll
version = 1.0
package.name = droneroll
package.domain = org.kivy

source.dir = .
source.include_exts = py,png,jpg,kv,atlas
p4a.local_recipes = recipes

android.permissions = BLUETOOTH, BLUETOOTH_ADMIN, ACCESS_COARSE_LOCATION

# android.private_storage = False

requirements = hostpython2,kivy,android,able

orientation = landscape
fullscreen = 1

[buildozer]
warn_on_root = 1
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2
