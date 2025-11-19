import os
import json
import pandas as pd
from tqdm import tqdm
from openai import OpenAI
import argparse
from typing import List, Dict, Any

# 创建智谱AI客户端
client = OpenAI(
    api_key="",
    base_url="https://open.bigmodel.cn/api/paas/v4/"
)


def extract_answer(text: str) -> List[str]:
    """从文本中提取答案选项"""
    import re

    # 尝试匹配常见的答案模式
    answer_patterns = [
        r'答案[是为]:?\s*([A-F])',
        r'选择[是为]:?\s*([A-F])',
        r'选项[是为]:?\s*([A-F])',
        r'Answer:?\s*([A-F])',
        r'The answer is:?\s*([A-F])',
        r'最终答案[是为]:?\s*([A-F])',
        r'Final answer:?\s*([A-F])',
        r'因此[，,]答案[是为]:?\s*([A-F])',
        r'所以[，,]答案[是为]:?\s*([A-F])',
        r'Therefore, the answer is:?\s*([A-F])',
    ]

    for pattern in answer_patterns:
        match = re.search(pattern, text)
        if match:
            return [match.group(1)]

    # 如果没有找到明确的答案标识，尝试查找最后出现的选项字母
    all_options = re.findall(r'[A-F]', text)
    if all_options:
        return [all_options[-1]]

    return []


def format_prompt(question: str, choices: str, hint: str = "") -> str:
    """格式化提示词"""
    prompt = f"""
请回答以下电气工程问题。请先分析问题，一步一步地思考，然后给出你认为正确的选项字母。

问题: {question}

选项:
{choices}

{hint}

请先分析问题，然后给出你的答案。最后明确指出选择哪个选项（A、B、C或D）。
"""
    return prompt


def calculate_score(model_ans: str, correct_ans: str) -> int:
    """计算得分"""
    if model_ans == correct_ans:
        return 1
    return 0


def run_test(dataset_path: str, output_path: str, model_name: str = "glm-4.1v-thinking-flashx"):
    # 检查是否存在未完成的测试结果
    results = []
    completed_indices = set()

    if os.path.exists(output_path):
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                previous_results = json.load(f)
                results = previous_results["results"]
                completed_indices = set(item["index"] for item in results)
                print(f"发现未完成的测试，已完成 {len(completed_indices)} 题")
        except Exception as e:
            print(f"读取之前的结果失败: {str(e)}")
            completed_indices = set()
    else:
        completed_indices = set()

    # 加载数据集
    df = pd.read_csv(dataset_path)
    results = []

    # 如果有之前的结果，加载进来
    # 如果存在已完成的测试结果，则加载之前的结果
    if completed_indices and 'previous_results' in locals():
        results = previous_results["results"]

    # 计算总题目数和已完成数
    total_questions = len(df)
    completed_count = len(completed_indices)
    remaining_questions = total_questions - completed_count

    print(f"\n总题目数: {total_questions}")
    print(f"已完成题目: {completed_count}")
    print(f"剩余题目: {remaining_questions}\n")

    # 使用剩余题目数创建进度条
    progress_bar = tqdm(
        total=remaining_questions,
        desc="测试进度",
        ncols=100,  # 设置进度条宽度
        unit="题"   # 设置单位
    )

    # 添加日志文件
    log_path = os.path.join(os.path.dirname(output_path), "test.log")

    def log_error(message: str):
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] {message}\n")

    def validate_data(df: pd.DataFrame) -> None:
        """验证数据集格式"""
        required_columns = ["index", "Question",
                            "Choices", "answer", "category"]
        missing_columns = [
            col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"数据集缺少必要的列: {', '.join(missing_columns)}")

    try:
        for _, row in df.iterrows():
            if row["index"] in completed_indices:
                continue

            try:
                # 处理单个题目
                question = row["Question"]
                choices = row["Choices"]
                correct_answer = row["answer"]
                category = row["category"]
                hint = row.get("Hint", "")
                image_path = row.get("imagepath", "")

                # 格式化提示词
                prompt = format_prompt(question, choices, hint)

                # 如果有图片，添加图片内容
                messages = []
                if image_path and image_path != "无":
                    # 构建完整的图片路径
                    full_image_path = os.path.join(
                        os.path.dirname(dataset_path), image_path)
                    if os.path.exists(full_image_path):
                        try:
                            # 读取图片为base64
                            import base64
                            with open(full_image_path, "rb") as image_file:
                                image_data = base64.b64encode(
                                    image_file.read()).decode('utf-8')

                            # 添加图片消息
                            messages.append({
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "请分析这张图片，然后我会给你具体的问题。"
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{image_data}"
                                        }
                                    }
                                ]
                            })
                        except Exception as e:
                            print(f"处理图片时出错 {full_image_path}: {str(e)}")
                            continue
                    else:
                        print(f"图片文件不存在: {full_image_path}")

                # 添加文本提示词
                messages.append({
                    "role": "user",
                    "content": prompt
                })

                # 调用模型获取回答
                try:
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=messages,
                        temperature=0.7,
                        max_tokens=12288,  # 设置最大token数
                        timeout=120  # 设置超时时间
                    )

                    model_response = response.choices[0].message.content

                    # 提取答案
                    extracted_answer = extract_answer(model_response)
                    model_answer = extracted_answer[0] if extracted_answer else ""

                    # 计算得分
                    score = calculate_score(model_answer, correct_answer)

                except Exception as e:
                    print(f"调用模型时出错: {str(e)}")
                    model_response = f"错误: {str(e)}"
                    model_answer = ""
                    score = 0

                # 记录结果
                result = {
                    "index": row["index"],
                    "question": question,
                    "choices": choices,
                    "correct_answer": correct_answer,
                    "model_response": model_response,
                    "extracted_answer": model_answer,
                    "score": score,
                    "category": category,
                    "image_path": image_path
                }

                results.append(result)

                # 打印当前结果
                print(
                    f"问题 {row['index']}: 正确答案={correct_answer}, 模型答案={model_answer}, 得分={score}")

                # 更新进度条
                progress_bar.update(1)
                progress_bar.set_postfix({
                    "当前题号": row["index"],
                    "得分": score
                })

                # 实时保存结果
                save_results(output_path, model_name, results)

            except Exception as e:
                print(f"\n处理题目 {row['index']} 时出错: {e}")
                continue

    except Exception as e:
        print(f"\n测试过程出现严重错误: {e}")
    finally:
        progress_bar.close()

    # 计算总分和各类别得分
    total_score = sum(item["score"] for item in results)
    average_score = round(total_score / len(results)
                          * 100, 2) if results else 0

    # 计算各类别得分
    category_scores = {}
    category_counts = {}

    for item in results:
        category = item["category"]
        score = item["score"]

        if category not in category_scores:
            category_scores[category] = 0
            category_counts[category] = 0

        category_scores[category] += score
        category_counts[category] += 1

    # 计算各类别平均分
    for category in category_scores:
        if category_counts[category] > 0:
            category_scores[category] = round(
                category_scores[category] / category_counts[category] * 100, 2)

    # 构建结果数据
    output_data = {
        "model_name": model_name,
        "average_score": average_score,
        "category_scores": category_scores,
        "results": results
    }

    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 保存到JSON文件
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

# 新增辅助函数


def calculate_average_score(results: List[Dict]) -> float:
    """计算平均分"""
    if not results:
        return 0.0
    total_score = sum(item["score"] for item in results)
    return round(total_score / len(results) * 100, 2)


def calculate_category_scores(results: List[Dict]) -> Dict[str, float]:
    """计算各类别得分"""
    category_scores = {}
    category_counts = {}

    for item in results:
        category = item["category"]
        score = item["score"]

        if category not in category_scores:
            category_scores[category] = 0
            category_counts[category] = 0

        category_scores[category] += score
        category_counts[category] += 1

    # 计算各类别平均分
    for category in category_scores:
        if category_counts[category] > 0:
            category_scores[category] = round(
                category_scores[category] / category_counts[category] * 100, 2)

    return category_scores


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="电气工程小批量测试")

    parser.add_argument("--dataset", type=str,
                        default="datasets/test.csv", help="数据集文件路径")
    parser.add_argument("--output", type=str,
                        default="results/test_results.json", help="输出文件路径")
    parser.add_argument("--model", type=str,
                        default="glm-4.1v-thinking-flashx", help="模型名称")

    return parser.parse_args()


def save_results(output_path: str, model_name: str, results: List[Dict]) -> None:
    """保存测试结果"""
    output_data = {
        "model_name": model_name,
        "average_score": calculate_average_score(results),
        "category_scores": calculate_category_scores(results),
        "results": results
    }

    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 保存到JSON文件
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    args = parse_args()

    # 确保路径是绝对路径
    dataset_path = os.path.join(r"D:\大论文资料\benchmark", args.dataset) if not os.path.isabs(
        args.dataset) else args.dataset
    output_path = os.path.join(r"D:\大论文资料\benchmark\elereasoning\experiment",
                               args.output) if not os.path.isabs(args.output) else args.output

    run_test(dataset_path, output_path, args.model)
