import csv
import re
import os

def extract_answers_from_md(md_file):
    """从markdown文件中提取题目和答案信息"""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 按题目分割
    questions = re.split(r'---\s*\n', content)
    
    answers_dict = {}
    for question in questions:
        if not question.strip():
            continue
        
        # 提取题号和答案
        index_match = re.search(r'# index\s*\n(\d+)', question)
        answer_match = re.search(r'## answer\s*\n(.+?)(?=\n##|\Z)', question, re.DOTALL)
        question_match = re.search(r'## question\s*\n(.+?)(?=\n##|\Z)', question, re.DOTALL)
        
        if index_match and answer_match and question_match:
            index = index_match.group(1).strip()
            answer = answer_match.group(1).strip()
            question_text = question_match.group(1).strip()
            
            # 提取试题编号
            question_id_match = re.search(r'【试题(\d+-\d+-\d+)】', question_text)
            question_id = question_id_match.group(1) if question_id_match else None
            
            answers_dict[index] = {
                'answer': answer,
                'question_id': question_id,
                'question_text': question_text
            }
    
    return answers_dict

def update_csv_with_answers(csv_file, answers_dict, output_file):
    """更新CSV文件中的答案字段"""
    rows = []
    updated_count = 0
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        rows.append(header)
        
        for row in reader:
            if len(row) >= 7:  # 确保行有足够的列
                index = row[0]
                question_text = row[5]
                
                # 尝试匹配题目
                matched = False
                for md_index, md_data in answers_dict.items():
                    # 检查问题文本是否相似
                    if similar_questions(question_text, md_data['question_text']):
                        row[2] = md_data['answer']  # 更新答案字段
                        matched = True
                        updated_count += 1
                        break
            
            rows.append(row)
    
    # 写入更新后的数据
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    
    return updated_count

def similar_questions(q1, q2):
    """判断两个问题是否相似"""
    # 移除格式标记和空白字符
    q1 = re.sub(r'【试题\d+-\d+-\d+】', '', q1)
    q1 = re.sub(r'<br>|\\n|\s+', '', q1)
    
    q2 = re.sub(r'【试题\d+-\d+-\d+】', '', q2)
    q2 = re.sub(r'<br>|\\n|\s+', '', q2)
    
    # 提取问题的主要部分（前30个字符）进行比较
    q1_start = q1[:min(30, len(q1))]
    q2_start = q2[:min(30, len(q2))]
    
    return q1_start in q2 or q2_start in q1

def main():
    md_file = r"d:\eleeng_bench\elereasoning\datasets\benchmark\output_from_json.md\modian.md"
    csv_file = r"d:\eleeng_bench\elereasoning\datasets\modian_question_fixed_final.csv"
    output_file = r"d:\eleeng_bench\elereasoning\datasets\modian_question_with_answers.csv"
    
    print("正在从Markdown文件提取答案...")
    answers_dict = extract_answers_from_md(md_file)
    print(f"共提取到 {len(answers_dict)} 个题目的答案")
    
    print("正在更新CSV文件...")
    updated_count = update_csv_with_answers(csv_file, answers_dict, output_file)
    print(f"成功更新了 {updated_count} 个题目的答案")
    print(f"更新后的文件已保存为: {output_file}")

if __name__ == "__main__":
    main()