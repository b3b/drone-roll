from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.config import Config
from kivy.utils import platform
from kivy.uix.boxlayout import BoxLayout
from drone import Drone

Config.set('kivy', 'log_level', 'debug')


if platform == 'android':
    from android.runnable import run_on_ui_thread
else:

    def run_on_ui_thread(f):
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)

        return wrapper


class MainLayout(BoxLayout):
    pass

class DroneApp(App):

    def build(self):
        return MainLayout()

    def on_start(self):
        Clock.schedule_once(self.init, 0)

    def on_pause(self):
        return True

    def on_resume(self):
        if not self.drone.state:
            self.disvover_drone()

    @run_on_ui_thread
    def init(self, *args, **kwargs):
        self.drone = Drone()
        self.discover_drone()

    def on_activity_result(self, request_code, result_code, intent):
        fmt = "on_activity_result request_code={}, result_code={}"
        Logger.debug(fmt.format(request_code, result_code))

    @run_on_ui_thread
    def discover_drone(self):
        self.drone.discover()


if __name__ == '__main__':
    DroneApp().run()
