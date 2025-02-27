import airsim

class DroneController:
    def __init__(self, panel, client, vehicle_name):
        self.panel = panel
        self.client = client
        self.vehicle_name = vehicle_name
        self.running = True
        
        # 控制参数
        self.vehicle_velocity = 2.0
        self.vehicle_yaw_rate = 5.0
        self.speedup_ratio = 10.0
        self.command_interval = 0.05

    def move_drone(self, velocity_x, velocity_y, velocity_z, yaw_rate, duration=0.05):
        """控制无人机移动"""
        try:
            self.client.moveByVelocityAsync(
                velocity_x,
                velocity_y, 
                velocity_z,
                duration=duration,
                drivetrain=airsim.DrivetrainType.MaxDegreeOfFreedom,
                yaw_mode=airsim.YawMode(is_rate=True, yaw_or_rate=yaw_rate),
                vehicle_name=self.vehicle_name
            )
        except Exception as e:
            self.panel.log(f"移动控制错误: {str(e)}")
