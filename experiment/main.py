import os
import argparse
import json
import pandas as pd
from typing import Dict, Any, List
from tqdm import tqdm

from model import create_model, BaseModel
from utils import (
    extract_answer, 
    extract_answer_llm, 
    calculate_single_score, 
    calculate_multi_score,
    save_results,
    load_dataset,
    split_reasoning_answer
)
from prompt import format_prompt

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="电气工程评测系统")
    
    parser.add_argument("--dataset", type=str, required=True, help="数据集文件路径")
    parser.add_argument("--config", type=str, required=True, help="模型配置文件路径")
    parser.add_argument("--output", type=str, default="results", help="输出目录")
    parser.add_argument("--strategy", type=str, default="cot", 
                        choices=["direct", "cot", "expert", "few-shot"], 
                        help="提示策略")
    parser.add_argument("--language", type=str, default="zh", 
                        choices=["zh", "en"], 
                        help="提示语言")
    parser.add_argument("--llm_extract", action="store_true", 
                        help="使用LLM提取答案")
    parser.add_argument("--extract_api_key", type=str, default="", 
                        help="用于LLM提取答案的API密钥")
    parser.add_argument("--extract_api_base", type=str, default=None, 
                        help="用于LLM提取答案的API基础URL")
    parser.add_argument("--extract_model", type=str, default="qwen-max", 
                        help="用于LLM提取答案的模型名称")
    parser.add_argument("--start_idx", type=int, default=0, 
                        help="开始评测的索引")
    parser.add_argument("--end_idx", type=int, default=-1, 
                        help="结束评测的索引，-1表示评测到最后")
    parser.add_argument("--categories", type=str, default="", 
                        help="要评测的类别，多个类别用逗号分隔，为空表示评测所有类别")
    
    return parser.parse_args()

def load_config(config_path: str) -> Dict[str, Any]:
    """加载模型配置"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def run_evaluation(
    model: BaseModel,
    dataset: pd.DataFrame,
    strategy: str,
    language: str,
    llm_extract: bool,
    extract_api_key: str,
    extract_api_base: str,
    extract_model: str,
    start_idx: int = 0,
    end_idx: int = -1,
    categories: List[str] = None
) -> List[Dict[str, Any]]:
    """
    运行评测
    
    Args:
        model: 模型实例
        dataset: 数据集
        strategy: 提示策略
        language: 提示语言
        llm_extract: 是否使用LLM提取答案
        extract_api_key: 用于LLM提取答案的API密钥
        extract_api_base: 用于LLM提取答案的API基础URL
        extract_model: 用于LLM提取答案的模型名称
        start_idx: 开始评测的索引
        end_idx: 结束评测的索引，-1表示评测到最后
        categories: 要评测的类别列表，None表示评测所有类别
        
    Returns:
        评测结果列表
    """
    results = []
    
    # 处理索引范围
    if end_idx == -1 or end_idx >= len(dataset):
        end_idx = len(dataset) - 1
    
    # 筛选数据集
    filtered_dataset = dataset.iloc[start_idx:end_idx+1]
    
    # 如果指定了类别，进一步筛选
    if categories:
        filtered_dataset = filtered_dataset[filtered_dataset['category'].isin(categories)]
    
    for _, row in tqdm(filtered_dataset.iterrows(), total=len(filtered_dataset), desc="评测进度"):
        question = row["Question"]
        choices = row["Choices"]
        correct_answer = row["answer"]
        category = row["category"]
        image_path = row.get("imagepath", "")
        
        # 格式化提示词
        prompt = format_prompt(strategy, question, choices, language)
        
        # 如果有图片，添加图片路径提示
        if image_path and image_path != "无":
            prompt += f"\n\n请注意查看图片: {image_path}"
        
        try:
            # 调用模型获取回答
            response = model.chat(prompt)
            
            # 分离推理过程和答案
            reasoning, answer_text = split_reasoning_answer(response)
            
            # 提取答案
            if llm_extract and extract_api_key:
                extracted_answer = extract_answer_llm(
                    response, 
                    extract_api_key, 
                    extract_api_base, 
                    extract_model
                )
            else:
                extracted_answer = extract_answer(response)
            
            # 如果提取出多个答案，但题目是单选题，则取第一个
            if len(extracted_answer) > 1 and isinstance(correct_answer, str) and len(correct_answer) == 1:
                model_answer = extracted_answer[0]
            else:
                model_answer = extracted_answer
            
            # 计算得分
            if isinstance(correct_answer, str) and len(correct_answer) == 1:
                # 单选题
                score = calculate_single_score(
                    model_answer[0] if isinstance(model_answer, list) and model_answer else model_answer,
                    correct_answer
                )
            else:
                # 多选题
                correct_list = list(correct_answer) if isinstance(correct_answer, str) else correct_answer
                score = calculate_multi_score(model_answer, correct_list)
            
            # 记录结果
            result = {
                "question": question,
                "choices": choices,
                "correct_answer": correct_answer,
                "model_response": response,
                "reasoning": reasoning,
                "answer_text": answer_text,
                "extracted_answer": extracted_answer,
                "score": score,
                "category": category,
                "image_path": image_path
            }
            
            results.append(result)
            
        except Exception as e:
            print(f"评测题目时出错: {e}")
            # 记录错误结果
            result = {
                "question": question,
                "choices": choices,
                "correct_answer": correct_answer,
                "model_response": f"错误: {str(e)}",
                "reasoning": "",
                "answer_text": "",
                "extracted_answer": [],
                "score": 0,
                "category": category,
                "image_path": image_path,
                "error": str(e)
            }
            
            results.append(result)
    
    return results

def main():
    """主函数"""
    args = parse_args()
    
    # 加载配置
    config = load_config(args.config)
    
    # 创建模型
    model = create_model(config)
    
    # 加载数据集
    dataset = load_dataset(args.dataset)
    
    # 处理类别
    categories = [cat.strip() for cat in args.categories.split(",")] if args.categories else None
    
    # 运行评测
    results = run_evaluation(
        model=model,
        dataset=dataset,
        strategy=args.strategy,
        language=args.language,
        llm_extract=args.llm_extract,
        extract_api_key=args.extract_api_key,
        extract_api_base=args.extract_api_base,
        extract_model=args.extract_model,
        start_idx=args.start_idx,
        end_idx=args.end_idx,
        categories=categories
    )
    
    # 构建输出文件路径
    os.makedirs(args.output, exist_ok=True)
    output_file = os.path.join(
        args.output, 
        f"{model.model_name}_{args.strategy}_{args.language}.json"
    )
    
    # 保存结果
    save_results(results, model.model_name, output_file)

if __name__ == "__main__":
    main()