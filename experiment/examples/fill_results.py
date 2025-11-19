import os
import csv
import re

def extract_model_results(result_file):
    """从result.txt文件中提取各个模型的评测结果"""
    with open(result_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 使用更灵活的正则表达式匹配每个模型的结果块
    model_blocks = re.findall(r'================================== (.*?) ================================[=]*\s+• Overall Scores:\s+Chinese\s+Single: ([\d\.]+)\s+\|\s+Multi: ([\d\.]+)\s+English\s+Single: ([\d\.]+)\s+\|\s+Multi: ([\d\.]+)\s+(?:\( Chinese Details \)|〔 Chinese Details 〕).*?score\s+\| ([\d\.]+)\s+\| ([\d\.]+).*?Irony\s+\| ([\d\.]+)\s+\| ([\d\.]+).*?(?:Cultural Metaphor|Cultural Metaphor) \| ([\d\.]+)\s+\| ([\d\.]+).*?Pun\s+\| ([\d\.]+)\s+\| ([\d\.]+).*?(?:Analogy|Analogy)\s+\| ([\d\.]+)\s+\| ([\d\.]+).*?(?:Foreshadowing and Callback|Foreshadowing and Callback) \| ([\d\.]+)\s+\| ([\d\.]+).*?Others\s+\| ([\d\.]+)\s+\| ([\d\.]+).*?(?:Situational Contrast|Situational Contrast) \| ([\d\.]+)\s+\| ([\d\.]+).*?(?:\( English Details \)|〔 English Details 〕).*?score\s+\| ([\d\.]+)\s+\| ([\d\.]+).*?Irony\s+\| ([\d\.]+)\s+\| ([\d\.]+).*?(?:Cultural Metaphor|Cultural Metaphor) \| ([\d\.]+)\s+\| ([\d\.]+).*?Pun\s+\| ([\d\.]+)\s+\| ([\d\.]+).*?(?:Analogy|Analogy)\s+\| ([\d\.]+)\s+\| ([\d\.]+).*?(?:Foreshadowing and Callback|Foreshadowing and Callback) \| ([\d\.]+)\s+\| ([\d\.]+).*?Others\s+\| ([\d\.]+)\s+\| ([\d\.]+).*?(?:Situational Contrast|Situational Contrast) \| ([\d\.]+)\s+\| ([\d\.]+)', content, re.DOTALL)
    
    results = {}
    for block in model_blocks:
        model_prompt = block[0].strip()
        # 解析模型名称和提示类型
        parts = model_prompt.split()
        model_name = parts[0]
        prompt_type = parts[1] if len(parts) > 1 else "direct"
        
        # 存储结果
        if model_name not in results:
            results[model_name] = {}
        
        results[model_name][prompt_type] = {
            'zh_single_overall': float(block[1]),
            'zh_multi_overall': float(block[2]),
            'en_single_overall': float(block[3]),
            'en_multi_overall': float(block[4]),
            'zh_single_score': float(block[5]),
            'zh_multi_score': float(block[6]),
            'zh_single_irony': float(block[7]),
            'zh_multi_irony': float(block[8]),
            'zh_single_cultural': float(block[9]),
            'zh_multi_cultural': float(block[10]),
            'zh_single_pun': float(block[11]),
            'zh_multi_pun': float(block[12]),
            'zh_single_analogy': float(block[13]),
            'zh_multi_analogy': float(block[14]),
            'zh_single_foreshadowing': float(block[15]),
            'zh_multi_foreshadowing': float(block[16]),
            'zh_single_others': float(block[17]),
            'zh_multi_others': float(block[18]),
            'zh_single_situational': float(block[19]),
            'zh_multi_situational': float(block[20]),
            'en_single_score': float(block[21]),
            'en_multi_score': float(block[22]),
            'en_single_irony': float(block[23]),
            'en_multi_irony': float(block[24]),
            'en_single_cultural': float(block[25]),
            'en_multi_cultural': float(block[26]),
            'en_single_pun': float(block[27]),
            'en_multi_pun': float(block[28]),
            'en_single_analogy': float(block[29]),
            'en_multi_analogy': float(block[30]),
            'en_single_foreshadowing': float(block[31]),
            'en_multi_foreshadowing': float(block[32]),
            'en_single_others': float(block[33]),
            'en_multi_others': float(block[34]),
            'en_single_situational': float(block[35]),
            'en_multi_situational': float(block[36])
        }
    
    return results

def fill_csv_template(template_file, output_file, results):
    """将结果填入CSV模板"""
    # 读取模板
    rows = []
    with open(template_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    # 创建新的CSV内容
    new_rows = [rows[0]]  # 保留表头
    
    # 标准化模型名称映射
    model_name_map = {
        'qwen-omni-turbo-0119': 'Qwen-Omni',
        'Qwen2Audio': 'Qwen2-Audio',
        'Qwen1Audio': 'Qwen1-Audio',
        'BaichuanAudio': 'Baichuan-Audio',
        'glm-4-voice': 'GLM-4-Voice'
    }
    
    # 为每种提示类型计算平均值
    prompt_type_averages = {}
    
    # 处理每个模型的结果
    for model_name, prompt_types in results.items():
        # 标准化模型名称
        std_model_name = None
        for key, value in model_name_map.items():
            if key in model_name:
                std_model_name = value
                break
        
        if not std_model_name:
            std_model_name = model_name
        
        for prompt_type, data in prompt_types.items():
            # 初始化提示类型的平均值字典
            if prompt_type not in prompt_type_averages:
                prompt_type_averages[prompt_type] = {
                    'zh_single_sum': 0, 'zh_single_count': 0,
                    'zh_multi_sum': 0, 'zh_multi_count': 0,
                    'en_single_sum': 0, 'en_single_count': 0,
                    'en_multi_sum': 0, 'en_multi_count': 0
                }
            
            # 中文单轮
            zh_single_row = [std_model_name, prompt_type, 'ZH', 'single', '', 
                            data['zh_single_overall'], 
                            data['zh_single_analogy'], 
                            data['zh_single_irony'], 
                            data['zh_single_cultural'], 
                            data['zh_single_pun'], 
                            data['zh_single_foreshadowing'], 
                            data['zh_single_situational'], 
                            data['zh_single_others']]
            
            # 计算平均值
            mean = sum([float(x) for x in zh_single_row[5:-1]]) / 7
            zh_single_row.append(f"{mean:.9f}")
            new_rows.append(zh_single_row)
            
            # 累加到提示类型平均值
            prompt_type_averages[prompt_type]['zh_single_sum'] += data['zh_single_overall']
            prompt_type_averages[prompt_type]['zh_single_count'] += 1
            
            # 中文多轮
            zh_multi_row = ['', '', '', 'multi', '', 
                           data['zh_multi_overall'], 
                           data['zh_multi_analogy'], 
                           data['zh_multi_irony'], 
                           data['zh_multi_cultural'], 
                           data['zh_multi_pun'], 
                           data['zh_multi_foreshadowing'], 
                           data['zh_multi_situational'], 
                           data['zh_multi_others']]
            
            # 计算平均值
            mean = sum([float(x) for x in zh_multi_row[5:-1]]) / 7
            zh_multi_row.append(f"{mean:.9f}")
            new_rows.append(zh_multi_row)
            
            # 累加到提示类型平均值
            prompt_type_averages[prompt_type]['zh_multi_sum'] += data['zh_multi_overall']
            prompt_type_averages[prompt_type]['zh_multi_count'] += 1
            
            # 中文平均
            zh_mean_row = ['', '', '', 'mean', '']
            for i in range(5, len(zh_single_row)-1):
                zh_mean_row.append(f"{(float(zh_single_row[i]) + float(zh_multi_row[i])) / 2:.9f}")
            new_rows.append(zh_mean_row)
            
            # 英文单轮
            en_single_row = ['', '', 'EN', 'single', '', 
                            data['en_single_overall'], 
                            data['en_single_analogy'], 
                            data['en_single_irony'], 
                            data['en_single_cultural'], 
                            data['en_single_pun'], 
                            data['en_single_foreshadowing'], 
                            data['en_single_situational'], 
                            data['en_single_others']]
            
            # 计算平均值
            mean = sum([float(x) for x in en_single_row[5:-1]]) / 7
            en_single_row.append(f"{mean:.9f}")
            new_rows.append(en_single_row)
            
            # 累加到提示类型平均值
            prompt_type_averages[prompt_type]['en_single_sum'] += data['en_single_overall']
            prompt_type_averages[prompt_type]['en_single_count'] += 1
            
            # 英文多轮
            en_multi_row = ['', '', '', 'multi', '', 
                           data['en_multi_overall'], 
                           data['en_multi_analogy'], 
                           data['en_multi_irony'], 
                           data['en_multi_cultural'], 
                           data['en_multi_pun'], 
                           data['en_multi_foreshadowing'], 
                           data['en_multi_situational'], 
                           data['en_multi_others']]
            
            # 计算平均值
            mean = sum([float(x) for x in en_multi_row[5:-1]]) / 7
            en_multi_row.append(f"{mean:.9f}")
            new_rows.append(en_multi_row)
            
            # 累加到提示类型平均值
            prompt_type_averages[prompt_type]['en_multi_sum'] += data['en_multi_overall']
            prompt_type_averages[prompt_type]['en_multi_count'] += 1
            
            # 英文平均
            en_mean_row = ['', '', '', 'mean', '']
            for i in range(5, len(en_single_row)-1):
                en_mean_row.append(f"{(float(en_single_row[i]) + float(en_multi_row[i])) / 2:.9f}")
            new_rows.append(en_mean_row)
    
    # 添加每种提示类型的平均值到CSV
    new_rows.append([])  # 空行分隔
    new_rows.append(["提示类型平均值统计"])
    new_rows.append(["Prompt Type", "ZH Single", "ZH Multi", "EN Single", "EN Multi", "Overall"])
    
    for prompt_type, avg_data in prompt_type_averages.items():
        zh_single_avg = avg_data['zh_single_sum'] / avg_data['zh_single_count'] if avg_data['zh_single_count'] > 0 else 0
        zh_multi_avg = avg_data['zh_multi_sum'] / avg_data['zh_multi_count'] if avg_data['zh_multi_count'] > 0 else 0
        en_single_avg = avg_data['en_single_sum'] / avg_data['en_single_count'] if avg_data['en_single_count'] > 0 else 0
        en_multi_avg = avg_data['en_multi_sum'] / avg_data['en_multi_count'] if avg_data['en_multi_count'] > 0 else 0
        
        # 计算总体平均值
        overall_avg = (zh_single_avg + zh_multi_avg + en_single_avg + en_multi_avg) / 4
        
        new_rows.append([
            prompt_type, 
            f"{zh_single_avg:.4f}", 
            f"{zh_multi_avg:.4f}", 
            f"{en_single_avg:.4f}", 
            f"{en_multi_avg:.4f}",
            f"{overall_avg:.4f}"
        ])
    
    # 写入新的CSV文件
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(new_rows)
    
    print(f"结果已成功写入到 {output_file}")
    print(f"共提取了 {len(results)} 个模型的结果")
    for model, prompt_types in results.items():
        print(f"  - {model}: {list(prompt_types.keys())}")
    
    print("\n各提示类型的平均值:")
    for prompt_type, avg_data in prompt_type_averages.items():
        zh_single_avg = avg_data['zh_single_sum'] / avg_data['zh_single_count'] if avg_data['zh_single_count'] > 0 else 0
        zh_multi_avg = avg_data['zh_multi_sum'] / avg_data['zh_multi_count'] if avg_data['zh_multi_count'] > 0 else 0
        en_single_avg = avg_data['en_single_sum'] / avg_data['en_single_count'] if avg_data['en_single_count'] > 0 else 0
        en_multi_avg = avg_data['en_multi_sum'] / avg_data['en_multi_count'] if avg_data['en_multi_count'] > 0 else 0
        overall_avg = (zh_single_avg + zh_multi_avg + en_single_avg + en_multi_avg) / 4
        
        print(f"  - {prompt_type}:")
        print(f"      ZH Single: {zh_single_avg:.4f}")
        print(f"      ZH Multi:  {zh_multi_avg:.4f}")
        print(f"      EN Single: {en_single_avg:.4f}")
        print(f"      EN Multi:  {en_multi_avg:.4f}")
        print(f"      Overall:   {overall_avg:.4f}")

if __name__ == "__main__":
    result_file = r'D:\git_proj\Audio_Deep\answer_output\root\answer_output\result1.txt'
    template_file = r'D:\git_proj\Audio_Deep\answer_output\root\answer_output\examples.csv'
    output_file = r'D:\git_proj\Audio_Deep\answer_output\root\answer_output\filled_results1.csv'
    
    # 提取结果
    results = extract_model_results(result_file)
    
    # 填入模板
    fill_csv_template(template_file, output_file, results)