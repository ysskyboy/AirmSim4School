import tkinter as tk
from tkinter import ttk, messagebox
from drone_base import BaseDronePanel
from keyboard_controller import KeyboardController
from joystick_controller import JoystickController  # 修改导入路径
import keyboard
import pygame
import airsim
from datetime import datetime

class DroneControlPanel(BaseDronePanel):
    def __init__(self):
        super().__init__()
        
        # 创建菜单栏
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # 创建各种菜单
        self._create_flight_menu()
        self._create_scene_menu()
        self._create_view_menu()
        self._create_display_menu()
        self._create_control_menu()
        self._create_help_menu()
        self._create_weather_menu()
        self._create_rc_menu()
        
        # 初始化控制器相关变量
        self.rc_controller = None
        self.client = None
        self.vehicle_name = None
        self.pygame_initialized = False  # 添加变量跟踪pygame状态
        
    def _create_flight_menu(self):
        self.flight_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="飞行控制", menu=self.flight_menu)
        self.flight_menu.add_command(label="起飞(3m)", command=lambda: self.on_takeoff(-3))
        self.flight_menu.add_command(label="起飞(5m)", command=lambda: self.on_takeoff(-5))
        self.flight_menu.add_command(label="起飞(10m)", command=lambda: self.on_takeoff(-10))
        self.flight_menu.add_separator()
        self.flight_menu.add_command(label="降落", command=self.on_land)
        self.flight_menu.add_separator()
        self.flight_menu.add_command(label="返回起点", command=self.on_return_home)
        self.flight_menu.add_separator()
        self.flight_menu.add_command(label="退出", command=self.on_exit)

    def _create_scene_menu(self):
        self.scene_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="场景控制", menu=self.scene_menu)
        self.scenes = {
            "张家界": "ZhangJiaJie_Medium",
            "预选赛场地1": "Qualifier_Tier_1",
            "预选赛场地2": "Qualifier_Tier_2",
            "预选赛场地3": "Qualifier_Tier_3",
            "决赛场地1": "Final_Tier_1",
            "决赛场地2": "Final_Tier_2",
            "决赛场地3": "Final_Tier_3",
            "足球场(简单)": "Soccer_Field_Easy",
            "足球场(中等)": "Soccer_Field_Medium",
            "99号建筑(困难)": "Building99_Hard"
        }
        for scene_name, scene_id in self.scenes.items():
            self.scene_menu.add_command(
                label=scene_name, 
                command=lambda id=scene_id: self.switch_scene(id)
            )

    def _create_view_menu(self):
        self.view_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="视角控制", menu=self.view_menu)
        self.view_menu.add_command(label="第一人称视角", command=lambda: self.switch_view("fpv"))
        self.view_menu.add_command(label="第三人称视角", command=lambda: self.switch_view("third"))
        self.view_menu.add_command(label="跟随视角", command=lambda: self.switch_view("follow"))
        self.view_menu.add_command(label="地面观察视角", command=lambda: self.switch_view("ground"))

    def _create_display_menu(self):
        self.display_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="显示控制", menu=self.display_menu)
        self.display_menu.add_command(label="帮助信息 (F1)", command=lambda: self.simulate_key('f1'))
        self.display_menu.add_command(label="线框模式 (F3)", command=lambda: self.simulate_key('f3'))
        self.display_menu.add_command(label="天气选项 (F10)", command=lambda: self.simulate_key('f10'))
        self.display_menu.add_separator()
        self.display_menu.add_command(label="切换所有子窗口 (0)", command=lambda: self.simulate_key('0'))
        self.display_menu.add_command(label="切换深度窗口 (1)", command=lambda: self.simulate_key('1'))
        self.display_menu.add_command(label="切换分割窗口 (2)", command=lambda: self.simulate_key('2'))
        self.display_menu.add_command(label="切换场景窗口 (3)", command=lambda: self.simulate_key('3'))
        self.display_menu.add_separator()
        self.display_menu.add_command(label="切换轨迹线 (T)", command=lambda: self.simulate_key('t'))
        self.display_menu.add_command(label="调试报告", command=self.toggle_debug_report)

    def _create_control_menu(self):
        self.control_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="操作控制", menu=self.control_menu)
        self.control_menu.add_command(label="开始/停止录制 (R)", command=lambda: self.simulate_key('r'))
        self.control_menu.add_command(label="重置所有 (Backspace)", command=lambda: self.simulate_key('backspace'))

    def _create_help_menu(self):
        self.help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="帮助", menu=self.help_menu)
        self.help_menu.add_command(label="键盘快捷键", command=self.show_keyboard_shortcuts)

    def _create_weather_menu(self):
        self.weather_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="天气控制", menu=self.weather_menu)
        
        self.rain_menu = tk.Menu(self.weather_menu, tearoff=0)
        self.weather_menu.add_cascade(label="雨天", menu=self.rain_menu)
        self.rain_menu.add_command(label="小雨", command=lambda: self.set_weather("rain", 0.3))
        self.rain_menu.add_command(label="中雨", command=lambda: self.set_weather("rain", 0.6))
        self.rain_menu.add_command(label="大雨", command=lambda: self.set_weather("rain", 0.9))
        
        self.fog_menu = tk.Menu(self.weather_menu, tearoff=0)
        self.weather_menu.add_cascade(label="雾天", menu=self.fog_menu)
        self.fog_menu.add_command(label="轻雾", command=lambda: self.set_weather("fog", 0.3))
        self.fog_menu.add_command(label="浓雾", command=lambda: self.set_weather("fog", 0.7))
        
        self.weather_menu.add_command(label="晴天", command=self.reset_weather)
        self.weather_menu.add_command(label="多云", command=lambda: self.set_weather("cloud", 0.5))
        self.weather_menu.add_command(label="夜晚", command=lambda: self.set_weather("night", 0.8))

    def _create_rc_menu(self):
        self.rc_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="RC控制器", menu=self.rc_menu)
        self.rc_menu.add_command(label="连接RC控制器", command=self.connect_rc_controller)

    def connect_rc_controller(self):
        """连接RC控制器"""
        try:
            if self.rc_controller is None:
                self.log("正在连接RC控制器...")
                # 初始化pygame
                if not self.pygame_initialized:
                    pygame.quit()  # 确保清理之前的pygame实例
                    pygame.init()
                    pygame.joystick.quit()
                    pygame.joystick.init()
                    self.pygame_initialized = True
                
                # 使用正确的JoystickController类
                self.rc_controller = JoystickController(self, self.client, self.vehicle_name)
                if pygame.joystick.get_count() > 0:
                    self.rc_menu.entryconfig("连接RC控制器", label="断开RC控制器")
            else:
                self.log("正在断开RC控制器...")
                self.rc_controller.running = False
                self.rc_controller = None
                pygame.joystick.quit()
                pygame.quit()
                self.pygame_initialized = False
                self.rc_menu.entryconfig("断开RC控制器", label="连接RC控制器")
        except Exception as e:
            self.log(f"RC控制器操作失败: {str(e)}")
            # 出错时确保清理
            if self.rc_controller:
                self.rc_controller.running = False
                self.rc_controller = None
            if self.pygame_initialized:
                pygame.joystick.quit()
                pygame.quit()
                self.pygame_initialized = False

    def init_controllers(self):
        """初始化控制器"""
        self.keyboard_controller = KeyboardController(self, self.client, self.vehicle_name)
