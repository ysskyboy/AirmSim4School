import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import keyboard  # 添加这个导入

class BaseDronePanel:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("无人机控制面板")
        self.root.geometry("500x150")
        self.root.attributes('-topmost', True)
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建日志框架
        self.log_frame = ttk.LabelFrame(self.main_frame, text="执行日志")
        self.log_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建日志文本区域
        self.log_text = tk.Text(self.log_frame, height=6, state='disabled')
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def log(self, message):
        """添加日志消息"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, f"[{current_time}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state='disabled')

    def on_takeoff(self, target_height=-3):
        try:
            self.log("正在解锁无人机...")
            self.client.enableApiControl(True, vehicle_name=self.vehicle_name)
            self.client.armDisarm(True, vehicle_name=self.vehicle_name)
            
            self.log("执行起飞...")
            self.client.takeoffAsync(vehicle_name=self.vehicle_name).join()
            
            self.log(f"上升到目标高度 {abs(target_height)}m...")
            self.client.moveToZAsync(target_height, 1, vehicle_name=self.vehicle_name).join()
            
            self.log("起飞完成")
        except Exception as e:
            self.log(f"起飞失败: {str(e)}")

    def on_land(self):
        self.log("执行降落指令")
        self.client.landAsync(vehicle_name=self.vehicle_name).join()

    def on_return_home(self):
        self.log("返回起点...")
        self.client.goHomeAsync(vehicle_name=self.vehicle_name)

    def on_exit(self):
        """退出程序"""
        self.log("正在退出程序...")
        self.root.after(1000, self.root.quit)

    def switch_scene(self, scene_name):
        """切换场景"""
        self.log(f"正在切换到场景: {scene_name}")
        try:
            self.client.simLoadLevel(scene_name)
            self.log(f"场景切换成功")
        except Exception as e:
            self.log(f"场景切换失败: {str(e)}")

    def switch_view(self, view_type):
        """切换相机视角"""
        try:
            if view_type == "fpv":
                camera_pose = airsim.Pose(airsim.Vector3r(0, 0, 0), airsim.to_quaternion(0, 0, 0))
                self.client.simSetVehiclePose(camera_pose, True, self.vehicle_name)
                self.log("切换到第一人称视角")
            elif view_type == "third":
                current_pose = self.client.simGetVehiclePose(self.vehicle_name)
                camera_pose = airsim.Pose(
                    airsim.Vector3r(current_pose.position.x_val - 5,
                                  current_pose.position.y_val,
                                  current_pose.position.z_val - 2),
                    airsim.to_quaternion(0, -0.2, 0)
                )
                self.client.simSetVehiclePose(camera_pose, True, self.vehicle_name)
                self.log("切换到第三人称视角")
            elif view_type == "follow":
                current_pose = self.client.simGetVehiclePose(self.vehicle_name)
                camera_pose = airsim.Pose(
                    airsim.Vector3r(current_pose.position.x_val - 8,
                                  current_pose.position.y_val,
                                  current_pose.position.z_val - 3),
                    airsim.to_quaternion(0, -0.15, 0)
                )
                self.client.simSetVehiclePose(camera_pose, True, self.vehicle_name)
                self.log("切换到跟随视角")
            elif view_type == "ground":
                current_pose = self.client.simGetVehiclePose(self.vehicle_name)
                camera_pose = airsim.Pose(
                    airsim.Vector3r(current_pose.position.x_val,
                                  current_pose.position.y_val,
                                  current_pose.position.z_val + 20),
                    airsim.to_quaternion(-0.4, 0, 0)
                )
                self.client.simSetVehiclePose(camera_pose, True, self.vehicle_name)
                self.log("切换到地面观察视角")
        except Exception as e:
            self.log(f"视角切换失败: {str(e)}")

    def simulate_key(self, key):
        """模拟按键事件"""
        self.log(f"执行快捷键: {key}")
        if key:
            keyboard.press_and_release(key)

    def toggle_debug_report(self):
        """切换调试报告"""
        self.log("切换调试报告显示")
        # 实现调试报告的显示/隐藏逻辑

    def show_keyboard_shortcuts(self):
        """显示键盘快捷键说明"""
        shortcuts = """快捷键说明:
视图控制:
  F - 第一人称视角
  B - 跟随视角
  空格 - 观察者视角
  M - 手动相机控制

显示控制:
  F1 - 帮助信息
  F3 - 线框模式
  F10 - 天气选项
  0-3 - 切换各种窗口
  T - 切换轨迹线

操作控制:
  R - 开始/停止录制
  Backspace - 重置所有

移动控制:
  W/S - 俯仰控制
  A/D - 偏航控制
  方向键 - 平移控制
  PgUp/PgDn - 上升/下降
"""
        messagebox.showinfo("键盘快捷键", shortcuts)

    def set_weather(self, weather_type, intensity):
        """设置天气状态"""
        try:
            self.log(f"正在设置天气: {weather_type}, 强度: {intensity}")
            weather_params = {
                "rain": ["Rain"],
                "fog": ["Fog"],
                "cloud": ["Clouds"]
            }
            self.reset_weather()
            if weather_type in weather_params:
                for param in weather_params[weather_type]:
                    self.client.simSetWeatherParameter(getattr(airsim.WeatherParameter, param), intensity)
                if weather_type == "rain":
                    self.client.simSetWeatherParameter(airsim.WeatherParameter.Roadwetness, intensity)
            self.log("天气设置成功")
        except Exception as e:
            self.log(f"天气设置失败: {str(e)}")

    def reset_weather(self):
        """重置天气到晴天"""
        try:
            self.log("正在重置天气...")
            weather_params = ["Rain", "Fog", "Clouds", "Roadwetness"]
            for param in weather_params:
                try:
                    self.client.simSetWeatherParameter(getattr(airsim.WeatherParameter, param), 0)
                except:
                    continue
            self.log("天气已重置为晴天")
        except Exception as e:
            self.log(f"天气重置失败: {str(e)}")
