import requests
import json
import time
import os

class OllamaClient:
    def __init__(self, api_url="http://localhost:11434/api", model_name="deepcoder:latest"):
        """初始化Ollama客户端
        
        Args:
            api_url: Ollama API的URL
            model_name: 使用的模型名称
        """
        # 设置API参数
        self.api_url = "http://localhost:11434/api"
        self.model_name = "deepcoder:latest"
        self.timeout = 10000
        
        # 设置生成参数
        self.max_tokens = -1  # 设置为-1表示不限制生成的token数量
        self.context_window = 26480  # 增大上下文窗口大小
        self.temperature = 0.7
        self.top_p = 0.9
        self.batch_size = 3
        
        # 推理模型参数
        self.inference_temperature = 0.1
        self.inference_top_p = 0.95
        self.inference_model_name = "deepcoder:latest"
    
    # _load_config方法已移除，因为我们现在使用固定的模型和API URL
    
    def update_settings(self, api_url=None, model_name=None, max_tokens=None, temperature=None, top_p=None, batch_size=None, inference_temperature=None, inference_top_p=None, inference_model_name=None):
        """更新API和生成设置
        
        Args:
            api_url: 新的API URL
            model_name: 新的模型名称
            max_tokens: 最大生成token数
            temperature: 温度参数
            top_p: top-p采样参数
            batch_size: 分批处理大小
            inference_temperature: 推理模式温度参数
            inference_top_p: 推理模式top-p采样参数
            inference_model_name: 推理模式使用的模型名称
        """
        if api_url:
            self.api_url = api_url
        if model_name:
            self.model_name = model_name
        if max_tokens:
            self.max_tokens = max_tokens
        if temperature:
            self.temperature = temperature
        if top_p:
            self.top_p = top_p
        if batch_size:
            self.batch_size = batch_size
        if inference_temperature:
            self.inference_temperature = inference_temperature
        if inference_top_p:
            self.inference_top_p = inference_top_p
        if inference_model_name:
            self.inference_model_name = inference_model_name
    
    def generate(self, prompt, inference_mode=False):
        """生成单个响应
        
        Args:
            prompt: 提示词
            inference_mode: 是否使用推理模式（更高质量但可能更慢）
            
        Returns:
            生成的文本响应
        """
        try:
            # 构建请求参数
            request_data = {
                "model": self.inference_model_name if inference_mode else self.model_name,  # 根据推理模式选择不同的模型
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": self.max_tokens,  # 设置为-1表示不限制生成的token数量
                    "temperature": self.inference_temperature if inference_mode else self.temperature,  # 使用配置的推理温度
                    "top_p": self.inference_top_p if inference_mode else self.top_p,  # 使用配置的推理top_p
                    "num_ctx": self.context_window  # 使用26480作为上下文窗口大小
                }
            }
            
            # 打印当前使用的参数
            print(f"使用模型: {self.inference_model_name if inference_mode else self.model_name}")
            print(f"最大token数: {self.max_tokens}")
            print(f"上下文窗口大小: {self.context_window}")
            
            # 发送请求
            response = requests.post(
                f"{self.api_url}/generate",
                json=request_data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json().get('response', '')
            else:
                error_msg = f"API错误: {response.status_code} - {response.text}"
                print(error_msg)
                return f"生成失败: {error_msg}"
        
        except Exception as e:
            error_msg = f"请求异常: {str(e)}"
            print(error_msg)
            return f"生成失败: {error_msg}"
    
    def generate_with_context(self, prompt, project_path, inference_mode=False):
        """分段处理大型上下文
        
        Args:
            prompt: 基础提示词
            project_path: 项目路径，用于读取文件内容
            inference_mode: 是否使用推理模式（更高质量但可能更慢）
            
        Returns:
            生成的响应列表
        """
        # 记录推理模式状态
        print(f"推理模式状态: {'启用' if inference_mode else '禁用'}")
        
        # 设置文件内容分块处理的阈值（字符数）
        FILE_CONTENT_CHUNK_SIZE = 10000  # 每个文件内容块的最大字符数
        MAX_PROMPT_SIZE = int(self.context_window * 0.7)  # 预留30%空间给响应
        
        # 检查上下文窗口大小，确保不超过模型限制
        if len(prompt) > MAX_PROMPT_SIZE:
            print(f"警告: 提示词长度接近上下文窗口限制 ({len(prompt)}/{self.context_window})")
            print("将自动进行分批处理...")
        responses = []
        
        # 记录开始时间，用于性能监控
        start_time = time.time()
        
        # 获取提示词模板
        system_message = "你是一个专业的软件开发助手，精通各种编程语言和框架。"
        planning_suffix = "首先，请分析需求并提供项目的整体规划和结构设计。"
        implementation_suffix = "请实现以下文件:"
        finalization_suffix = "请检查项目的完整性，确保所有必要的文件都已创建，并提供如何运行和测试项目的说明。"
        
        # 构建基础提示词
        base_prompt = f"{system_message}\n\n{prompt}"
        
        # 第一阶段：项目规划和结构设计（使用推理模式获取更好的规划）
        planning_prompt = f"{base_prompt}\n\n{planning_suffix}"
        print(f"开始项目规划阶段 (推理模式: 开启)")
        planning_response = self.generate(planning_prompt, inference_mode=True)  # 规划阶段总是使用推理模式
        responses.append(planning_response)
        print(f"项目规划阶段完成，耗时: {time.time() - start_time:.2f}秒")
        
        # 从响应中提取计划信息
        planned_files = self._extract_planned_files(planning_response)
        
        # 第二阶段：逐个实现文件
        if planned_files:
            # 如果AI已经规划了文件，按计划实现
            batch_size = self.batch_size  # 使用配置的批处理大小
            total_batches = len(planned_files) // batch_size + (1 if len(planned_files) % batch_size > 0 else 0)
            print(f"开始文件实现阶段，共 {len(planned_files)} 个文件，分 {total_batches} 批处理 (每批 {batch_size} 个文件)")
            print(f"推理模式: {'开启' if inference_mode else '关闭'}")
            
            batch_start_time = time.time()
            for i, file_group in enumerate(self._group_files(planned_files, batch_size)):
                print(f"处理批次 {i+1}/{total_batches}，文件: {', '.join(file_group)}")
                files_prompt = f"{base_prompt}\n\n{implementation_suffix}\n" + "\n".join([f"- {f}" for f in file_group])
                
                # 如果是修改现有项目，添加现有文件内容（分批处理大文件）
                for file_path in file_group:
                    full_path = os.path.join(project_path, file_path) if not os.path.isabs(file_path) else file_path
                    if os.path.exists(full_path):
                        try:
                            # 获取文件大小
                            file_size = os.path.getsize(full_path)
                            print(f"处理文件: {file_path} (大小: {file_size/1024:.2f} KB)")
                            
                            # 读取文件内容
                            with open(full_path, 'r', encoding='utf-8') as f:
                                file_content = f.read()
                            
                            # 检查文件内容大小，如果超过阈值则分块处理
                            if len(file_content) > FILE_CONTENT_CHUNK_SIZE:
                                print(f"文件 {file_path} 内容过大，进行分块处理")
                                # 添加文件头部信息
                                files_prompt += f"\n\n现有文件 {file_path} 的内容(已分块，这是第1块):\n```\n{file_content[:FILE_CONTENT_CHUNK_SIZE]}\n```"
                                files_prompt += f"\n注意：文件 {file_path} 内容较长，已分块显示。这只是文件的前一部分。"
                            else:
                                # 文件内容不大，完整添加
                                files_prompt += f"\n\n现有文件 {file_path} 的内容:\n```\n{file_content}\n```"
                        except Exception as e:
                            files_prompt += f"\n\n无法读取文件 {file_path}: {str(e)}"
                
                # 检查提示词大小，如果超过限制则分批处理
                if len(files_prompt) > MAX_PROMPT_SIZE:
                    print(f"警告: 提示词长度超过限制 ({len(files_prompt)}/{MAX_PROMPT_SIZE})，进行分批处理")
                    # 分批处理大型提示词
                    batch_responses = self._process_large_prompt(files_prompt, base_prompt, implementation_suffix, file_group, project_path, inference_mode)
                    responses.extend(batch_responses)
                else:
                    # 正常处理
                    implementation_response = self.generate(files_prompt, inference_mode=inference_mode)
                    responses.append(implementation_response)
                
                print(f"批次 {i+1} 完成，耗时: {time.time() - batch_start_time:.2f}秒")
                batch_start_time = time.time()
        else:
            # 如果AI没有明确规划文件，分批次生成代码
            implementation_prompt = f"{base_prompt}\n\n请开始实现项目的核心文件。"
            implementation_response = self.generate(implementation_prompt, inference_mode=inference_mode)
            responses.append(implementation_response)
            
            # 继续生成其他必要文件
            followup_prompt = f"{base_prompt}\n\n请继续实现项目的其他必要文件，包括配置文件、辅助模块和文档。"
            followup_response = self.generate(followup_prompt, inference_mode=inference_mode)
            responses.append(followup_response)
        
        # 第三阶段：完善和测试
        print(f"开始项目完善阶段 (推理模式: {'开启' if inference_mode else '关闭'})")
        finalization_prompt = f"{base_prompt}\n\n{finalization_suffix}"
        finalization_response = self.generate(finalization_prompt, inference_mode=inference_mode)
        responses.append(finalization_response)
        
        # 输出总体性能统计
        total_time = time.time() - start_time
        print(f"项目生成完成，总耗时: {total_time:.2f}秒，生成了 {len(responses)} 个响应")
        print(f"平均每个响应耗时: {total_time/len(responses):.2f}秒")
        
        return responses
    
    def _extract_planned_files(self, response):
        """从响应中提取计划创建的文件列表
        
        Args:
            response: AI的响应文本
            
        Returns:
            计划创建的文件路径列表
        """
        import re
        
        # 尝试从文件模式中提取
        file_pattern = r"```file:(.+?)\n"
        file_matches = re.findall(file_pattern, response)
        
        if file_matches:
            return [path.strip() for path in file_matches]
        
        # 尝试从项目结构描述中提取
        structure_pattern = r"(?:项目结构|文件结构|目录结构)[:：]?\s*(?:\n|.)*?(?:```|\n\n)"
        structure_match = re.search(structure_pattern, response)
        
        if structure_match:
            structure_text = structure_match.group(0)
            # 查找结构中的文件路径
            path_pattern = r"[\w\-\.]+\.[\w]+"  # 简单的文件名模式
            return re.findall(path_pattern, structure_text)
        
        return []
    
    def _group_files(self, files, group_size):
        """将文件列表分组
        
        Args:
            files: 文件路径列表
            group_size: 每组的大小
            
        Returns:
            分组后的列表
        """
        return [files[i:i+group_size] for i in range(0, len(files), group_size)]
        
    def _process_large_prompt(self, original_prompt, base_prompt, implementation_suffix, file_group, project_path, inference_mode=False):
        """处理超大提示词，将其分解为多个较小的请求
        
        Args:
            original_prompt: 原始完整提示词
            base_prompt: 基础提示词部分
            implementation_suffix: 实现部分的提示词后缀
            file_group: 当前处理的文件组
            project_path: 项目路径
            inference_mode: 是否使用推理模式
            
        Returns:
            生成的响应列表
        """
        print(f"开始处理大型提示词，推理模式: {'启用' if inference_mode else '禁用'}")
        
        batch_responses = []
        MAX_PROMPT_SIZE = int(self.context_window * 0.7)  # 预留30%空间给响应
        
        # 对每个文件单独处理
        for file_path in file_group:
            print(f"单独处理大文件: {file_path}")
            full_path = os.path.join(project_path, file_path) if not os.path.isabs(file_path) else file_path
            
            if not os.path.exists(full_path):
                continue
                
            try:
                # 读取文件内容
                with open(full_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                
                # 如果文件内容很大，需要分块处理
                if len(file_content) > MAX_PROMPT_SIZE // 2:  # 文件内容占用提示词的一半以上
                    # 使用配置的文件块大小或默认值
                    chunk_size = self.config["generation"]["file_chunk_size"] if self.config and "file_chunk_size" in self.config["generation"] else MAX_PROMPT_SIZE // 2
                    chunks = [file_content[i:i+chunk_size] for i in range(0, len(file_content), chunk_size)]
                    
                    print(f"文件 {file_path} 分为 {len(chunks)} 块处理")
                    
                    # 处理每个块
                    for i, chunk in enumerate(chunks):
                        chunk_prompt = f"{base_prompt}\n\n{implementation_suffix}\n- {file_path}\n\n"
                        chunk_prompt += f"现有文件 {file_path} 的内容(第{i+1}/{len(chunks)}块):\n```\n{chunk}\n```\n"
                        
                        if i > 0:
                            chunk_prompt += f"\n注意：这是文件 {file_path} 的第 {i+1} 块，请继续之前的实现。"
                        
                        # 生成响应
                        chunk_response = self.generate(chunk_prompt, inference_mode=inference_mode)
                        batch_responses.append(chunk_response)
                else:
                    # 文件不是特别大，可以一次处理
                    file_prompt = f"{base_prompt}\n\n{implementation_suffix}\n- {file_path}\n\n"
                    file_prompt += f"现有文件 {file_path} 的内容:\n```\n{file_content}\n```"
                    
                    # 生成响应
                    file_response = self.generate(file_prompt, inference_mode=inference_mode)
                    batch_responses.append(file_response)
                    
            except Exception as e:
                print(f"处理文件 {file_path} 时出错: {str(e)}")
                # 添加错误信息到响应
                error_prompt = f"{base_prompt}\n\n{implementation_suffix}\n- {file_path}\n\n无法读取文件 {file_path}: {str(e)}"
                error_response = self.generate(error_prompt, inference_mode=inference_mode)
                batch_responses.append(error_response)
        
        return batch_responses