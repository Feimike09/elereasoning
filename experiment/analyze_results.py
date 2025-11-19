import os
import json
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Any
import seaborn as sns

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="电气工程评测结果分析")
    
    parser.add_argument("--results_dir", type=str, required=True, help="结果目录路径")
    parser.add_argument("--output", type=str, default="analysis", help="分析结果输出目录")
    
    return parser.parse_args()

def load_results(file_path: str) -> Dict[str, Any]:
    """加载评测结果"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_results(results_files: List[str], output_dir: str) -> None:
    """分析评测结果"""
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 存储所有模型的结果
    all_models_data = []
    
    for file_path in results_files:
        # 加载结果
        results_data = load_results(file_path)
        model_name = results_data["model_name"]
        average_score = results_data["average_score"]
        category_scores = results_data["category_scores"]
        results = results_data["results"]
        
        # 收集模型数据
        model_data = {
            "model_name": model_name,
            "average_score": average_score,
            "category_scores": category_scores,
            "results_count": len(results),
            "correct_count": sum(1 for r in results if r["score"] > 0),
            "file_path": file_path
        }
        
        all_models_data.append(model_data)
        
        # 分析每个类别的得分
        categories = list(category_scores.keys())
        scores = list(category_scores.values())
        
        # 绘制类别得分柱状图
        plt.figure(figsize=(12, 6))
        plt.bar(categories, scores)
        plt.xlabel('类别')
        plt.ylabel('得分 (%)')
        plt.title(f'{model_name} - 各类别得分')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'{model_name}_category_scores.png'))
        plt.close()
        
        # 分析错误案例
        error_cases = [r for r in results if r["score"] == 0]
        if error_cases:
            error_df = pd.DataFrame([{
                "问题": e["question"],
                "正确答案": e["correct_answer"],
                "模型答案": e["extracted_answer"],
                "类别": e["category"]
            } for e in error_cases])
            
            error_df.to_csv(os.path.join(output_dir, f'{model_name}_error_cases.csv'), index=False, encoding='utf-8')
    
    # 比较不同模型的总体表现
    if len(all_models_data) > 1:
        # 创建比较表格
        comparison_df = pd.DataFrame([{
            "模型": d["model_name"],
            "平均得分 (%)": d["average_score"],
            "题目数量": d["results_count"],
            "正确题目数": d["correct_count"],
            "正确率 (%)": round(d["correct_count"] / d["results_count"] * 100, 2)
        } for d in all_models_data])
        
        comparison_df.to_csv(os.path.join(output_dir, 'model_comparison.csv'), index=False, encoding='utf-8')
        
        # 绘制模型比较柱状图
        plt.figure(figsize=(10, 6))
        plt.bar(comparison_df["模型"], comparison_df["平均得分 (%)"])
        plt.xlabel('模型')
        plt.ylabel('平均得分 (%)')
        plt.title('不同模型的平均得分比较')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'model_comparison.png'))
        plt.close()
        
        # 比较不同模型在各类别上的表现
        # 收集所有类别
        all_categories = set()
        for d in all_models_data:
            all_categories.update(d["category_scores"].keys())
        
        # 创建类别比较数据
        category_comparison = {cat: [] for cat in all_categories}
        model_names = []
        
        for d in all_models_data:
            model_names.append(d["model_name"])
            for cat in all_categories:
                category_comparison[cat].append(d["category_scores"].get(cat, 0))
        
        # 绘制类别比较热图
        plt.figure(figsize=(12, 8))
        heatmap_data = pd.DataFrame(category_comparison, index=model_names)
        sns.heatmap(heatmap_data, annot=True, cmap="YlGnBu", fmt=".1f")
        plt.title('不同模型在各类别上的得分比较 (%)')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'category_comparison_heatmap.png'))
        plt.close()

def main():
    """主函数"""
    args = parse_args()
    
    # 获取结果文件列表
    results_files = [
        os.path.join(args.results_dir, f) 
        for f in os.listdir(args.results_dir) 
        if f.endswith('.json')
    ]
    
    if not results_files:
        print(f"在 {args.results_dir} 中未找到结果文件")
        return
    
    # 分析结果
    analyze_results(results_files, args.output)
    print(f"分析结果已保存到 {args.output} 目录")

if __name__ == "__main__":
    main()