# EleReasoning - 电气工程基准评测系统

EleReasoning 是一个专门用于评估大语言模型在电气工程领域知识和推理能力的基准评测系统。该系统支持多种评测策略、多种模型接口，并提供全面的结果分析功能。

## 功能特点

- **多模型支持**：支持 OpenAI、通义千问、百度文心一言、本地部署模型等多种模型接口
- **多模态评测**：支持文本、图像和音频等多种输入模态的评测
- **多种评测策略**：提供直接回答、思维链(CoT)、专家提示、少样本学习等多种评测策略
- **多语言支持**：支持中文和英文两种语言的评测
- **全面的结果分析**：提供详细的得分分析、类别比较和错误案例分析
- **灵活的评测配置**：支持自定义评测范围、类别筛选和答案提取方式

## 项目结构



## 安装说明

### 环境要求

- Python 3.8+
- PyTorch 1.10+
- 其他依赖包（见requirements.txt）

### 安装步骤

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/elereasoning.git
cd elereasoning
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置模型：
   - 复制 `experiment/config/` 目录下的配置文件模板
   - 填入您的API密钥或本地模型路径

## 使用方法

### 基本评测

使用命令行运行评测：

```bash
cd experiment
python main.py \
    --dataset "datasets/elecbench_choices_fixed.csv" \
    --config "config/openai.json" \
    --output "results" \
    --strategy "cot" \
    --language "zh" \
    --llm_extract
```

### 参数说明

- `--dataset`: 数据集文件路径（必需）
- `--config`: 模型配置文件路径（必需）
- `--output`: 输出目录（默认：results）
- `--strategy`: 提示策略（可选：direct, cot, expert, few-shot，默认：cot）
- `--language`: 提示语言（可选：zh, en，默认：zh）
- `--llm_extract`: 使用LLM提取答案（可选）
- `--extract_api_key`: 用于LLM提取答案的API密钥（可选）
- `--extract_api_base`: 用于LLM提取答案的API基础URL（可选）
- `--extract_model`: 用于LLM提取答案的模型名称（默认：qwen-max）
- `--start_idx`: 开始评测的索引（默认：0）
- `--end_idx`: 结束评测的索引，-1表示评测到最后（默认：-1）
- `--categories`: 要评测的类别，多个类别用逗号分隔，为空表示评测所有类别（默认：""）

### 批处理脚本

Windows用户可以使用提供的批处理脚本：

```bash
run_evaluation.bat
```

### 结果分析

评测完成后，使用以下命令分析结果：

```bash
python analyze_results.py \
    --results_dir "results" \
    --output "analysis"
```

## 多模态评测

对于包含音频和图像的多模态评测，使用 `examples` 目录下的代码：

```bash
cd examples
python main.py
```

## 支持的模型

### OpenAI模型

配置示例 (`config/openai.json`):
```json
{
    "type": "openai",
    "model_name": "gpt-4",
    "api_key": "your_api_key_here",
    "api_base": null
}
```

### 通义千问模型

配置示例 (`config/qwen.json`):
```json
{
    "type": "qwen",
    "model_name": "qwen-max",
    "api_key": "your_api_key_here"
}
```

### 本地模型

配置示例 (`config/local.json`):
```json
{
    "type": "local",
    "model_name": "llama3-70b",
    "api_url": "http://localhost:8000/v1/chat/completions"
}
```

## 评测策略

### 直接回答 (Direct)

模型直接给出答案选项，不进行详细推理。

### 思维链 (Chain-of-Thought, CoT)

模型先进行逐步推理，然后给出答案。

### 专家提示 (Expert)

将模型设定为电气工程专家，以专家身份回答问题。

### 少样本学习 (Few-shot)

提供几个示例问题及其答案，引导模型按照类似方式回答。

## 数据集格式

评测数据集应为CSV格式，包含以下列：

- `Question`: 问题文本
- `Choices`: 选项文本
- `answer`: 正确答案
- `category`: 问题类别
- `imagepath`: 图片路径（可选）

## 结果输出

评测结果以JSON格式保存，包含：

- 模型名称
- 总平均分
- 各类别平均分
- 每道题的详细结果（问题、选项、正确答案、模型回答、得分等）

## 贡献指南

欢迎提交问题报告和功能请求！如果您想贡献代码，请：

1. Fork 本仓库
2. 创建您的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件至：your.email@example.com

## 致谢

感谢所有为本项目做出贡献的研究者和开发者。