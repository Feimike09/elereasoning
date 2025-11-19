import pandas as pd
import re

def process_question_field(question_text):
    # 初始化结果字典
    result = {
        'Hint': '',
        'Question': '',
        'Choices': ''
    }
    
    # 分离Hint部分
    hint_match = re.search(r'Hint:(.*?)Question:', question_text, re.DOTALL)
    if hint_match:
        result['Hint'] = hint_match.group(1).strip()
    
    # 分离Question部分
    question_match = re.search(r'Question:(.*?)(?:Choices|Choice)s?:', question_text, re.DOTALL)
    if question_match:
        result['Question'] = question_match.group(1).strip()
    
    # 分离Choices部分
    choices_match = re.search(r'(?:Choices|Choice)s?:(.*)', question_text, re.DOTALL)
    if choices_match:
        result['Choices'] = choices_match.group(1).strip()
    
    return result

def main():
    # 读取CSV文件
    file_path = 'd:/eleeng_bench/elereasoning/datasets/elecbench.csv'
    df = pd.read_csv(file_path)
    
    # 处理question字段
    processed_data = []
    for index, row in df.iterrows():
        question_text = row['question']
        processed_fields = process_question_field(question_text)
        
        # 创建新行，包含原始数据和处理后的字段
        new_row = row.to_dict()
        new_row.update(processed_fields)
        processed_data.append(new_row)
    
    # 创建新的DataFrame
    processed_df = pd.DataFrame(processed_data)
    
    # 保存处理后的数据
    output_path = 'd:/eleeng_bench/elereasoning/datasets/elecbench_processed.csv'
    processed_df.to_csv(output_path, index=False)
    
    print(f"处理完成，结果已保存至 {output_path}")

if __name__ == "__main__":
    main()