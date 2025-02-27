import keyboard
import threading
import time
import airsim
import queue
import logging

class KeyboardController:
    def __init__(self, control_panel, airsim_client, vehicle_name):
        self.panel = control_panel
        self.client = airsim_client
        self.vehicle_name = vehicle_name
        
        # 控制参数
        self.vehicle_velocity = 2.0
        self.vehicle_yaw_rate = 5.0
        self.speedup_ratio = 10.0
        self.running = True
        self.max_angle = 0.1  # 最大倾角(弧度)
        
        # 添加命令队列
        self.command_queue = queue.Queue()
        
        # 启动控制循环
        self.control_thread = threading.Thread(target=self.control_loop, daemon=True)
        self.control_thread.start()
        
        logging.basicConfig(level=logging.DEBUG)
        self.check_client_connection()
        
    def check_client_connection(self):
        """检查AirSim客户端连接"""
        try:
            self.client.confirmConnection()
            logging.debug("AirSim client connected successfully.")
        except Exception as e:
            logging.error(f"AirSim client connection failed: {str(e)}")
            self.panel.log(f"AirSim client connection failed: {str(e)}")

    def control_loop(self):
        """键盘控制循环"""
        last_command_time = 0
        min_command_interval = 0.02  # 最小命令间隔(秒)
        
        while self.running:
            try:
                current_time = time.time()
                if current_time - last_command_time < min_command_interval:
                    time.sleep(0.001)  # 短暂休眠以避免CPU过载
                    continue
                    
                roll = 0.0    # 横滚角
                pitch = 0.0   # 俯仰角
                yaw_rate = 0.0  # 偏航角速率
                velocity_z = 0.0  # 初始化垂直速度
                
                # 检测加速键
                scale_ratio = self.speedup_ratio if keyboard.is_pressed('space') else 1.0
                
                # 偏航控制 (A/D)
                if keyboard.is_pressed('a') or keyboard.is_pressed('d'):
                    yaw_rate = -(keyboard.is_pressed('d') - keyboard.is_pressed('a')) * scale_ratio * self.vehicle_yaw_rate
                
                # 前后控制 (UP/DOWN) - 俯仰
                if keyboard.is_pressed('up') or keyboard.is_pressed('down'):
                    pitch = (keyboard.is_pressed('up') - keyboard.is_pressed('down')) * scale_ratio * self.max_angle
                
                # 左右控制 (LEFT/RIGHT) - 横滚
                if keyboard.is_pressed('left') or keyboard.is_pressed('right'):
                    roll = -(keyboard.is_pressed('right') - keyboard.is_pressed('left')) * scale_ratio * self.max_angle
                
                # 上下控制 (W/S) - 高度控制
                if keyboard.is_pressed('w') or keyboard.is_pressed('s'):
                    velocity_z = -(keyboard.is_pressed('w') - keyboard.is_pressed('s')) * scale_ratio * self.vehicle_velocity
                
                # 仅在有实际输入时发送命令
                # 分别处理高度控制和姿态控制
                if abs(velocity_z) > 0.01:  # 处理高度控制
                    try:
                        self.client.moveByVelocityAsync(
                            0,  # x速度为0
                            0,  # y速度为0
                            velocity_z,
                            duration=min_command_interval,
                            vehicle_name=self.vehicle_name
                        ).join()
                        last_command_time = current_time
                    except Exception as e:
                        self.panel.log(f"高度控制失败: {str(e)}")
                        logging.error(f"高度控制失败: {str(e)}")

                if any([abs(x) > 0.01 for x in [roll, pitch, yaw_rate]]):  # 处理姿态控制
                    try:
                        current_z = self.client.getMultirotorState(vehicle_name=self.vehicle_name).kinematics_estimated.position.z_val
                        self.client.moveByRollPitchYawrateZAsync(
                            roll,
                            pitch,
                            yaw_rate,
                            current_z,  # 保持当前高度
                            duration=min_command_interval,
                            vehicle_name=self.vehicle_name
                        ).join()
                        last_command_time = current_time
                    except Exception as e:
                        self.panel.log(f"姿态控制失败: {str(e)}")
                        logging.error(f"姿态控制失败: {str(e)}")
                
                # 检测退出
                if keyboard.is_pressed('esc'):
                    self.panel.root.quit()
                    break
                    
            except Exception as e:
                self.panel.log(f"键盘控制错误: {str(e)}")
                time.sleep(1)  # 错误发生时等待一段时间
                
            time.sleep(0.001)  # 避免过度占用CPU

    def __del__(self):
        """清理资源"""
        self.running = False
        if hasattr(self, 'control_thread'):
            self.control_thread.join(timeout=1.0)
