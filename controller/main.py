import sys
import time
import airsim
import keyboard
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime
from drone_base import BaseDronePanel
import pygame  # 添加pygame导入
from gui_panel import DroneControlPanel
from joystick_controller import JoystickController

# 初始化joystick_controller变量
joystick_controller = None

class JoystickController:
    def __init__(self, control_panel, airsim_client, vehicle_name):
        
        self.panel = control_panel
        self.client = airsim_client
        self.vehicle_name = vehicle_name
        
        # 检查RC控制器
        if pygame.joystick.get_count() == 0:
            self.panel.log("未检测到RC控制器!")
            return
        
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        self.panel.log(f"已连接RC控制器: {self.joystick.get_name()}")
        self.panel.log(f"轴数量: {self.joystick.get_numaxes()}")
        self.panel.log(f"按钮数量: {self.joystick.get_numbuttons()}")

        # 修改控制参数
        self.vehicle_velocity = 5.0    # 基础速度提高一些
        self.vehicle_yaw_rate = 3.0    # 降低偏航速率使控制更平滑
        self.speedup_ratio = 2.0       # 降低加速倍率
        self.running = True
        
        # 添加按键状态跟踪
        self.takeoff_state = False
        
        # 启动控制循环
        self.control_thread = threading.Thread(target=self.control_loop, daemon=True)
        self.control_thread.start()

    # 移除control_loop方法，现在使用joystick_controller.py中的实现

import sys
import airsim
from gui_panel import DroneControlPanel

def main():
    # AirSim settings
    global AirSim_client, vehicle_name
    vehicle_name = "Drone"
    AirSim_client = airsim.MultirotorClient()
    AirSim_client.confirmConnection()
    AirSim_client.enableApiControl(True, vehicle_name=vehicle_name)
    AirSim_client.armDisarm(True, vehicle_name=vehicle_name)

    # 创建GUI面板
    panel = DroneControlPanel()
    panel.client = AirSim_client
    panel.vehicle_name = vehicle_name
    panel.log("无人机控制系统已启动")
    panel.log("按键说明:")
    panel.log("W/S: 上升/下降")
    panel.log("A/D: 左右旋转")
    panel.log("方向键: 前后左右移动")
    panel.log("空格: 临时加速")
    panel.log("ESC: 退出程序")

    # 初始化键盘控制器
    panel.init_controllers()
    
    # 启动GUI主循环
    panel.root.mainloop()
    sys.exit()

if __name__ == "__main__":
    main()