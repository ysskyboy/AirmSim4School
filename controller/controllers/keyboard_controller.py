from threading import Thread
import keyboard
import time
from ..base_controller import DroneController

class KeyboardController(DroneController):
    def __init__(self, panel, client, vehicle_name):
        super().__init__(panel, client, vehicle_name)
        self.control_thread = Thread(target=self._keyboard_control_loop, daemon=True)
        self.setup_keyboard_bindings()
        self.control_thread.start()
        
    def setup_keyboard_bindings(self):
        """设置键盘快捷键"""
        keyboard.on_press_key('t', lambda _: self.panel.on_takeoff())
        keyboard.on_press_key('l', lambda _: self.panel.on_land())
        keyboard.on_press_key('h', lambda _: self.panel.on_return_home())
        
    def _keyboard_control_loop(self):
        """键盘控制循环"""
        while self.running:
            vx = vy = vz = yaw = 0
            
            if keyboard.is_pressed('w'): vx = self.vehicle_velocity
            if keyboard.is_pressed('s'): vx = -self.vehicle_velocity
            if keyboard.is_pressed('a'): vy = -self.vehicle_velocity
            if keyboard.is_pressed('d'): vy = self.vehicle_velocity
            if keyboard.is_pressed('q'): vz = -self.vehicle_velocity
            if keyboard.is_pressed('e'): vz = self.vehicle_velocity
            if keyboard.is_pressed('left'): yaw = -self.vehicle_yaw_rate
            if keyboard.is_pressed('right'): yaw = self.vehicle_yaw_rate
            
            # Speed boost when holding shift
            if keyboard.is_pressed('shift'):
                vx *= self.speedup_ratio
                vy *= self.speedup_ratio
                vz *= self.speedup_ratio
                
            if any([vx, vy, vz, yaw]):
                self.move_drone(vx, vy, vz, yaw)
                
            time.sleep(self.command_interval)

    def cleanup(self):
        """清理资源"""
        self.running = False
        self.control_thread.join()
