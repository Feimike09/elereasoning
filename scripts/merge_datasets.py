import csv
import os

def merge_datasets(modian_file, elecbench_file, output_file):
    # 读取elecbench数据，了解其格式
    elecbench_data = []
    with open(elecbench_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)  # 获取表头
        for row in reader:
            elecbench_data.append(row)
    
    # 读取modian数据
    modian_data = []
    with open(modian_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # 跳过表头
        for row in reader:
            if len(row) >= 7:  # 确保行有足够的列
                modian_data.append(row)
    
    # 获取elecbench最大索引
    max_index = max([int(float(row[0])) for row in elecbench_data])
    
    # 转换modian数据为elecbench格式
    converted_modian_data = []
    for i, row in enumerate(modian_data):
        new_index = max_index + i + 1
        
        # 提取数据
        imagepath = row[1]
        answer = row[2] if row[2] else ""
        category = "ModianCircuit"  # 使用固定类别
        
        # 提示语
        hint = "请详细解答以下电路问题，包括必要的计算步骤、解释和推导过程。最后请明确给出答案（如A、B、C、D）。"
        
        # 问题和选项
        question = row[5]
        choices = row[6]
        
        # 创建新行
        new_row = [str(new_index), imagepath, answer, category, hint, question, choices]
        converted_modian_data.append(new_row)
    
    # 合并数据并写入新文件
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        
        # 写入原始elecbench数据
        for row in elecbench_data:
            writer.writerow(row)
        
        # 写入转换后的modian数据
        for row in converted_modian_data:
            writer.writerow(row)
    
    print(f"合并完成！共添加了 {len(converted_modian_data)} 条模电题目数据。")
    print(f"新文件已保存为: {output_file}")

if __name__ == "__main__":
    modian_file = r"d:\eleeng_bench\elereasoning\datasets\modian_question_fixed_final.csv"
    elecbench_file = r"d:\eleeng_bench\elereasoning\datasets\elecbench_choices_fixed.csv"
    output_file = r"d:\eleeng_bench\elereasoning\datasets\elecbench_merged.csv"
    
    merge_datasets(modian_file, elecbench_file, output_file)