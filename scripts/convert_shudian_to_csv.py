import re
import csv
import os

def extract_data_from_md(md_file):
    """从markdown文件中提取数据"""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 按题目分割
    questions = re.split(r'---\s*\n', content)
    
    data = []
    for question in questions:
        if not question.strip():
            continue
        
        # 提取各个字段
        index_match = re.search(r'# index\s*\n(\d+)', question)
        imagepath_match = re.search(r'## imagepath\s*\n(.+?)(?=\n##|\Z)', question, re.DOTALL)
        question_match = re.search(r'## question\s*\n(.+?)(?=\n##|\Z)', question, re.DOTALL)
        choices_match = re.search(r'## choices\s*\n(.+?)(?=\n##|\Z)', question, re.DOTALL)
        category_match = re.search(r'## category\s*\n(.+?)(?=\n##|\Z)', question, re.DOTALL)
        
        if not (index_match and question_match):
            continue
        
        index = index_match.group(1).strip()
        
        # 处理图片路径
        imagepath = ""
        if imagepath_match:
            img_text = imagepath_match.group(1).strip()
            if "![" in img_text:
                img_match = re.search(r'!\[\]\((.*?)\)', img_text)
                if img_match:
                    # 提取图片路径并转换为相对路径
                    img_path = img_match.group(1)
                    img_path = img_path.replace("../all_images/", "")
                    imagepath = img_path
            elif img_text != "无":
                imagepath = img_text
        
        # 处理问题文本
        question_text = question_match.group(1).strip() if question_match else ""
        
        # 处理选项
        choices = choices_match.group(1).strip() if choices_match else ""
        
        # 处理类别
        category = category_match.group(1).strip() if category_match else ""
        
        # 提取答案（从choices字段）
        answer = choices
        
        # 从问题文本中分离选项
        choices_in_question = ""
        if "<br>A." in question_text or "\nA." in question_text:
            parts = re.split(r'<br>A\.|\nA\.', question_text, 1)
            if len(parts) > 1:
                question_text = parts[0].strip()
                choices_in_question = "A." + parts[1].strip()
        
        data.append({
            'index': index,
            'imagepath': imagepath,
            'answer': answer,
            'category': category,
            'hint': "",  # 数电题目没有提示
            'question': question_text,
            'choices': choices_in_question
        })
    
    return data

def write_to_csv(data, output_file):
    """将数据写入CSV文件"""
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['index', 'imagepath', 'answer', 'category', 'Hint', 'Question', 'Choices'])
        
        for item in data:
            writer.writerow([
                item['index'],
                item['imagepath'],
                item['answer'],
                item['category'],
                item['hint'],
                item['question'],
                item['choices']
            ])

def main():
    md_file = r"d:\eleeng_bench\elereasoning\datasets\benchmark\output_from_json.md\shudian.md"
    output_file = r"d:\eleeng_bench\elereasoning\datasets\shudian_converted.csv"
    
    data = extract_data_from_md(md_file)
    write_to_csv(data, output_file)
    
    print(f"转换完成！共处理了 {len(data)} 个题目。")
    print(f"输出文件：{output_file}")

if __name__ == "__main__":
    main()