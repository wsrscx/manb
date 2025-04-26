# AI项目构建器

这是一个基于Python的AI自动构建项目工具，使用Ollama API与AI模型交互，帮助用户根据简单的需求描述自动生成完整的项目代码。

## 功能特点

- 使用Ollama API与AI模型交互，使用 `deepcoder:latest` 模型
- 分段处理大型上下文，解决上下文长度限制问题
- 实时显示AI工作进度和下一步计划
- 支持创建新项目或修改现有项目
- 用户可自定义Ollama API地址和使用的模型
- 直观的TK图形界面，操作简单

## 安装要求

- `Python >= 3.6`
- Ollama服务已安装并运行（默认地址：[localhost:11434](http://localhost:11434)）
- 已安装 [deepcoder:latest](https://ollama.com/library/deepcoder) 模型

## 使用方法

1. 确保Ollama服务已启动，并已安装所需模型
2. 运行主程序：`python main.py`
3. 在界面中配置Ollama API地址和模型名称
4. 选择项目文件夹（新建或现有）
5. 输入项目需求描述
6. 选择创建新项目或修改现有项目
7. 点击 `开始生成`
