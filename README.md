# AI视频标题改名器

AI视频标题改名器是一个基于人工智能的工具，可以根据原始视频标题生成意思相近但表达不同的新标题。该工具支持多种国内外AI大模型API，能够生成多样化、有创意的标题变体，同时保持原始标题的核心意义。

## 特性

- **保持原意的标题改写**：生成新的标题表达，但保留原标题的核心信息和意思
- **自定义输出字数**：可以指定生成标题的目标字数
- **多种风格选择**：支持多种预设风格，如"幽默"、"正式"、"疑问式"等
- **批量处理**：支持批量处理多个标题
- **多种AI模型支持**：支持阿里通义千问、百度文心一言、讯飞星火、智谱ChatGLM等多种AI大模型
- **OpenAI兼容接口**：支持通过OpenAI兼容接口调用通义千问模型
- **命令行和图形界面**：同时提供命令行界面和GUI界面，满足不同用户需求
- **可定制性**：可调整生成的随机性和输出变体数量

## 支持的AI模型

- **阿里通义千问**：提供标准版、极速版和增强版三种模型选择
- **百度文心一言**：提供标准版和快速版两种模型选择
- **讯飞星火认知大模型**：科大讯飞提供的大语言模型
- **智谱AI ChatGLM**：清华大学开源的对话语言模型

## 安装

1. 克隆本项目到本地：
```bash
git clone https://github.com/yourusername/ai-video-title-renamer.git
cd ai-video-title-renamer
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 在 `config.py` 中配置您的API密钥：
```python
# 在config.py中修改
# 阿里云通义千问API配置
ALIYUN_API_KEY = "your-aliyun-api-key-here"
ALIYUN_SECRET_KEY = "your-aliyun-secret-key-here"

# 百度文心一言API配置
BAIDU_API_KEY = "your-baidu-api-key-here"
BAIDU_SECRET_KEY = "your-baidu-secret-key-here"
```

## 使用方法

### 命令行界面

最简单的使用方法是通过命令行界面：

```bash
# 使用阿里通义千问重命名标题
python cli.py "Python入门教程：从零开始学习编程的完整指南" -m qwen

# 使用百度文心一言重命名标题
python cli.py "Python入门教程：从零开始学习编程的完整指南" -m ernie_bot

# 指定字数
python cli.py "Python入门教程：从零开始学习编程的完整指南" -l 15

# 指定风格
python cli.py "Python入门教程：从零开始学习编程的完整指南" -s 幽默

# 生成多个变体
python cli.py "Python入门教程：从零开始学习编程的完整指南" -n 3

# 处理文件中的多个标题
python cli.py -f titles.txt -o results.md

# 查看所有可用的标题风格
python cli.py --list-styles

# 查看所有可用的AI模型
python cli.py --list-models
```

### 图形界面使用

我们提供了图形用户界面，让使用变得更加简单：

```bash
python gui.py
```

在GUI界面中，您可以：
1. 选择使用的AI模型
2. 配置不同模型的API密钥
3. 输入或粘贴原始标题
4. 调整字数、风格、随机性和变体数量等参数
5. 点击"生成标题"按钮生成新标题
6. 复制或保存生成的结果

### 使用OpenAI兼容接口

本工具支持使用OpenAI兼容接口调用通义千问模型，使用方式更加简单直接：

```python
import os
from openai import OpenAI

# 初始化OpenAI客户端，指向通义千问的兼容端点
client = OpenAI(
    api_key="your-aliyun-api-key", 
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 调用API生成标题
original_title = "Python入门教程：从零开始学习编程的完整指南"
completion = client.chat.completions.create(
    model="qwen-plus",  # 可选：qwen-v1（标准版）、qwen-turbo（极速版）、qwen-plus（增强版）
    messages=[
        {'role': 'system', 'content': '你是一位专业的视频标题优化专家，擅长根据原标题创作新颖、吸引人的标题变体。'},
        {'role': 'user', 'content': f'请帮我优化这个视频标题，生成一个更吸引人的版本。原标题：{original_title}。字数控制在20个字左右。'}
    ],
    temperature=0.7
)

# 打印生成的标题
print(completion.choices[0].message.content)
```

### 作为Python库使用

您也可以在自己的Python代码中导入并使用AI改名器：

```python
from ai_rename import AIRenamer

# 初始化改名器（使用通义千问）
renamer = AIRenamer(
    api_key="your-aliyun-api-key",
    secret_key="your-aliyun-secret-key", 
    model="qwen-plus"  # 使用增强版，也可选择"qwen"或"qwen-turbo"
)

# 基本使用
original_title = "Python入门教程：从零开始学习编程的完整指南"
new_title = renamer.rename(original_title)
print(f"新标题: {new_title}")

# 指定字数和风格
new_title = renamer.rename(original_title, target_length=15, style="幽默")
print(f"新标题(幽默风格，约15字): {new_title}")

# 生成多个变体
variants = renamer.rename(original_title, num_variants=3)
for i, variant in enumerate(variants, 1):
    print(f"变体{i}: {variant}")
```

### 运行演示

项目中包含一个演示脚本，展示了AI改名器的各种功能：

```bash
python demo.py
```

## 获取API密钥

要使用本工具，您需要获取相应AI模型的API密钥：

1. **阿里通义千问**：前往[通义千问开放平台](https://dashscope.aliyun.com/)注册账号并获取API Key
2. **百度文心一言**：前往[百度智能云](https://cloud.baidu.com/product/wenxinworkshop)注册账号并获取API Key和Secret Key
3. **讯飞星火**：前往[讯飞开放平台](https://www.xfyun.cn/service/aigc)注册账号并获取相关密钥
4. **智谱ChatGLM**：前往[智谱AI](https://open.bigmodel.cn/)注册账号并获取API Key

## 可用的标题风格

程序预设了多种标题风格：
- **幽默**：幽默风趣，让人忍俊不禁
- **正式**：正式、专业、学术性强
- **吸引眼球**：引人注目，激发好奇心
- **简洁**：简洁明了，直奔主题
- **疑问式**：以问题形式呈现，引发思考
- **情感化**：带有情感色彩，引起共鸣
- **故事化**：以讲故事的方式呈现标题
- **数字化**：在标题中包含数字，提高可信度

您可以根据需要在`config.py`中添加更多自定义风格。

## 注意事项

1. 程序需要联网才能正常工作，因为它需要调用相应的AI模型API
2. API调用可能会产生费用，请注意控制使用量
3. 对于批量处理大量标题，程序会添加延时以避免API限流
4. 不同模型的生成效果可能有所差异，建议尝试不同模型以获得最佳效果
5. 使用OpenAI兼容接口需要安装`openai`库（`pip install openai`）

## 许可证

本项目采用MIT许可证。详见[LICENSE](LICENSE)文件。

## 贡献

欢迎贡献代码、报告bug或提出新功能建议。请提交issue或pull request。 