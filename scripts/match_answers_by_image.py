import csv
import re
import os

def extract_answers_from_md(md_file):
    """从markdown文件中提取图片路径和对应的答案"""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 按题目分割
    questions = re.split(r'---\s*\n', content)
    
    image_to_answer = {}
    for question in questions:
        if not question.strip():
            continue
        
        # 提取图片路径
        image_match = re.search(r'## imagepath\s*\n(!\[\]\(.*?\))', question, re.DOTALL)
        if not image_match:
            continue
        
        image_path = image_match.group(1).strip()
        
        # 提取答案
        answer_match = re.search(r'## answer\s*\n(.+?)(?=\n##|\Z)', question, re.DOTALL)
        if not answer_match:
            continue
        
        answer = answer_match.group(1).strip()
        
        # 将图片路径和答案关联起来
        image_to_answer[image_path] = answer
    
    return image_to_answer

def update_csv_with_answers(csv_file, image_to_answer, output_file):
    """根据图片路径更新CSV文件中的答案"""
    rows = []
    updated_count = 0
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        rows.append(header)
        
        for row in reader:
            if len(row) >= 7:  # 确保行有足够的列
                imagepath = row[1]
                
                # 构建与MD文件中相同格式的图片路径
                if imagepath and imagepath != "无":
                    # 提取文件名
                    filename = os.path.basename(imagepath)
                    md_image_path = f"![](../all_images/modian_images/{filename})"
                    
                    # 查找匹配的答案
                    if md_image_path in image_to_answer:
                        row[2] = image_to_answer[md_image_path]  # 更新答案字段
                        updated_count += 1
            
            rows.append(row)
    
    # 写入更新后的数据
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    
    return updated_count

def main():
    md_file = r"d:\eleeng_bench\elereasoning\datasets\benchmark\output_from_json.md\modian.md"
    csv_file = r"d:\eleeng_bench\elereasoning\datasets\modian_question_with_answers.csv"
    output_file = r"d:\eleeng_bench\elereasoning\datasets\modian_question_with_answers_updated.csv"
    
    print("正在从Markdown文件提取答案...")
    image_to_answer = extract_answers_from_md(md_file)
    print(f"共提取到 {len(image_to_answer)} 个图片路径和答案的对应关系")
    
    print("正在更新CSV文件...")
    updated_count = update_csv_with_answers(csv_file, image_to_answer, output_file)
    print(f"成功更新了 {updated_count} 个题目的答案")
    print(f"更新后的文件已保存为: {output_file}")

if __name__ == "__main__":
    main()