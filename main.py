from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.config import Config
from android import activity
from android.runnable import run_on_ui_thread
from kivy.uix.boxlayout import BoxLayout
from drone import Drone

Config.set('kivy', 'log_level', 'debug')

class MainLayout(BoxLayout):
    pass

class DroneApp(App):

    def build(self):
        activity.bind(on_activity_result=self.on_activity_result)
        return MainLayout()

    def on_start(self):
        Clock.schedule_once(self.init, 0)

    def on_pause(self):
        return True

    def on_resume(self):
        if not self.drone.state:
            self.start_scan()

    @run_on_ui_thread
    def init(self, *args, **kwargs):
        self.drone = Drone()
        self.start_scan()

    def on_activity_result(self, request_code, result_code, intent):
        fmt = "on_activity_result request_code={}, result_code={}"
        Logger.debug(fmt.format(request_code, result_code))

    @run_on_ui_thread
    def start_scan(self):
        self.drone.start_scan()


if __name__ == '__main__':
    DroneApp().run()
