from model import GLM4Audio, Qwen1Audio, Qwen2Audio, GeminiAudio, BaichuanAudio,MiniCPMAudio,Qwen2AudioBase,Qwen25OmniAudio
from utils import extract_answer, extract_answer_llm, calculate_multi_score_iter, calculate_multi_score, calculate_single_score_iter,calculate_single_score
from prompt import *
import json
import os
import pandas as pd
from few_shot_examples import *

config = {
    'direct': {
        'zh': [DIRECT_SINGLE_ZH, DIRECT_MULTIPLE_ZH],
        'en': [DIRECT_SINGLE_EN, DIRECT_MULTIPLE_EN],
    },
    'cot': {
        'zh': [COT_SINGLE_ZH, COT_MULTIPLE_ZH],
        'en': [COT_SINGLE_EN, COT_MULTIPLE_EN],
    },
    'xlt': {
        'zh': [XLT_SINGLE_ZH, XLT_MULTIPLE_ZH],
        'en': [XLT_SINGLE_EN, XLT_MULTIPLE_EN],
    },
    'few-shot': {
        'zh': [FEW_SHOT_SINGLE_ZH, FEW_SHOT_MULTIPLE_ZH],
        'en': [FEW_SHOT_SINGLE_EN, FEW_SHOT_MULTIPLE_EN],
        'examples': FEW_SHOT_EXAMPLES
    },
    'few-shot1': {
        'zh': [FEW_SHOT1_SINGLE_ZH, FEW_SHOT1_MULTIPLE_ZH],
        'en': [FEW_SHOT1_SINGLE_EN, FEW_SHOT1_MULTIPLE_EN],
        'examples': FEW_SHOT_EXAMPLES1
    },
    'few-shot2': {
        'zh': [FEW_SHOT2_SINGLE_ZH, FEW_SHOT2_MULTIPLE_ZH],
        'en': [FEW_SHOT2_SINGLE_EN, FEW_SHOT2_MULTIPLE_EN],
        'examples': FEW_SHOT_EXAMPLES2
    },
    'few-shot3': {
        'zh': [FEW_SHOT3_SINGLE_ZH, FEW_SHOT3_MULTIPLE_ZH],
        'en': [FEW_SHOT3_SINGLE_EN, FEW_SHOT3_MULTIPLE_EN],
        'examples': FEW_SHOT_EXAMPLES3
    }
}

def build_few_shot_prompt(examples, current_question, current_choices, language='en'):
    prompt = "Please answer the following question based on these examples:\n\n"
    
    # 添加示例
    for idx, example_group in enumerate(examples, 1):
        prompt += f"Example Group {idx}:\n"
        for example in example_group['examples']:
            prompt += f"Question: {example['question']}\n"
            prompt += f"Choices:\n"
            for choice in example['choices']:
                prompt += f"{choice}\n"
            
            # 处理答案，确保多选题答案正确显示
            if isinstance(example['answer'], list):
                answer_str = ','.join(example['answer'])
                prompt += f"Answer: {answer_str}\n\n"
            else:
                prompt += f"Answer: {example['answer']}\n\n"
    
    # 添加当前问题
    prompt += f"Now, please answer this question:\n"
    prompt += f"Question: {current_question}\n"
    prompt += f"Choices:\n"
    for choice in current_choices.split('\n'):
        if choice.strip():  # 避免添加空行
            prompt += f"{choice}\n"
    
    # 明确指出可以选择多个答案
    if "multiple" in current_question.lower() or "multi" in current_question.lower():
        prompt += "\nYou can select multiple answers. Please format your answer as a comma-separated list (e.g., A,C,F).\n"
    
    return prompt

def run_experiment(model, df, task, path):
    for index, row in df.iterrows():
        # 假设实际提示信息在 single_question 列，根据实际情况修改
        prompt = row['single_question']
        audio_path = row['save_path']  # 假设音频路径在 save_path 列，根据实际情况修改
        language = row.get('Language', 'en')  # 假设语言信息在 Language 列，根据实际情况修改
        try:
            model_single_response_raw = model.chat(prompt, audio_path, language)
            # 后续处理逻辑
            # ...
        except Exception as e:
            print(f"处理音频 {audio_path} 时出错: {e}")
            continue

    """
    model: Model object
    df: DataFrame
    task: str
    path: str, path to audio files
    """
    if task == 'direct':
        prompts = config['direct']
    elif task == 'cot':
        prompts = config['cot']
    elif task == 'xlt':
        prompts = config['xlt']
    elif task == 'key':
        prompts = config['key']
    elif task == 'class':
        prompts = config['class']
    elif task == 'few-shot':
        prompts = config['few-shot']
    elif task == 'few-shot1':
        prompts = config['few-shot1']
    elif task == 'few-shot2':
        prompts = config['few-shot2']
    elif task == 'few-shot3':
        prompts = config['few-shot3']
    else:
        raise ValueError('Invalid task type. Must be one of: direct, cot, xlt, key, class, few-shot, few-shot1, few-shot2, few-shot3')
    
    if not os.path.exists('answer_output'):
        os.mkdir('answer_output')
    if not os.path.exists(f'answer_output/{task}'):
        os.mkdir(f'answer_output/{task}')
    
    # 初始化结果文件和路径
    filename = f'{model.model_name}_{task}.json'
    output_path = f'answer_output/{task}/{filename}'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 初始化或加载已有结果
    if os.path.exists(output_path):
        with open(output_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
            single_res = existing_data['single_res']
            multi_res = existing_data['multi_res']
    else:
        single_res = []
        multi_res = []
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                'task': task,
                'model_name': model.model_name,
                'single_score': None,
                'multi_score': None,
                'single_res': single_res,
                'multi_res': multi_res
            }, f, indent=4, ensure_ascii=False)

    def update_results():
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                'task': task,
                'model_name': model.model_name,
                'single_score': calculate_single_score_iter(single_res),
                'multi_score': calculate_multi_score_iter(multi_res),
                'single_res': single_res,
                'multi_res': multi_res
            }, f, indent=4, ensure_ascii=False)

    for i in range(238, len(df)):
        item = df.iloc[i]
        audio_path = path + '/' + item['save_path']
        print(audio_path)
        
        # 获取所有需要的变量
        single_question = item['single_question']
        single_select = item['single_choice']
        single_select_ans = item['single_answer']
        single_select_ans = extract_answer(single_select_ans)[0]

        multi_question = item['multiple_question']
        multi_select = item['multi_choice']
        multi_select_ans = item['multi_answer']
        multi_select_ans = extract_answer(multi_select_ans)
        
        label = item['humor_label']
        
        # 根据任务类型处理提示
        if task in ['few-shot', 'few-shot1', 'few-shot2', 'few-shot3']:
            # 构建few-shot提示并获取回答
            single_prompt = build_few_shot_prompt(
                examples=prompts['examples'],
                current_question=single_question,
                current_choices=single_select,
                language=item['Language']
            )
            
            model_single_response_raw = model.chat(
                prompt=single_prompt, 
                audio_path=audio_path
            )
            
            multi_prompt = build_few_shot_prompt(
                examples=prompts['examples'],
                current_question=multi_question,
                current_choices=multi_select,
                language=item['Language']
            )
            
            model_multi_response_raw = model.chat(
                prompt=multi_prompt, 
                audio_path=audio_path
            )
        else:
            # 使用标准提示格式
            if item['Language'] == 'zh':
                prompt = prompts['zh']
            else:
                prompt = prompts['en']
                
            model_single_response_raw = model.chat(
                prompt=prompt[0].format(question=single_question, choices=single_select), 
                audio_path=audio_path
            )
            
            model_multi_response_raw = model.chat(
                prompt=prompt[1].format(question=multi_question, choices=multi_select), 
                audio_path=audio_path
            )
        
        # 提取答案
        model_single_response = extract_answer_llm(model_single_response_raw)
        if not model_single_response:
            model_single_response = ''
        else:
            model_single_response = model_single_response[0]

        model_multi_response = extract_answer_llm(model_multi_response_raw)
        if not model_multi_response:
            model_multi_response = []
        
        # 计算分数
        single_score = calculate_single_score(model_single_response, single_select_ans)
        multi_score = calculate_multi_score(model_multi_response, multi_select_ans)

        single_res.append({
            'save_path': audio_path, 
            'model_ans_raw': model_single_response_raw,
            'model_ans': model_single_response, 
            'correct_ans': single_select_ans, 
            'label': label, 
            'language': item['Language'],
            'score': single_score,
        })

        multi_res.append({
            'save_path': audio_path, 
            'model_ans_raw': model_multi_response_raw,
            'model_ans': model_multi_response, 
            'correct_ans': multi_select_ans, 
            'label': label, 
            'language': item['Language'],
            'score': multi_score,
        })

        # 实时更新结果文件
        update_results()
        
        print(f'################## Question {i + 1} ##################')
        print(f"Langue: {item['Language']}")
        print('               Single Select Question')
        print(f'{model.model_name}: ', model_single_response)
        print('Correct Answer: ', single_select_ans)
        print('Score: ', single_score)

        print('               Multi Select Question')
        print(f'{model.model_name}: ', model_multi_response)
        print('Correct Answer: ', multi_select_ans)
        print('Score: ', multi_score)

    # 最终更新一次确保数据完整
    update_results()

    single_score = calculate_single_score_iter(single_res)
    multi_score = calculate_multi_score_iter(multi_res)

    result = {
        'task': task,
        'model_name': model.model_name,
        'single_score': single_score,
        'multi_score': multi_score,
        'single_res': single_res,
        'multi_res': multi_res,
    }

    # 根据任务类型生成不同的文件名
    filename = f'{model.model_name}_{task}.json'  # 统一格式为 模型名_任务名.json

    with open(f'answer_output/{task}/{filename}', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print(f'################## {task} Score ##################')
    print(f'{model.model_name} Single Select Score: {single_score:.2f}')
    print(f'{model.model_name} Multi Select Score: {multi_score:.2f}')

# 在 main 函数中添加保存结果到 few_shot.txt 的代码
if __name__ == '__main__':
    
    model = Qwen25OmniAudio(model_path='/root/autodl-tmp/qwenomin3b')
    df = pd.read_csv(r'/root/final_new_with_save_path.csv')
    path = r'/root/slice0215'
    for task in ['cot', 'xlt','few-shot1','few-shot2','few-shot3']:
        print(f"开始运行 {task} 模式...")
        run_experiment(model, df, task, path)
        print(f"{task} 模式运行完成\n")
    # task='direct'
    # run_experiment(model,df,task,path)