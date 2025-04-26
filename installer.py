import os
import sys
import tkinter as tk
import threading
import urllib.request
import zipfile
import shutil
import subprocess
import socket
import random
import time
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

# 全局变量
DEFAULT_INSTALL_PATH = os.path.join(os.path.expanduser("~"), "马牛逼代码助手")
DOWNLOAD_URL = "https://install.imwzr.top/open/zip.zip"
APP_NAME = "马牛逼代码助手"
APP_VERSION = "1.0.0"

# 许可协议内容
LICENSE_CONTENT = """#  许可协议

## "马牛逼代码助手"软件许可协议

本许可协议（"协议"）是您（"用户"或"您"）与"马牛逼代码助手"软件（"软件"）的所有者之间的法律协议。通过安装、复制或以其他方式使用本软件，您同意受本协议条款的约束。如果您不同意本协议的条款，请勿安装或使用本软件。

## 1. 授权

根据本协议的条款和条件，我们授予您非独占的、不可转让的许可，以便在您拥有或控制的设备上安装和使用本软件。

## 2. 限制

您不得：
- 修改、反向工程、反编译或反汇编本软件的任何部分，除非适用法律明确允许此类活动。
- 出租、租赁、出借、转售、再许可或分发本软件。
- 删除或更改本软件上的任何版权、商标或其他专有权利声明。

## 3. 所有权

本软件受版权法和国际版权条约以及其他知识产权法律和条约的保护。本软件是许可使用的，而非出售给您。我们保留所有未明确授予您的权利。

## 4. 免责声明

本软件按"原样"提供，不提供任何明示或暗示的保证，包括但不限于对适销性、特定用途适用性和非侵权性的保证。

## 5. 责任限制

在任何情况下，我们均不对因使用或无法使用本软件而导致的任何特殊的、偶然的、间接的或后果性的损害负责，包括但不限于数据丢失、业务中断或任何其他商业损害或损失。

## 6. 终止

如果您未能遵守本协议的任何条款，本协议将自动终止。终止后，您必须停止使用本软件并销毁本软件的所有副本。

## 7. 适用法律

本协议受中华人民共和国法律管辖并按其解释，不考虑法律冲突原则。

## 8. 完整协议

本协议构成您与我们之间关于本软件的完整协议，并取代所有先前或同时期的口头或书面通信、提议和陈述。

通过安装和使用本软件，您确认已阅读并理解本协议，并同意受其条款的约束。"""

# EULA内容
EULA_CONTENT = """#  "马牛逼代码助手"最终用户许可协议 (EULA)

本最终用户许可协议（"EULA"）是您（"最终用户"）与"马牛逼代码助手"软件（"软件"）提供者之间的法律协议。

## 接受条款

通过安装、复制、下载、访问或以其他方式使用本软件，您同意接受本EULA的条款。如果您不同意本EULA的条款，请勿安装或使用本软件。

## 软件许可

在您遵守本EULA所有条款和条件的前提下，我们授予您以下权利：

1. **安装和使用**：您可以在您拥有或控制的设备上安装和使用本软件的一个副本。

2. **备份副本**：您可以制作一份本软件的备份副本，仅用于存档目的。

## 描述其他权利和限制

1. **禁止反向工程**：您不得对本软件进行反向工程、反编译或反汇编，除非适用法律明确允许此类活动。

2. **组件分离**：本软件是作为单一产品许可的。您不得将其组件分离用于多个设备。

3. **转让**：您不得出租、租赁、出借、转售、分发或再许可本软件。

4. **支持服务**：我们可能会为本软件提供支持服务。支持服务的使用受我们的政策和计划的约束。

5. **合规**：您必须遵守与您使用本软件相关的所有适用法律。

## 第三方软件

本软件可能包含第三方软件组件，这些组件受其各自的许可条款的约束。本EULA不适用于这些组件。

## 数据收集

本软件可能会收集关于您使用本软件的某些数据。我们对这些数据的使用受我们的隐私政策的约束。

## 终止

在不损害任何其他权利的情况下，如果您未能遵守本EULA的条款和条件，我们可能会终止本EULA。在这种情况下，您必须销毁本软件的所有副本及其所有组件。

## 免责声明

本软件按"原样"提供，不提供任何形式的保证，无论是明示的还是暗示的，包括但不限于对适销性、特定用途适用性和非侵权性的保证。

## 责任限制

在任何情况下，我们均不对任何特殊的、偶然的、间接的或后果性的损害负责，包括但不限于利润损失、数据丢失、业务中断或任何其他商业损害或损失。

## 适用法律

本EULA受中华人民共和国法律的约束和解释。

## 完整协议

本EULA构成您与我们之间关于本软件的完整协议，并取代所有先前或同时期的口头或书面通信和提议。

通过安装和使用本软件，您确认已阅读并理解本EULA，并同意受其条款的约束。"""

# 隐私政策内容
PRIVACY_CONTENT = """#  "马牛逼代码助手"隐私政策

本隐私政策描述了"马牛逼代码助手"软件（"软件"）如何收集、使用和共享您的个人信息。我们重视您的隐私，并致力于保护您的个人数据。

## 收集信息
1:软件不会收集您的任何信息到服务器您的信息将完全存储于本地您的信息永远属于您自己
2：软件不会上传任何数据到软件的服务器"""

class InstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} 安装程序")
        self.root.geometry("700x500")
        self.root.resizable(False, False)
        
        # 设置窗口图标（如果有的话）
        # self.root.iconbitmap("icon.ico")
        
        # 初始化变量
        self.install_path = tk.StringVar(value=DEFAULT_INSTALL_PATH)
        self.create_shortcut = tk.BooleanVar(value=True)
        self.progress_var = tk.DoubleVar(value=0.0)
        self.status_text = tk.StringVar(value="准备安装...")
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建不同的页面
        self.pages = {}
        self.current_page = None
        
        self.create_welcome_page()
        self.create_license_page()
        self.create_eula_page()
        self.create_privacy_page()
        self.create_install_page()
        self.create_progress_page()
        self.create_finish_page()
        
        # 显示欢迎页面
        self.show_page("welcome")
    
    def create_welcome_page(self):
        page = ttk.Frame(self.main_frame)
        
        # 欢迎标题
        ttk.Label(page, text=f"欢迎安装 {APP_NAME}", font=("Arial", 16, "bold")).pack(pady=20)
        
        # 欢迎信息
        welcome_text = f"本向导将引导您完成 {APP_NAME} {APP_VERSION} 的安装过程。\n\n"
        welcome_text += "在开始安装之前，请确保您已关闭所有其他应用程序。\n\n"
        welcome_text += "点击\"下一步\"继续安装过程。"
        
        ttk.Label(page, text=welcome_text, wraplength=600, justify="left").pack(pady=20)
        
        # 按钮区域
        btn_frame = ttk.Frame(page)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)
        
        ttk.Button(btn_frame, text="取消", command=self.confirm_exit).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="下一步", command=lambda: self.show_page("license")).pack(side=tk.RIGHT, padx=5)
        
        self.pages["welcome"] = page
    
    def create_license_page(self):
        page = ttk.Frame(self.main_frame)
        
        # 许可标题
        ttk.Label(page, text="许可协议", font=("Arial", 16, "bold")).pack(pady=10)
        ttk.Label(page, text="请仔细阅读以下许可协议。您必须接受协议才能继续安装。", wraplength=600).pack(pady=5)
        
        # 许可文本区域
        license_frame = ttk.Frame(page, borderwidth=1, relief="solid")
        license_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=5)
        
        license_text = tk.Text(license_frame, wrap=tk.WORD, height=15, width=80)
        license_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(license_frame, command=license_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        license_text.config(yscrollcommand=scrollbar.set)
        
        # 使用内置的许可协议文本
        license_content = LICENSE_CONTENT
        
        license_text.insert(tk.END, license_content)
        license_text.config(state="disabled")
        
        # 同意选项
        self.license_agreed = tk.BooleanVar(value=False)
        ttk.Checkbutton(page, text="我接受许可协议中的条款", variable=self.license_agreed).pack(anchor=tk.W, pady=10)
        
        # 按钮区域
        btn_frame = ttk.Frame(page)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="取消", command=self.confirm_exit).pack(side=tk.RIGHT, padx=5)
        self.next_btn_license = ttk.Button(btn_frame, text="下一步", command=lambda: self.show_page("eula"), state="disabled")
        self.next_btn_license.pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="上一步", command=lambda: self.show_page("welcome")).pack(side=tk.RIGHT, padx=5)
        
        # 绑定复选框状态变化
        self.license_agreed.trace("w", self.update_license_next_button)
        
        self.pages["license"] = page
    
    def create_eula_page(self):
        page = ttk.Frame(self.main_frame)
        
        # EULA标题
        ttk.Label(page, text="最终用户许可协议", font=("Arial", 16, "bold")).pack(pady=10)
        ttk.Label(page, text="请仔细阅读以下最终用户许可协议。您必须接受协议才能继续安装。", wraplength=600).pack(pady=5)
        
        # EULA文本区域
        eula_frame = ttk.Frame(page, borderwidth=1, relief="solid")
        eula_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=5)
        
        eula_text = tk.Text(eula_frame, wrap=tk.WORD, height=15, width=80)
        eula_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(eula_frame, command=eula_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        eula_text.config(yscrollcommand=scrollbar.set)
        
        # 使用内置的EULA文本
        eula_content = EULA_CONTENT
        
        eula_text.insert(tk.END, eula_content)
        eula_text.config(state="disabled")
        
        # 同意选项
        self.eula_agreed = tk.BooleanVar(value=False)
        ttk.Checkbutton(page, text="我接受最终用户许可协议中的条款", variable=self.eula_agreed).pack(anchor=tk.W, pady=10)
        
        # 按钮区域
        btn_frame = ttk.Frame(page)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="取消", command=self.confirm_exit).pack(side=tk.RIGHT, padx=5)
        self.next_btn_eula = ttk.Button(btn_frame, text="下一步", command=lambda: self.show_page("privacy"), state="disabled")
        self.next_btn_eula.pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="上一步", command=lambda: self.show_page("license")).pack(side=tk.RIGHT, padx=5)
        
        # 绑定复选框状态变化
        self.eula_agreed.trace("w", self.update_eula_next_button)
        
        self.pages["eula"] = page
    
    def create_privacy_page(self):
        page = ttk.Frame(self.main_frame)
        
        # 隐私政策标题
        ttk.Label(page, text="隐私政策", font=("Arial", 16, "bold")).pack(pady=10)
        ttk.Label(page, text="请仔细阅读以下隐私政策。您必须接受政策才能继续安装。", wraplength=600).pack(pady=5)
        
        # 隐私政策文本区域
        privacy_frame = ttk.Frame(page, borderwidth=1, relief="solid")
        privacy_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=5)
        
        privacy_text = tk.Text(privacy_frame, wrap=tk.WORD, height=15, width=80)
        privacy_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(privacy_frame, command=privacy_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        privacy_text.config(yscrollcommand=scrollbar.set)
        
        # 使用内置的隐私政策文本
        privacy_content = PRIVACY_CONTENT
        
        privacy_text.insert(tk.END, privacy_content)
        privacy_text.config(state="disabled")
        
        # 同意选项
        self.privacy_agreed = tk.BooleanVar(value=False)
        ttk.Checkbutton(page, text="我接受隐私政策中的条款", variable=self.privacy_agreed).pack(anchor=tk.W, pady=10)
        
        # 按钮区域
        btn_frame = ttk.Frame(page)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="取消", command=self.confirm_exit).pack(side=tk.RIGHT, padx=5)
        self.next_btn_privacy = ttk.Button(btn_frame, text="下一步", command=lambda: self.show_page("install"), state="disabled")
        self.next_btn_privacy.pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="上一步", command=lambda: self.show_page("eula")).pack(side=tk.RIGHT, padx=5)
        
        # 绑定复选框状态变化
        self.privacy_agreed.trace("w", self.update_privacy_next_button)
        
        self.pages["privacy"] = page
    
    def create_install_page(self):
        page = ttk.Frame(self.main_frame)
        
        # 安装选项标题
        ttk.Label(page, text="安装选项", font=("Arial", 16, "bold")).pack(pady=20)
        
        # 安装路径选择
        path_frame = ttk.Frame(page)
        path_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(path_frame, text="安装位置:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=10)
        ttk.Entry(path_frame, textvariable=self.install_path, width=50).grid(row=0, column=1, padx=5, pady=10)
        ttk.Button(path_frame, text="浏览...", command=self.browse_install_path).grid(row=0, column=2, padx=5, pady=10)
        
        # 磁盘空间信息
        space_frame = ttk.Frame(page)
        space_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(space_frame, text="所需空间: 约 12 GB").pack(side=tk.LEFT, padx=5)
        self.available_space_label = ttk.Label(space_frame, text="可用空间: 计算中...")
        self.available_space_label.pack(side=tk.LEFT, padx=20)
        
        # 更新可用空间信息
        self.update_available_space()
        
        # 附加选项
        options_frame = ttk.LabelFrame(page, text="附加选项")
        options_frame.pack(fill=tk.X, pady=20, padx=5)
        
        ttk.Checkbutton(options_frame, text="创建桌面快捷方式", variable=self.create_shortcut).pack(anchor=tk.W, padx=10, pady=10)
        
        # 按钮区域
        btn_frame = ttk.Frame(page)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)
        
        ttk.Button(btn_frame, text="取消", command=self.confirm_exit).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="安装", command=self.start_installation).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="上一步", command=lambda: self.show_page("privacy")).pack(side=tk.RIGHT, padx=5)
        
        self.pages["install"] = page
    
    def create_progress_page(self):
        page = ttk.Frame(self.main_frame)
        
        # 安装进度标题
        ttk.Label(page, text="正在安装", font=("Arial", 16, "bold")).pack(pady=20)
        ttk.Label(page, text=f"正在安装 {APP_NAME} 到您的计算机...").pack(pady=10)
        
        # 进度条
        progress_frame = ttk.Frame(page)
        progress_frame.pack(fill=tk.X, pady=20, padx=20)
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, length=600, mode="determinate")
        self.progress_bar.pack(fill=tk.X, pady=10)
        
        # 状态文本
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_text)
        self.status_label.pack(pady=10)
        
        # 按钮区域
        btn_frame = ttk.Frame(page)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)
        
        self.cancel_btn = ttk.Button(btn_frame, text="取消", command=self.confirm_exit)
        self.cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        self.pages["progress"] = page
    
    def create_finish_page(self):
        page = ttk.Frame(self.main_frame)
        
        # 完成标题
        ttk.Label(page, text="安装完成", font=("Arial", 16, "bold")).pack(pady=20)
        
        # 完成信息
        finish_text = f"{APP_NAME} 已成功安装到您的计算机。\n\n"
        finish_text += "点击\"完成\"退出安装程序。"
        
        ttk.Label(page, text=finish_text, wraplength=600, justify="left").pack(pady=20)
        
        # 启动选项
        self.launch_after_install = tk.BooleanVar(value=True)
        ttk.Checkbutton(page, text=f"立即启动 {APP_NAME}", variable=self.launch_after_install).pack(anchor=tk.W, pady=10)
        
        # 按钮区域
        btn_frame = ttk.Frame(page)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)
        
        ttk.Button(btn_frame, text="完成", command=self.finish_installation).pack(side=tk.RIGHT, padx=5)
        
        self.pages["finish"] = page
    
    def show_page(self, page_name):
        # 隐藏当前页面
        if self.current_page and self.current_page in self.pages:
            self.pages[self.current_page].pack_forget()
        
        # 显示新页面
        if page_name in self.pages:
            self.pages[page_name].pack(fill=tk.BOTH, expand=True)
            self.current_page = page_name
            
            # 特殊页面处理
            if page_name == "install":
                self.update_available_space()
    
    def update_license_next_button(self, *args):
        if self.license_agreed.get():
            self.next_btn_license.config(state="normal")
        else:
            self.next_btn_license.config(state="disabled")
    
    def update_eula_next_button(self, *args):
        if self.eula_agreed.get():
            self.next_btn_eula.config(state="normal")
        else:
            self.next_btn_eula.config(state="disabled")
    
    def update_privacy_next_button(self, *args):
        if self.privacy_agreed.get():
            self.next_btn_privacy.config(state="normal")
        else:
            self.next_btn_privacy.config(state="disabled")
    
    def browse_install_path(self):
        path = filedialog.askdirectory(initialdir=self.install_path.get())
        if path:
            # 确保路径末尾有 Ollama 文件夹
            if not path.endswith(APP_NAME):
                path = os.path.join(path, APP_NAME)
            self.install_path.set(path)
            self.update_available_space()
    
    def update_available_space(self):
        try:
            path = self.install_path.get()
            # 获取驱动器根目录
            if os.path.isdir(path):
                drive_root = os.path.splitdrive(path)[0] + os.path.sep
            else:
                drive_root = os.path.splitdrive(os.path.dirname(path))[0] + os.path.sep
            
            # 获取可用空间
            total, used, free = shutil.disk_usage(drive_root)
            free_gb = free / (1024 * 1024 * 1024)
            
            self.available_space_label.config(text=f"可用空间: {free_gb:.2f} GB")
        except Exception as e:
            self.available_space_label.config(text=f"可用空间: 无法获取 ({str(e)})")
    
    def confirm_exit(self):
        if messagebox.askyesno("确认退出", "您确定要退出安装程序吗？"):
            self.root.destroy()
    
    def start_installation(self):
        # 检查安装路径
        install_path = self.install_path.get()
        if not install_path:
            messagebox.showerror("错误", "请指定安装路径")
            return
        
        # 创建安装目录（如果不存在）
        try:
            os.makedirs(install_path, exist_ok=True)
        except Exception as e:
            messagebox.showerror("错误", f"无法创建安装目录: {str(e)}")
            return
        
        # 显示进度页面
        self.show_page("progress")
        
        # 启动安装线程
        threading.Thread(target=self.installation_process, daemon=True).start()
    
    def installation_process(self):
        try:
            install_path = self.install_path.get()
            create_shortcut = self.create_shortcut.get()
            
            # 步骤1: 准备安装
            self.update_progress(0, "准备安装...")
            
            # 步骤2: 下载文件
            self.update_progress(10, "正在下载 zip")
            download_path = os.path.join(install_path, "zip.zip")
            self.download_file(DOWNLOAD_URL, download_path)
            
            # 步骤3: 解压文件
            self.update_progress(60, "正在解压文件...")
            self.extract_zip(download_path, install_path)
            
            # 步骤4: 清理临时文件
            self.update_progress(80, "正在清理临时文件...")
            try:
                os.remove(download_path)
            except:
                pass
            
            # 步骤5: 创建快捷方式
            if create_shortcut:
                self.update_progress(90, "正在创建桌面快捷方式...")
                self.create_desktop_shortcut(install_path)
            
            # 步骤6: 设置环境变量
            self.update_progress(95, "正在设置环境变量...")
            self.add_to_environment_variables(install_path)
            
            # 完成安装
            self.update_progress(100, "安装完成!")
            
            # 显示完成页面
            self.root.after(1000, lambda: self.show_page("finish"))
            
        except Exception as e:
            # 安装失败
            self.root.after(0, lambda: messagebox.showerror("安装失败", f"安装过程中发生错误: {str(e)}"))
            self.update_progress(0, "安装失败")
    
    def update_progress(self, value, status):
        self.root.after(0, lambda: self.progress_var.set(value))
        self.root.after(0, lambda: self.status_text.set(status))
    
    def download_file(self, url, destination):
        # 设置线程数和超时时间
        retry_count = 0
        timeout = 100  # 设置超时时间为100秒
        num_threads = 4  # 设置下载线程数
        
        # 常见浏览器的User-Agent列表
        user_agents = [
            # Chrome
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            # Firefox
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
            # Edge
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
            # Safari
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
        ]
        
        # 多线程下载函数
        def download_chunk(url, start_byte, end_byte, chunk_file, user_agent, thread_id):
            try:
                # 创建请求对象并设置自定义请求头
                opener = urllib.request.build_opener()
                
                # 设置多个请求头，模拟真实浏览器行为
                headers = [
                    ("User-Agent", user_agent),
                    ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"),
                    ("Accept-Language", "zh-CN,zh;q=0.9,en;q=0.8"),
                    ("Accept-Encoding", "gzip, deflate, br"),
                    ("Connection", "keep-alive"),
                    ("Upgrade-Insecure-Requests", "1"),
                    ("Cache-Control", "max-age=0"),
                    ("Referer", "https://imwzr.top/"),
                    ("Range", f"bytes={start_byte}-{end_byte}"),  # 添加Range头，指定下载范围
                    ("Sec-Fetch-Dest", "document"),
                    ("Sec-Fetch-Mode", "navigate"),
                    ("Sec-Fetch-Site", "cross-site"),
                    ("Sec-Fetch-User", "?1")
                ]
                
                opener.addheaders = headers
                urllib.request.install_opener(opener)
                
                # 模拟用户行为：在请求前随机等待一小段时间
                time.sleep(random.uniform(0.1, 0.5))
                
                # 使用urlopen设置超时
                request = urllib.request.Request(url)
                with urllib.request.urlopen(request, timeout=timeout) as response, open(chunk_file, 'wb') as out_file:
                    # 随机选择不同的块大小，模拟不同的网络环境
                    block_size = 4096  # 4KB
                    downloaded = 0
                    chunk_size = end_byte - start_byte + 1
                    
                    while True:
                        # 模拟网络波动：随机调整下载速度
                        if random.random() < 0.05:  # 5%的概率出现速度变化
                            time.sleep(random.uniform(0.01, 0.1))
                        
                        buffer = response.read(block_size)
                        if not buffer:
                            break
                            
                        downloaded += len(buffer)
                        out_file.write(buffer)
                        
                        # 更新进度信息到共享变量
                        with download_chunk.lock:
                            download_chunk.total_downloaded += len(buffer)
                            current_progress = download_chunk.total_downloaded / download_chunk.total_size * 100
                            current_time = time.time()
                            
                            # 每0.5秒更新一次进度显示
                            if current_time - download_chunk.last_update_time >= 0.5:
                                # 计算下载速度 (bytes/second)
                                download_speed = (download_chunk.total_downloaded - download_chunk.last_downloaded) / (current_time - download_chunk.last_update_time)
                                download_chunk.last_downloaded = download_chunk.total_downloaded
                                download_chunk.last_update_time = current_time
                                
                                # 计算预计剩余时间
                                if download_speed > 0:
                                    remaining_bytes = download_chunk.total_size - download_chunk.total_downloaded
                                    estimated_time = remaining_bytes / download_speed
                                    
                                    # 格式化时间显示
                                    if estimated_time < 60:
                                        time_str = f"{estimated_time:.0f}秒"
                                    elif estimated_time < 3600:
                                        time_str = f"{estimated_time/60:.1f}分钟"
                                    else:
                                        time_str = f"{estimated_time/3600:.1f}小时"
                                    
                                    # 显示下载速度和预计剩余时间
                                    speed_str = f"{download_speed/1024/1024:.2f}MB/s"
                                    percent = min(current_progress, 50) + 10
                                    self.update_progress(percent, f"多线程下载: {percent:.1f}% ({download_chunk.total_downloaded/(1024*1024):.1f}MB/{download_chunk.total_size/(1024*1024):.1f}MB) - {speed_str} - 剩余时间: {time_str}")
                
                return True
            except Exception as e:
                print(f"线程 {thread_id} 下载失败: {str(e)}")
                return False
        
        # 无限重试下载
        while True:
            try:
                # 确保目标目录存在
                os.makedirs(os.path.dirname(destination), exist_ok=True)
                
                # 随机选择一个User-Agent
                user_agent = random.choice(user_agents)
                
                # 获取文件大小
                self.update_progress(10, "正在连接到下载服务器...")
                
                # 创建请求对象并设置自定义请求头
                opener = urllib.request.build_opener()
                headers = [("User-Agent", user_agent)]
                opener.addheaders = headers
                urllib.request.install_opener(opener)
                
                # 获取文件大小
                request = urllib.request.Request(url, method='HEAD')
                with urllib.request.urlopen(request, timeout=timeout) as response:
                    file_size = int(response.info().get('Content-Length', 0))
                
                # 如果文件大小为0或无法获取，使用单线程下载
                if file_size == 0:
                    self.update_progress(15, "无法获取文件大小，使用单线程下载...")
                    # 使用单线程下载
                    request = urllib.request.Request(url)
                    with urllib.request.urlopen(request, timeout=timeout) as response, open(destination, 'wb') as out_file:
                        total_size = int(response.info().get('Content-Length', 0))
                        downloaded = 0
                        block_size = 4096
                        
                        while True:
                            buffer = response.read(block_size)
                            if not buffer:
                                break
                                
                            downloaded += len(buffer)
                            out_file.write(buffer)
                            
                            if total_size > 0:
                                percent = min(downloaded * 100 / total_size, 50) + 10
                                self.update_progress(percent, f"正在下载: {percent:.1f}% ({downloaded/(1024*1024):.1f}MB/{total_size/(1024*1024):.1f}MB)")
                            else:
                                self.update_progress(30, f"正在下载: {downloaded/(1024*1024):.1f}MB (未知总大小)")
                else:
                    # 使用多线程下载
                    self.update_progress(15, f"准备多线程下载，文件大小: {file_size/(1024*1024):.1f}MB...")
                    
                    # 计算每个线程下载的字节范围
                    chunk_size = file_size // num_threads
                    chunks = []
                    for i in range(num_threads):
                        start_byte = i * chunk_size
                        end_byte = start_byte + chunk_size - 1 if i < num_threads - 1 else file_size - 1
                        chunks.append((start_byte, end_byte))
                    
                    # 创建临时目录存放分块文件
                    temp_dir = os.path.join(os.path.dirname(destination), "temp_download")
                    os.makedirs(temp_dir, exist_ok=True)
                    
                    # 初始化共享变量
                    download_chunk.lock = threading.Lock()
                    download_chunk.total_downloaded = 0
                    download_chunk.total_size = file_size
                    download_chunk.last_update_time = time.time()
                    download_chunk.last_downloaded = 0
                    
                    # 创建并启动下载线程
                    threads = []
                    chunk_files = []
                    for i, (start_byte, end_byte) in enumerate(chunks):
                        chunk_file = os.path.join(temp_dir, f"chunk_{i}.tmp")
                        chunk_files.append(chunk_file)
                        thread = threading.Thread(
                            target=download_chunk,
                            args=(url, start_byte, end_byte, chunk_file, user_agent, i)
                        )
                        threads.append(thread)
                        thread.start()
                    
                    # 等待所有线程完成
                    for thread in threads:
                        thread.join()
                    
                    # 检查所有分块是否下载成功
                    all_chunks_exist = all(os.path.exists(f) for f in chunk_files)
                    if not all_chunks_exist:
                        raise Exception("部分分块下载失败")
                    
                    # 合并分块文件
                    self.update_progress(60, "正在合并文件...")
                    with open(destination, 'wb') as outfile:
                        for chunk_file in chunk_files:
                            with open(chunk_file, 'rb') as infile:
                                shutil.copyfileobj(infile, outfile)
                    
                    # 清理临时文件
                    for chunk_file in chunk_files:
                        if os.path.exists(chunk_file):
                            os.remove(chunk_file)
                    if os.path.exists(temp_dir):
                        os.rmdir(temp_dir)
                
                # 验证下载的文件
                if not os.path.exists(destination) or os.path.getsize(destination) == 0:
                    raise Exception("下载文件为空或不存在")
                
                # 下载成功，跳出循环
                break
                    
            except urllib.error.HTTPError as e:
                retry_count += 1
                # 模拟真实用户重试行为：等待时间随重试次数增加
                wait_time = random.uniform(1.0, 3.0) * min(retry_count, 10)
                self.update_progress(10, f"下载失败，{wait_time:.1f}秒后重试(第{retry_count}次)...")
                time.sleep(wait_time)
            except urllib.error.URLError as e:
                retry_count += 1
                wait_time = random.uniform(1.5, 3.5) * min(retry_count, 10)
                self.update_progress(10, f"连接失败，{wait_time:.1f}秒后重试(第{retry_count}次)...")
                time.sleep(wait_time)
            except socket.timeout:
                retry_count += 1
                wait_time = random.uniform(2.0, 4.0) * min(retry_count, 10)
                self.update_progress(10, f"连接超时，{wait_time:.1f}秒后重试(第{retry_count}次)...")
                time.sleep(wait_time)
            except Exception as e:
                retry_count += 1
                wait_time = random.uniform(1.0, 3.0) * min(retry_count, 10)
                self.update_progress(10, f"下载出错，{wait_time:.1f}秒后重试(第{retry_count}次)...")
                time.sleep(wait_time)
                
        # 无限重试，不会到达这里
    
    def extract_zip(self, zip_path, extract_to):
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # 获取文件列表
                file_list = zip_ref.namelist()
                total_files = len(file_list)
                
                # 解压每个文件
                for i, file in enumerate(file_list):
                    zip_ref.extract(file, extract_to)
                    progress = 60 + (i / total_files) * 20
                    self.update_progress(progress, f"正在解压: {i+1}/{total_files}")
        except Exception as e:
            raise Exception(f"解压失败: {str(e)}")
    
    def create_desktop_shortcut(self, install_path):
        try:
            # 查找可执行文件
            exe_path = None
            for root, dirs, files in os.walk(install_path):
                for file in files:
                    if file.lower() == "main.exe":
                        exe_path = os.path.join(root, file)
                        break
                if exe_path:
                    break
            
            if not exe_path:
                raise Exception("找不到可执行文件")
            
            # 获取桌面路径
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            
            # 创建快捷方式
            shortcut_path = os.path.join(desktop_path, "马牛逼代码助手.lnk")
            
            # 使用PowerShell创建快捷方式
            ps_command = f'''
            $WshShell = New-Object -ComObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
            $Shortcut.TargetPath = "{exe_path}"
            $Shortcut.WorkingDirectory = "{os.path.dirname(exe_path)}"
            $Shortcut.Description = "马牛逼代码助手"
            $Shortcut.Save()
            '''
            
            # 执行PowerShell命令
            subprocess.run(["powershell", "-Command", ps_command], check=True)
            
        except Exception as e:
            # 快捷方式创建失败，但不影响安装
            self.root.after(0, lambda: messagebox.showwarning("警告", f"无法创建桌面快捷方式: {str(e)}"))
    
    def add_to_environment_variables(self, install_path):
        try:
            # 构建models文件夹路径
            models_path = os.path.join(install_path, "models")
            
            # 确保models文件夹存在
            os.makedirs(models_path, exist_ok=True)
            
            # 使用PowerShell设置环境变量
            ps_command = f'''
            [System.Environment]::SetEnvironmentVariable("OLLAMA_MODELS", "{models_path}", [System.EnvironmentVariableTarget]::User)
            '''
            
            # 执行PowerShell命令
            subprocess.run(["powershell", "-Command", ps_command], check=True)
            
            self.update_progress(95, "正在设置环境变量...")
            
        except Exception as e:
            # 环境变量设置失败，但不影响安装
            self.root.after(0, lambda: messagebox.showwarning("警告", f"无法设置环境变量: {str(e)}"))

    
    def finish_installation(self):
        # 如果选择了立即启动
        if self.launch_after_install.get():
            install_path = self.install_path.get()
            # 查找可执行文件
            exe_path = None
            for root, dirs, files in os.walk(install_path):
                for file in files:
                    if file.lower() == "main.exe":
                        exe_path = os.path.join(root, file)
                        break
                if exe_path:
                    break
            
            if exe_path:
                # 使用subprocess启动程序
                subprocess.Popen([exe_path], cwd=os.path.dirname(exe_path))
        
        # 退出安装程序
        self.root.destroy()

# 主函数
def main():
    root = tk.Tk()
    app = InstallerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()