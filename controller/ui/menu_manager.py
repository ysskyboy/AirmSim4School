import tkinter as tk
from tkinter import ttk, messagebox

class MenuManager:
    def __init__(self, root, panel):
        self.root = root
        self.panel = panel
        self.create_menus()
        
    def create_menus(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 控制菜单
        control_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="控制", menu=control_menu)
        control_menu.add_command(label="起飞 (T)", command=self.panel.on_takeoff)
        control_menu.add_command(label="降落 (L)", command=self.panel.on_land)
        control_menu.add_command(label="返航 (H)", command=self.panel.on_return_home)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)
        
    def show_about(self):
        """显示关于对话框"""
        messagebox.showinfo("关于", 
            "AirSim Drone Controller\n"
            "使用方法：\n"
            "WSAD - 前后左右移动\n"
            "QE - 上升/下降\n"
            "方向键 - 旋转\n"
            "Shift - 加速\n"
            "T - 起飞\n"
            "L - 降落\n"
            "H - 返航")
