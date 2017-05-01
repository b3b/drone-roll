from kivy.event import EventDispatcher
from kivy.utils import platform

from .drone import DroneBehavior


__all__ = ('Drone',)


if platform == 'android':
    from .android import Drone
else:
    class Drone(DroneBehavior, EventDispatcher):

        def discover(self):
            pass
