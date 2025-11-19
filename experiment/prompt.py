# 直接回答策略的提示词
DIRECT_ZH = """
请回答以下电气工程问题。直接给出你认为正确的选项字母（如A、B、C或D）。

问题: {question}

选项:
{choices}

请直接回答选项字母。
"""

DIRECT_EN = """
Please answer the following electrical engineering question. Directly provide the letter of the option you think is correct (e.g., A, B, C, or D).

Question: {question}

Choices:
{choices}

Please directly answer with the option letter.
"""

# 思维链(CoT)策略的提示词
COT_ZH = """
请回答以下电气工程问题。请先分析问题，一步一步地思考，然后给出你认为正确的选项字母（如A、B、C或D）。

问题: {question}

选项:
{choices}

请先分析问题，然后给出你的答案。
"""

COT_EN = """
Please answer the following electrical engineering question. First analyze the problem step by step, then provide the letter of the option you think is correct (e.g., A, B, C, or D).

Question: {question}

Choices:
{choices}

Please analyze the problem first, then provide your answer.
"""

# 专家提示策略的提示词
EXPERT_ZH = """
你是一位经验丰富的电气工程专家，擅长解决各种电气工程问题。请回答以下问题，展示你的专业知识和分析能力。

问题: {question}

选项:
{choices}

请分析问题并给出正确答案，解释你的推理过程。最后，明确指出你选择的选项字母。
"""

EXPERT_EN = """
You are an experienced electrical engineering expert skilled in solving various electrical engineering problems. Please answer the following question, demonstrating your professional knowledge and analytical abilities.

Question: {question}

Choices:
{choices}

Please analyze the problem and provide the correct answer, explaining your reasoning process. Finally, clearly indicate the letter of your chosen option.
"""

# Few-shot示例
FEW_SHOT_EXAMPLES_ZH = """
示例1:
问题: 在下图所示的电路中，二极管的正向压降为0.7V，求输出电压Vo。
选项:
A. 2.3V
B. 3.0V
C. 3.7V
D. 4.3V

分析: 二极管导通时，阳极电压比阴极高0.7V。在此电路中，二极管阴极连接到输出端，阳极连接到+5V电源。因此，输出电压Vo = 5V - 0.7V = 4.3V。
答案: D

示例2:
问题: 在RC串联电路中，时间常数τ等于什么？
选项:
A. R/C
B. RC
C. 1/RC
D. C/R

分析: 时间常数τ定义为电阻R与电容C的乘积，表示电容充电至63.2%所需的时间。因此τ = RC。
答案: B
"""

FEW_SHOT_EXAMPLES_EN = """
Example 1:
Question: In the circuit shown below, the forward voltage drop of the diode is 0.7V. Find the output voltage Vo.
Choices:
A. 2.3V
B. 3.0V
C. 3.7V
D. 4.3V

Analysis: When a diode is conducting, its anode voltage is 0.7V higher than its cathode. In this circuit, the diode's cathode is connected to the output, and the anode is connected to the +5V supply. Therefore, the output voltage Vo = 5V - 0.7V = 4.3V.
Answer: D

Example 2:
Question: In an RC series circuit, the time constant τ equals what?
Choices:
A. R/C
B. RC
C. 1/RC
D. C/R

Analysis: The time constant τ is defined as the product of resistance R and capacitance C, representing the time required for the capacitor to charge to 63.2%. Therefore, τ = RC.
Answer: B
"""

# Few-shot策略的提示词
FEW_SHOT_ZH = """
请参考以下示例，回答电气工程问题：

{examples}

现在，请回答以下问题：

问题: {question}

选项:
{choices}

请分析问题并给出正确答案，解释你的推理过程。最后，明确指出你选择的选项字母。
"""

FEW_SHOT_EN = """
Please refer to the following examples to answer the electrical engineering question:

{examples}

Now, please answer the following question:

Question: {question}

Choices:
{choices}

Please analyze the problem and provide the correct answer, explaining your reasoning process. Finally, clearly indicate the letter of your chosen option.
"""

def format_prompt(strategy: str, question: str, choices: str, language: str = "zh") -> str:
    """
    根据策略和语言格式化提示词
    
    Args:
        strategy: 提示策略，可选值: "direct", "cot", "expert", "few-shot"
        question: 问题文本
        choices: 选项文本
        language: 语言，可选值: "zh", "en"
        
    Returns:
        格式化后的提示词
    """
    if strategy == "direct":
        template = DIRECT_ZH if language == "zh" else DIRECT_EN
    elif strategy == "cot":
        template = COT_ZH if language == "zh" else COT_EN
    elif strategy == "expert":
        template = EXPERT_ZH if language == "zh" else EXPERT_EN
    elif strategy == "few-shot":
        template = FEW_SHOT_ZH if language == "zh" else FEW_SHOT_EN
        examples = FEW_SHOT_EXAMPLES_ZH if language == "zh" else FEW_SHOT_EXAMPLES_EN
        return template.format(examples=examples, question=question, choices=choices)
    else:
        raise ValueError(f"不支持的提示策略: {strategy}")
    
    return template.format(question=question, choices=choices)