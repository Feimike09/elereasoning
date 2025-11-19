import os
import re
import json
import pandas as pd
from typing import List, Dict, Any, Union, Tuple
from openai import OpenAI

def extract_answer(text: str) -> List[str]:
    """
    从文本中提取答案选项（A, B, C, D, E, F）
    
    Args:
        text: 模型回答的文本
        
    Returns:
        提取出的答案选项列表
    """
    # 尝试匹配"答案是X"或"Answer: X"等模式
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
    
    # 如果没有找到明确的答案标识，则提取文本中的所有选项字母
    all_options = re.findall(r'[A-F]', text)
    
    # 去重并保持顺序
    seen = set()
    unique_options = []
    for option in all_options:
        if option not in seen:
            seen.add(option)
            unique_options.append(option)
    
    # 如果有多个选项，取最后出现的几个（通常是结论部分）
    if len(unique_options) > 3:  # 如果选项太多，可能是文本中的干扰项
        return unique_options[-3:]  # 取最后3个选项
    
    return unique_options

def extract_answer_llm(text: str, api_key: str, base_url: str = None, model: str = "qwen-max") -> List[str]:
    """
    使用LLM从文本中提取答案选项
    
    Args:
        text: 模型回答的文本
        api_key: API密钥
        base_url: API基础URL（可选）
        model: 使用的模型名称
        
    Returns:
        提取出的答案选项列表
    """
    prompt = f"""
你是一个专业的答案提取专家。请分析以下文本，识别模型选择的正确答案。
仅提取最终选择的答案选项字母（A/B/C/D/E/F）。

如果模型选择的答案是"A"，你应该返回["A"]的JSON格式。
如果模型选择的答案是"A/B"或"AB"，你应该返回["A", "B"]的JSON格式。

待分析文本:

{text}

说明:
1. 识别哪个选项被明确指出为正确答案
2. 忽略所有中间推理和分析
3. 仅返回JSON格式的字母列表
4. 确保大小写敏感（使用大写字母）

以有效的JSON格式返回，键名为"answer":
"""
    
    try:
        client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)
        
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        
        response_text = completion.choices[0].message.content
        
        # 尝试解析JSON
        try:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
                if "answer" in result and isinstance(result["answer"], list):
                    return result["answer"]
        except:
            pass
        
        # 如果JSON解析失败，尝试直接提取字母
        return extract_answer(response_text)
        
    except Exception as e:
        print(f"LLM提取答案失败: {e}")
        # 回退到正则表达式提取
        return extract_answer(text)

def calculate_single_score(model_ans: str, correct_ans: str) -> int:
    """
    计算单选题得分
    
    Args:
        model_ans: 模型回答
        correct_ans: 正确答案
        
    Returns:
        得分（0或1）
    """
    if model_ans == correct_ans:
        return 1
    return 0

def calculate_multi_score(model_ans: List[str], correct_ans: List[str]) -> float:
    """
    计算多选题得分
    
    Args:
        model_ans: 模型回答的选项列表
        correct_ans: 正确答案的选项列表
        
    Returns:
        得分（0到1之间的浮点数）
    """
    if not model_ans:
        return 0
    
    model_set = set(model_ans)
    correct_set = set(correct_ans)
    
    # 如果有错选，得0分
    if not model_set.issubset(correct_set):
        return 0
    
    # 计算正确选中的比例
    correct_count = len(model_set)
    total_correct = len(correct_set)
    
    if total_correct == 0:
        return 0
    
    score = correct_count / total_correct
    return round(score, 2)

def calculate_category_scores(results: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    计算各类别的平均分数
    
    Args:
        results: 评测结果列表
        
    Returns:
        各类别的平均分数字典
    """
    category_scores = {}
    category_counts = {}
    
    for item in results:
        category = item.get("category", "未分类")
        score = item.get("score", 0)
        
        if category not in category_scores:
            category_scores[category] = 0
            category_counts[category] = 0
        
        category_scores[category] += score
        category_counts[category] += 1
    
    # 计算平均分
    for category in category_scores:
        if category_counts[category] > 0:
            category_scores[category] = round(category_scores[category] / category_counts[category] * 100, 2)
    
    return category_scores

def save_results(results: List[Dict[str, Any]], model_name: str, output_path: str) -> None:
    """
    保存评测结果到JSON文件
    
    Args:
        results: 评测结果列表
        model_name: 模型名称
        output_path: 输出文件路径
    """
    # 计算总平均分
    total_score = sum(item.get("score", 0) for item in results)
    average_score = round(total_score / len(results) * 100, 2) if results else 0
    
    # 计算各类别平均分
    category_scores = calculate_category_scores(results)
    
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
    
    print(f"结果已保存到: {output_path}")
    print(f"总平均分: {average_score}%")
    print("各类别平均分:")
    for category, score in category_scores.items():
        print(f"  {category}: {score}%")

def load_dataset(file_path: str) -> pd.DataFrame:
    """
    加载数据集
    
    Args:
        file_path: 数据集文件路径
        
    Returns:
        加载的数据集DataFrame
    """
    if file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        return pd.read_excel(file_path)
    else:
        raise ValueError(f"不支持的文件格式: {file_path}")

def split_reasoning_answer(text: str) -> Tuple[str, str]:
    """
    将模型回答拆分为推理过程和最终答案
    
    Args:
        text: 模型回答的文本
        
    Returns:
        (推理过程, 最终答案)的元组
    """
    # 尝试查找常见的答案标识
    answer_markers = [
        r'答案[是为]:?\s*[A-F]',
        r'选择[是为]:?\s*[A-F]',
        r'Answer:?\s*[A-F]',
        r'The answer is:?\s*[A-F]',
        r'最终答案[是为]:?\s*[A-F]',
        r'Final answer:?\s*[A-F]',
        r'因此[，,]答案[是为]:?\s*[A-F]',
        r'所以[，,]答案[是为]:?\s*[A-F]',
        r'Therefore, the answer is:?\s*[A-F]',
    ]
    
    for marker in answer_markers:
        match = re.search(marker, text)
        if match:
            answer_start = match.start()
            reasoning = text[:answer_start].strip()
            answer = text[answer_start:].strip()
            return reasoning, answer
    
    # 如果没有找到明确的答案标识，尝试查找最后一段作为答案
    paragraphs = text.split('\n\n')
    if len(paragraphs) > 1:
        reasoning = '\n\n'.join(paragraphs[:-1]).strip()
        answer = paragraphs[-1].strip()
        return reasoning, answer
    
    # 如果没有明确的段落分隔，将最后一句作为答案
    sentences = re.split(r'[.!?。！？]', text)
    if len(sentences) > 1:
        reasoning = '.'.join(sentences[:-1]).strip()
        answer = sentences[-1].strip()
        return reasoning, answer
    
    # 如果无法分割，则整个文本既是推理也是答案
    return text, text