# AirSim Drone Teaching Simulation

## 项目简介
本项目是基于 AirSim 模拟器开发的无人机教学仿真系统，支持键盘和遥控器控制无人机飞行。

## 系统要求
- Windows 10 或更高版本
- Python 3.8 或更高版本
- AirSim 模拟器环境

## 安装步骤

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 下载 AirSim 环境
- 从 [AirSim Releases](https://github.com/microsoft/AirSim/releases) 下载最新版本
- 解压到任意目录

## 使用说明

### 1. 启动 AirSim 环境
- 运行解压目录中的 `run.bat` 或 `AirSimDroneRacingLab.exe -windowed`

### 2. 运行仿真程序
```bash
python controller/main.py
```

### 3. 控制方式

#### 键盘控制
- W/S: 上升/下降
- A/D: 左右旋转
- 方向键: 前后左右移动
- 空格: 临时加速
- ESC: 退出程序

#### 遥控器控制
- 支持标准 RC 遥控器
- 插入遥控器后自动识别

## 项目结构
```
AirmSim4School/
├── controller/         # 控制器代码
│   ├── main.py        # 主程序入口
│   ├── base_controller.py   # 基础控制器
│   └── joystick_controller.py  # 遥控器控制
├── tests/             # 测试代码
└── requirements.txt   # 项目依赖
```

## 常见问题

### 1. 找不到遥控器
- 检查遥控器是否正确连接
- 确认驱动程序已正确安装

### 2. AirSim 连接失败
- 确保 AirSim 环境已正常运行
- 检查 settings.json 配置是否正确

## 贡献指南
欢迎提交 Issue 和 Pull Request 来改进项目。

## 许可证
MIT License
