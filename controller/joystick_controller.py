from base_controller import DroneController
import pygame
import threading
import time
import airsim

class JoystickController(DroneController):
    def __init__(self, panel, client, vehicle_name):
        super().__init__(panel, client, vehicle_name)
        pygame.init()
        pygame.joystick.init()
        
        # 初始化RC控制器
        if pygame.joystick.get_count() == 0:
            self.panel.log("未检测到RC控制器!")
            return
        
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        self.panel.log(f"已连接RC控制器: {self.joystick.get_name()}")
        self.panel.log(f"轴数量: {self.joystick.get_numaxes()}")
        self.panel.log(f"按钮数量: {self.joystick.get_numbuttons()}")

        # 修改轴映射以匹配RC模拟器的实际输出
        num_axes = self.joystick.get_numaxes()
        self.axis_map = {
            'yaw': 0,       # 方向 - 轴0
            'throttle': 2,  # 油门 - 轴2
            'pitch': 1,     # 升降 - 轴1
            'roll': 3,      # 加速 - 轴3
            'trim': 4       # 微调 - 轴4
        }

        # 输出映射关系作为调试信息
        self.panel.log("\n当前轴映射关系:")
        self.panel.log("轴0 -> 方向(偏航)")
        self.panel.log("轴1 -> 油门")
        self.panel.log("轴2 -> 升降(俯仰)")
        self.panel.log("轴3 -> 加速(横滚)")
        self.panel.log("轴4 -> 微调")
        
        # 添加校准参数
        self.calibrated = False  # 添加校准状态标志
        self.center_threshold = 0.5    # 增大中心位置容差
        self.deadzone = 0.2           # 增大死区范围
        self.center_positions = [0.0] * num_axes  # 初始化中心位置
        
        # 打印初始状态
        self.debug_axes_state()
        
        # 执行校准
        self.calibrate_axes()
        self.wait_for_center_position()
        
        # 按钮相关的初始化
        max_buttons = self.joystick.get_numbuttons()
        self.button_map = {
            'takeoff': 0,
            'land': 1,
            'return': 2,
            'speedup': 3
        }
        
        # 按钮和状态跟踪
        self.button_states = {i: {'pressed': False, 'handled': False} for i in range(max_buttons)}
        self.takeoff_state = False
        self.last_button_time = time.time()
        self.button_cooldown = 0.5
        
        # 控制参数
        self.vehicle_velocity = 5.0
        self.vehicle_yaw_rate = 3.0
        self.speedup_ratio = 2.0
        self.running = True

        # 日志输出映射信息
        self.panel.log("\n按钮映射:")
        for action, button in self.button_map.items():
            self.panel.log(f"- {action}: 按钮{button}")
        
        self.panel.log("\n轴映射:")
        for action, axis in self.axis_map.items():
            self.panel.log(f"- {action}: 轴{axis}")
        
        # 确保在初始化时启用API控制
        try:
            self.client.enableApiControl(True, vehicle_name=self.vehicle_name)
            self.client.armDisarm(True, vehicle_name=self.vehicle_name)
            self.panel.log("RC控制器初始化完成，已启用API控制")
        except Exception as e:
            self.panel.log(f"API控制启用失败: {str(e)}")

        # 启动控制循环
        self.control_thread = threading.Thread(target=self.control_loop, daemon=True)
        self.control_thread.start()

    def debug_axes_state(self):
        """打印所有轴的当前状态"""
        pygame.event.pump()
        debug_info = "\n当前所有轴的状态:"
        for i in range(self.joystick.get_numaxes()):
            value = self.joystick.get_axis(i)
            debug_info += f"\n轴 {i}: {value:>6.3f}"
            if i in self.axis_map.values():
                for name, axis_id in self.axis_map.items():
                    if axis_id == i:
                        debug_info += f" ({name})"
        self.panel.log(debug_info)

    def wait_for_center_position(self):
        """等待所有摇杆回到中心位置"""
        self.panel.log("\n开始校准流程...")
        self.debug_axes_state()  # 打印初始状态
        
        # 校准前的延迟，确保读数稳定
        time.sleep(1.0)
        
        # 读取当前位置作为中心位置
        pygame.event.pump()
        self.center_positions = []
        for i in range(self.joystick.get_numaxes()):
            center_pos = self.joystick.get_axis(i)
            self.center_positions.append(center_pos)
        
        # 打印中心位置
        debug_info = "\n记录的中心位置:"
        for i, pos in enumerate(self.center_positions):
            debug_info += f"\n轴 {i}: {pos:>6.3f}"
            if i in self.axis_map.values():
                for name, axis_id in self.axis_map.items():
                    if axis_id == i:
                        debug_info += f" ({name})"
        self.panel.log(debug_info)
        
        # 直接设置校准状态为完成
        self.calibrated = True
        self.panel.log("校准完成")

    def calibrate_axes(self):
        """校准摇杆，记录中心位置"""
        pygame.event.pump()
        self.center_positions = []
        
        # 读取每个轴的初始位置作为中心点
        for i in range(self.joystick.get_numaxes()):
            initial_pos = self.joystick.get_axis(i)
            self.center_positions.append(initial_pos)
            self.panel.log(f"轴 {i} 中心位置: {initial_pos:.2f}")
        
        self.panel.log("摇杆校准完成")
        
        # 打印当前所有轴的值，用于调试
        debug_info = "\n当前轴状态:"
        for axis_name, axis_id in self.axis_map.items():
            value = self.joystick.get_axis(axis_id)
            debug_info += f"\n{axis_name}: {value:>6.2f} [轴{axis_id}]"
        self.panel.log(debug_info)

    def apply_deadzone(self, value, axis_index):
        """应用死区和校准"""
        # 获取该轴的中心位置
        center = self.center_positions[axis_index]
        
        # 减去中心偏移
        value = value - center
        
        # 应用死区，使用更大的死区值
        if abs(value) < self.deadzone:
            return 0.0
        
        # 将死区外的值重新映射到整个范围，使用平滑过渡
        sign = 1.0 if value > 0 else -1.0
        scaled_value = sign * (abs(value) - self.deadzone) / (1 - self.deadzone)
        
        # 限制在-1到1的范围内，并应用平滑曲线
        scaled_value = max(-1.0, min(1.0, scaled_value))
        return scaled_value * abs(scaled_value)  # 使用平方关系使控制更平滑

    def control_loop(self):
        """RC控制器主循环"""
        last_command_time = time.time()
        last_debug_time = 0
        debug_interval = 1.0  # 每秒打印一次调试信息

        while self.running:
            try:
                # if not self.calibrated:  # 注释掉这个检查
                #     time.sleep(0.1)
                #     continue
                    
                current_time = time.time()
                pygame.event.pump()
                
                # 读取轴的值并调整符号（调整油门方向）
                yaw = -self.apply_deadzone(self.joystick.get_axis(self.axis_map['yaw']), self.axis_map['yaw'])
                throttle = -self.apply_deadzone(self.joystick.get_axis(self.axis_map['throttle']), self.axis_map['throttle'])  # 移除负号
                pitch = self.apply_deadzone(self.joystick.get_axis(self.axis_map['pitch']), self.axis_map['pitch'])
                roll = -self.apply_deadzone(self.joystick.get_axis(self.axis_map['roll']), self.axis_map['roll'])
                
                # 定期打印遥感信号调试信息，添加原始值
                if current_time - last_debug_time > debug_interval:
                    debug_info = (
                        f"\n遥感信号(处理后/原始值):"
                        f"\n方向(Yaw): {yaw:>6.2f} / {self.joystick.get_axis(self.axis_map['yaw']):>6.2f} [轴{self.axis_map['yaw']}]"
                        f"\n油门(Throttle): {throttle:>6.2f} / {self.joystick.get_axis(self.axis_map['throttle']):>6.2f} [轴{self.axis_map['throttle']}]"
                        f"\n升降(Pitch): {pitch:>6.2f} / {self.joystick.get_axis(self.axis_map['pitch']):>6.2f} [轴{self.axis_map['pitch']}]"
                        f"\n加速(Roll): {roll:>6.2f} / {self.joystick.get_axis(self.axis_map['roll']):>6.2f} [轴{self.axis_map['roll']}]"
                        f"\n微调(Trim): {self.joystick.get_axis(self.axis_map['trim']):>6.2f} [轴{self.axis_map['trim']}]"
                    )
                    self.panel.log(debug_info)
                    last_debug_time = current_time

                # 使用微调轴作为加速控制
                trim = self.joystick.get_axis(self.axis_map['trim'])
                scale_ratio = 1.0 + (self.speedup_ratio - 1.0) * ((trim + 1) / 2)

                # 应用控制值
                velocity_x = pitch * scale_ratio * self.vehicle_velocity    # 前后移动
                velocity_y = roll * scale_ratio * self.vehicle_velocity     # 左右移动
                velocity_z = throttle * scale_ratio * self.vehicle_velocity # 上下移动
                yaw_rate = yaw * scale_ratio * self.vehicle_yaw_rate       # 偏航控制

                # 检查按钮事件并处理起飞/降落
                current_time = time.time()
                if current_time - self.last_button_time >= self.button_cooldown:
                    for button_id in range(self.joystick.get_numbuttons()):
                        current_state = bool(self.joystick.get_button(button_id))
                        button_info = self.button_states[button_id]
                        
                        if current_state:  # 按钮被按下
                            if not button_info['pressed']:  # 按钮刚被按下
                                button_info['pressed'] = True
                                if not button_info['handled']:  # 尚未处理过这次按下
                                    self.panel.log(f"按钮 {button_id} 被按下")
                                    if (button_id == self.button_map.get('takeoff')):
                                        if not self.takeoff_state:
                                            self.panel.log("执行起飞指令...")
                                            try:
                                                self.client.enableApiControl(True, vehicle_name=self.vehicle_name)
                                                self.client.armDisarm(True, vehicle_name=self.vehicle_name)
                                                self.client.takeoffAsync(vehicle_name=self.vehicle_name).join()
                                                self.takeoff_state = True
                                                self.panel.log("起飞完成")
                                            except Exception as e:
                                                self.panel.log(f"起飞失败: {str(e)}")
                                        else:
                                            self.panel.log("执行降落指令...")
                                            try:
                                                self.client.landAsync(vehicle_name=self.vehicle_name).join()
                                                self.takeoff_state = False
                                                self.panel.log("降落完成")
                                            except Exception as e:
                                                self.panel.log(f"降落失败: {str(e)}")
                                        button_info['handled'] = True
                                        self.last_button_time = current_time
                        else:  # 按钮被释放
                            if button_info['pressed']:  # 之前是按下状态
                                button_info['pressed'] = False
                                button_info['handled'] = False  # 重置处理状态
                                self.panel.log(f"按钮 {button_id} 被释放")

                # 仅在起飞状态下发送移动命令
                if self.takeoff_state and any([abs(x) > 0.01 for x in [velocity_x, velocity_y, velocity_z, yaw_rate]]):
                    try:
                        self.client.moveByVelocityAsync(
                            velocity_x,
                            velocity_y,
                            velocity_z,
                            duration=0.1,
                            drivetrain=airsim.DrivetrainType.MaxDegreeOfFreedom,
                            yaw_mode=airsim.YawMode(is_rate=True, yaw_or_rate=yaw_rate),
                            vehicle_name=self.vehicle_name
                        ).join()
                    except Exception as e:
                        self.panel.log(f"移动命令执行失败: {str(e)}")
                        
                time.sleep(0.02)  # 控制更新频率

            except Exception as e:
                self.panel.log(f"RC控制错误: {str(e)}")
                time.sleep(0.1)

    def move_drone(self, vx, vy, vz, yaw_rate):
        """执行无人机移动命令"""
        try:
            if self.takeoff_state:  # 只在起飞状态时执行移动命令
                self.client.moveByVelocityAsync(
                    vx, vy, vz,
                    duration=0.02,
                    drivetrain=airsim.DrivetrainType.MaxDegreeOfFreedom,
                    yaw_mode=airsim.YawMode(is_rate=True, yaw_or_rate=yaw_rate),
                    vehicle_name=self.vehicle_name
                ).join()
        except Exception as e:
            self.panel.log(f"移动命令执行失败: {str(e)}")

    def cleanup(self):
        """清理资源"""
        self.running = False
        pygame.quit()
