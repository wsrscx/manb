import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
import queue
import json
import time
import subprocess
import atexit
import signal

# 导入自定义模块
import json
import os
from ollama_client import OllamaClient
from project_manager import ProjectManager
from ui_manager import UIManager

class AIProjectBuilder:
    def __init__(self, root):
        self.root = root
        self.root.title("AI项目构建器")
        self.root.geometry("1000x700")
        
        # 创建队列用于线程间通信
        self.message_queue = queue.Queue()
        
        # 初始化组件
        self.ollama_client = OllamaClient()
        self.project_manager = ProjectManager()
        self.ui_manager = UIManager(self.root, self.message_queue, self.start_project_generation, 
                                   self.select_project_folder, self.update_ollama_settings)
        
        # 设置固定值
        self.project_path = ""
        self.requirement = ""
        self.model_name = "deepcoder:latest"
        self.ollama_api_url = "http://localhost:11434/api"
        self.inference_mode = True  # 始终启用推理模式
        
        # 更新Ollama客户端设置
        # 设置最大token数为-1和上下文窗口大小为26480
        self.ollama_client.update_settings(max_tokens=-1)  # 设置无限制的token生成
        
        # 启动Ollama服务
        self.ollama_process = None
        self.start_ollama_server()
        atexit.register(self.stop_ollama_server)
        
        # 启动UI更新线程
        self.running = True
        self.update_thread = threading.Thread(target=self.update_ui_from_queue)
        self.update_thread.daemon = True
        self.update_thread.start()
    
    def select_project_folder(self):
        """选择项目文件夹"""
        folder = filedialog.askdirectory()
        if folder:
            self.project_path = folder
            self.ui_manager.update_project_path(folder)
            self.message_queue.put({"type": "status", "message": f"已选择项目路径: {folder}"})
    
    # _load_config方法已移除，因为我们现在使用固定的模型和API URL
    
    def update_ollama_settings(self, api_url=None, model_name=None, max_tokens=None, temperature=None, top_p=None, batch_size=None, inference_temperature=None, inference_top_p=None, inference_mode=None):
        """更新Ollama设置（推理模式始终启用）"""
        # 推理模式始终为True，忽略传入的参数
        
        # 设置最大token数为-1和上下文窗口大小为26480
        max_tokens = -1
        context_window = 26480
        
        # 更新Ollama客户端设置
        self.ollama_client.update_settings(max_tokens=max_tokens)
        
        # 更新状态消息
        settings_msg = "已更新AI设置 - 推理模式: 已启用，最大token数: 无限制，上下文窗口: 26480"
        self.message_queue.put({"type": "status", "message": settings_msg})
    
    def start_project_generation(self, requirement, is_new_project):
        """启动项目生成过程"""
        self.requirement = requirement
        
        # 检查项目路径
        if not self.project_path:
            self.message_queue.put({"type": "error", "message": "请先选择项目文件夹"})
            return
        
        # 检查需求
        if not requirement.strip():
            self.message_queue.put({"type": "error", "message": "请输入项目需求"})
            return
        
        # 清空日志并显示开始信息
        self.ui_manager.clear_logs()
        self.message_queue.put({"type": "status", "message": "开始处理项目需求..."})
        
        # 在新线程中运行项目生成
        generation_thread = threading.Thread(
            target=self.run_project_generation,
            args=(requirement, is_new_project)
        )
        generation_thread.daemon = True
        generation_thread.start()
    
    def run_project_generation(self, requirement, is_new_project):
        """在单独的线程中运行项目生成"""
        try:
            # 准备项目上下文
            if is_new_project:
                status_msg = "创建新项目..."
                print(f"[状态] {status_msg}")  # 同步输出到控制台
                self.message_queue.put({"type": "status", "message": status_msg})
                os.makedirs(self.project_path, exist_ok=True)
            else:
                status_msg = "分析现有项目..."
                print(f"[状态] {status_msg}")  # 同步输出到控制台
                self.message_queue.put({"type": "status", "message": status_msg})
                project_files = self.project_manager.scan_project(self.project_path)
                files_msg = f"找到 {len(project_files)} 个文件"
                print(f"[状态] {files_msg}")  # 同步输出到控制台
                self.message_queue.put({"type": "status", "message": files_msg})
                # 立即刷新UI
                self.root.update_idletasks()
            
            # 构建提示词
            prompt = self.build_prompt(requirement, is_new_project)
            
            # 调用AI生成代码
            gen_msg = "正在使用AI生成代码..."
            print(f"[状态] {gen_msg}")  # 同步输出到控制台
            self.message_queue.put({"type": "status", "message": gen_msg})
            
            plan_msg = "使用推理模式并规划项目结构"
            print(f"[计划] {plan_msg}")  # 同步输出到控制台
            self.message_queue.put({"type": "plan", "message": plan_msg})
            
            # 立即刷新UI
            self.root.update_idletasks()
            
            # 记录推理模式状态
            print("推理模式状态: 启用")
            
            # 分段处理大型上下文
            responses = self.ollama_client.generate_with_context(prompt, self.project_path, True)  # 始终启用推理模式
            
            # 处理AI响应
            for i, response in enumerate(responses):
                self.process_ai_response(response, i+1, len(responses))
                # 每处理完一个响应后立即刷新UI
                self.root.update_idletasks()
            
            complete_msg = "项目生成完成!"
            print(f"[状态] {complete_msg}")  # 同步输出到控制台
            self.message_queue.put({"type": "status", "message": complete_msg})
            
            done_msg = "所有任务已完成"
            print(f"[计划] {done_msg}")  # 同步输出到控制台
            self.message_queue.put({"type": "plan", "message": done_msg})
            
            # 最终刷新UI
            self.root.update_idletasks()
            
        except Exception as e:
            error_msg = f"错误: {str(e)}"
            print(f"[错误] {error_msg}")  # 同步输出到控制台
            self.message_queue.put({"type": "error", "message": error_msg})
            # 发生错误时立即刷新UI
            self.root.update_idletasks()
    
    def start_ollama_server(self):
        """启动Ollama服务"""
        try:
            # 检查是否在PyInstaller打包环境中运行
            if getattr(sys, 'frozen', False):
                # 如果是打包后的环境，使用sys._MEIPASS获取临时解压目录
                base_dir = sys._MEIPASS
                ollama_dir = os.path.join(base_dir, "ollama")
            else:
                # 如果是开发环境，使用脚本所在目录
                base_dir = os.path.dirname(os.path.abspath(__file__))
                ollama_dir = os.path.join(base_dir, "ollama")
            
            ollama_path = os.path.join(ollama_dir, "ollama.exe")
            
            print(f"[信息] 尝试使用Ollama路径: {ollama_path}")
            
            if not os.path.exists(ollama_path):
                error_msg = f"错误: 未找到ollama.exe，路径: {ollama_path}"
                print(f"[错误] {error_msg}")
                self.message_queue.put({"type": "error", "message": error_msg})
                return

            # 使用CREATE_NEW_PROCESS_GROUP确保可以正确终止进程及其子进程
            self.ollama_process = subprocess.Popen(
                [ollama_path, "serve"],
                cwd=ollama_dir, # 在ollama目录下执行
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                stdout=subprocess.PIPE, # 重定向输出
                stderr=subprocess.PIPE
            )
            print(f"[信息] Ollama进程工作目录: {ollama_dir}")
            status_msg = f"Ollama服务已启动 (PID: {self.ollama_process.pid})"
            print(f"[状态] {status_msg}")
            self.message_queue.put({"type": "status", "message": status_msg})
        except Exception as e:
            error_msg = f"启动Ollama服务失败: {str(e)}"
            print(f"[错误] {error_msg}")
            self.message_queue.put({"type": "error", "message": error_msg})

    def stop_ollama_server(self):
        """停止Ollama服务"""
        if self.ollama_process and self.ollama_process.poll() is None:
            try:
                # 在Windows上，使用 CTRL_BREAK_EVENT 来终止进程组
                os.kill(self.ollama_process.pid, signal.CTRL_BREAK_EVENT)
                self.ollama_process.wait(timeout=5) # 等待进程结束
                status_msg = f"Ollama服务 (PID: {self.ollama_process.pid}) 已停止"
                print(f"[状态] {status_msg}")
                # 不再向队列发送消息，因为程序可能正在退出
            except ProcessLookupError:
                 print(f"[状态] Ollama服务 (PID: {self.ollama_process.pid}) 似乎已经停止")
            except subprocess.TimeoutExpired:
                print(f"[警告] 停止Ollama服务超时，强制终止")
                self.ollama_process.terminate() # 尝试温和终止
                try:
                    self.ollama_process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    print(f"[警告] 强制终止Ollama服务失败，可能需要手动处理")
                    self.ollama_process.kill() # 最后手段
            except Exception as e:
                error_msg = f"停止Ollama服务时出错: {str(e)}"
                print(f"[错误] {error_msg}")
            finally:
                self.ollama_process = None
        else:
            print("[状态] Ollama服务未运行或已停止")

    def build_prompt(self, requirement, is_new_project):
        """构建提示词"""
        if is_new_project:
            prompt = (
                "你是一个专业的软件开发助手，精通各种编程语言和框架。\n\n"
                "# 任务\n"
                "根据用户的需求，创建一个完整的项目，包括所有必要的代码文件、配置文件和文档。\n\n"
                "# 要求\n"
                "1. 分析用户需求，确定合适的项目结构和技术栈\n"
                "2. 创建所有必要的文件，包括源代码、配置文件和文档\n"
                "3. 确保代码质量高，没有明显的bug和错误\n"
                "4. 提供清晰的注释和文档\n"
                "5. 考虑代码的可维护性和可扩展性\n\n"
                "# 输出格式\n"
                "对于每个文件，请使用以下格式：\n"
                "```file:<文件路径>\n"
                "<文件内容>\n"
                "```\n\n"
                "在文件之间，你可以添加解释说明，说明你的设计决策和下一步计划。\n\n"
                "# 用户需求\n"
                f"{requirement}\n"
            )
        else:
            prompt = (
                "你是一个专业的软件开发助手，精通各种编程语言和框架。\n\n"
                "# 任务\n"
                "根据用户的需求，修改现有项目，添加新功能或修复问题。\n\n"
                "# 要求\n"
                "1. 分析用户需求和现有代码\n"
                "2. 修改、添加或删除必要的文件\n"
                "3. 确保代码质量高，没有明显的bug和错误\n"
                "4. 保持代码风格的一致性\n"
                "5. 考虑代码的可维护性和可扩展性\n\n"
                "# 输出格式\n"
                "对于每个需要创建或修改的文件，请使用以下格式：\n"
                "```file:<文件路径>\n"
                "<文件内容>\n"
                "```\n\n"
                "在文件之间，你可以添加解释说明，说明你的设计决策和下一步计划。\n\n"
                "# 用户需求\n"
                f"{requirement}\n\n"
                "# 现有项目文件\n"
            )
            # 添加项目文件列表和内容摘要
            project_files = self.project_manager.scan_project(self.project_path)
            for file_path in project_files[:10]:  # 限制文件数量，避免超出上下文限制
                relative_path = os.path.relpath(file_path, self.project_path)
                prompt += f"- {relative_path}\n"
            
            prompt += "\n如果需要查看更多文件内容，请在回复中说明。\n"
        
        return prompt
    
    def process_ai_response(self, response, current_part, total_parts):
        """处理AI的响应，提取文件并保存"""
        status_msg = f"处理AI响应 ({current_part}/{total_parts})..."
        print(f"[状态] {status_msg}")  # 同步输出到控制台
        self.message_queue.put({"type": "status", "message": status_msg})
        
        # 解析响应中的文件
        file_pattern = r"```file:(.+?)\n([\s\S]+?)```"
        import re
        matches = re.finditer(file_pattern, response)
        
        files_processed = 0
        for match in matches:
            file_path = match.group(1).strip()
            file_content = match.group(2)
            
            # 确保文件路径是绝对路径
            if not os.path.isabs(file_path):
                file_path = os.path.join(self.project_path, file_path)
            
            # 创建目录（如果不存在）
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 保存文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_content)
            
            files_processed += 1
            relative_path = os.path.relpath(file_path, self.project_path)
            file_msg = f"已保存文件: {relative_path}"
            print(f"[文件] {file_msg}")  # 同步输出到控制台
            self.message_queue.put({"type": "file", "message": file_msg})
            
            # 每保存一个文件后立即刷新UI
            self.root.update_idletasks()
        
        # 提取计划信息
        plans = re.finditer(r"(?:下一步计划|接下来我将|计划如下|我的计划是)[:：]?\s*(.+?)(?=\n\n|$)", response)
        for plan in plans:
            plan_text = plan.group(1).strip()
            if plan_text:
                print(f"[计划] {plan_text}")  # 同步输出到控制台
                self.message_queue.put({"type": "plan", "message": plan_text})
                # 每添加一个计划后立即刷新UI
                self.root.update_idletasks()
        
        if files_processed == 0:
            no_file_msg = "此部分响应中没有找到文件"
            print(f"[状态] {no_file_msg}")  # 同步输出到控制台
            self.message_queue.put({"type": "status", "message": no_file_msg})
    
    def update_ui_from_queue(self):
        """从队列更新UI"""
        while self.running:
            try:
                # 处理队列中的所有消息
                messages_processed = 0
                max_messages_per_update = 10  # 每次更新处理的最大消息数
                
                # 处理多条消息，但限制每次循环处理的数量，避免UI冻结
                while messages_processed < max_messages_per_update:
                    # 非阻塞方式获取消息
                    message = self.message_queue.get(block=False)
                    message_type = message.get("type", "")
                    message_text = message.get("message", "")
                    
                    # 立即打印到控制台，确保控制台和UI同步
                    print(f"[{message_type}] {message_text}")
                    
                    if message_type == "status":
                        self.ui_manager.update_status(message_text)
                    elif message_type == "error":
                        self.ui_manager.update_error(message_text)
                    elif message_type == "file":
                        self.ui_manager.update_file_log(message_text)
                    elif message_type == "plan":
                        self.ui_manager.update_plan(message_text)
                    
                    self.message_queue.task_done()
                    messages_processed += 1
                    
                    # 每处理一条消息后立即更新UI
                    self.root.update_idletasks()
            except queue.Empty:
                # 队列为空，跳出内部循环
                pass
            
            # 短暂休眠，避免CPU占用过高，但不要太长以保持UI响应
            time.sleep(0.05)
            
            # 更新UI
            try:
                self.root.update()
            except tk.TclError:
                # 窗口已关闭
                self.running = False
                break
    
    def on_closing(self):
        """窗口关闭时的处理"""
        print("[状态] 正在关闭应用程序...")
        self.running = False
        self.stop_ollama_server() # 确保Ollama服务被停止
        # 等待UI更新线程结束（可选，但有助于干净退出）
        if self.update_thread.is_alive():
            try:
                self.update_thread.join(timeout=1)
            except RuntimeError:
                pass # 线程已结束
        self.root.destroy()
        sys.exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = AIProjectBuilder(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing) # 绑定关闭事件
    root.mainloop()