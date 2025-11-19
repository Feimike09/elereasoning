import csv
import os
import re

def extract_filename(path):
    """从路径中提取文件名（不含扩展名）"""
    if not path or path == "无":
        return None
    
    # 提取最底层的文件名
    filename = os.path.basename(path)
    
    # 移除扩展名
    filename_without_ext = os.path.splitext(filename)[0]
    
    return filename_without_ext

def update_answers_by_image(csv_file, output_file):
    """根据imagepath匹配并更新answer字段"""
    # 读取CSV文件
    rows = []
    image_to_answer = {}
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        rows.append(header)
        
        # 第一遍：建立图片文件名到答案的映射
        for row in reader:
            if len(row) >= 7 and row[2]:  # 如果有答案
                imagepath = row[1]
                answer = row[2]
                
                filename = extract_filename(imagepath)
                if filename:
                    image_to_answer[filename] = answer
    
    # 重置文件指针
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # 跳过表头
        
        # 第二遍：更新没有答案的行
        for row in reader:
            if len(row) >= 7 and not row[2]:  # 如果没有答案
                imagepath = row[1]
                
                filename = extract_filename(imagepath)
                if filename and filename in image_to_answer:
                    row[2] = image_to_answer[filename]
            
            rows.append(row)
    
    # 写入更新后的数据
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    
    return len(image_to_answer)

def main():
    csv_file = r"d:\eleeng_bench\elereasoning\datasets\modian_question_with_answers.csv"
    output_file = r"d:\eleeng_bench\elereasoning\datasets\modian_question_with_answers_updated.csv"
    
    print("正在根据图片文件名匹配答案...")
    matched_count = update_answers_by_image(csv_file, output_file)
    print(f"共找到 {matched_count} 个图片文件名与答案的匹配")
    print(f"更新后的文件已保存为: {output_file}")

if __name__ == "__main__":
    main()