import csv
import re

def process_csv(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        # 写入表头
        header = next(reader)
        writer.writerow(header)
        
        for row in reader:
            if len(row) >= 6:  # 确保行有足够的列
                # 处理问题文本
                question = row[5]
                
                # 替换"如图X.X.X所示"为"如图所示"
                question = re.sub(r'如图\d+\.\d+\.\d+所示', '如图所示', question)
                
                # 去掉开头的"如图所示"
                if question.startswith("如图所示"):
                    question = question[4:]  # 移除前4个字符
                
                row[5] = question
            
            writer.writerow(row)

if __name__ == "__main__":
    input_file = r"d:\eleeng_bench\elereasoning\datasets\modian_question_fixed.csv"
    output_file = r"d:\eleeng_bench\elereasoning\datasets\modian_question_fixed_new.csv"
    process_csv(input_file, output_file)
    print("处理完成！新文件已保存为:", output_file)