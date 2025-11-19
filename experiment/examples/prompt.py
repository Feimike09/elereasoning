DIRECT_SINGLE_ZH = """
请尝试根据提供的音频回答下面的单答案选择题。
{question}
{choices}
所以答案是:
"""

DIRECT_SINGLE_EN = """
Please try to answer the single-answer multiple choice question below based on the audio provided.
{question}
{choices}
So the answer is:
"""

DIRECT_MULTIPLE_ZH = """
请尝试根据提供的音频回答下面的多答案选择题。
{question}
{choices}
所以答案是:
"""

DIRECT_MULTIPLE_EN = """
Please try to answer the multiple-answer multiple choice question below based on the audio provided.
{question}
{choices}
So the answer is:
"""

COT_SINGLE_ZH = """
请尝试根据提供的音频回答下面的单答案选择题。
让我们仔细考虑一下每个选项。让我们一步一步来思考。
{question}
{choices}
"""

COT_SINGLE_EN = """
Please try to answer the single-answer multiple choice question below based on the audio provided.
Let's think through each option. Let's think step by step.
{question}
{choices}
"""

COT_MULTIPLE_ZH = """
请尝试根据提供的音频回答下面的多答案选择题。
让我们仔细考虑一下每个选项。让我们一步一步来思考。
{question}
{choices}
"""

COT_MULTIPLE_EN = """
Please try to answer the multiple-answer multiple choice question below based on the audio provided.
Let's think through each option. Let's think step by step.
{question}
{choices}
"""


XLT_SINGLE_EN = """
I want you to act as an audio reasoning expert for Chinese.
Question: Single choice, Which of the following best illustrates the underlying joke in the story?
{question}
{choices}
You should retell the Question in English.
You should do step-by-step answer to obtain a option answer .
You should step-by-step answer the question.
"""

XLT_SINGLE_ZH = """
我希望你能充当一名英文音频推理专家。
问题：单选，以下哪一项最能体现该段故事中的隐含笑点？
{question}
{choices}
你应该用英文重新叙述问题。
你应该逐步回答问题以获得一个最佳选项答案。
你应该逐步回答问题。
"""

XLT_MULTIPLE_EN = """
I want you to act as an audio reasoning expert for Chinese.
Question: Multiple choice, Which of the following best illustrates the underlying joke in the story?
{question}
{choices}
You should retell the Question in English.
You should do step-by-step answer to obtain multiple option answers.
You should step-by-step answer the question.
"""

XLT_MULTIPLE_ZH = """
我希望你能充当一名英文音频推理专家。
问题：多选，以下哪几项最能体现该段故事中的隐含笑点？
{question}
{choices}
你应该用英文重新叙述问题。
你应该逐步回答问题以获得多个最佳选项答案。
你应该逐步回答问题。
"""


KEY_SINGLE_ZH = """
请作为一名音频分析专家，分析以下音频中的关键幽默元素。
让我们按以下步骤分析：
1. 识别故事的主要场景和背景
2. 找出故事中的转折或对比点
3. 定位幽默的来源
4. 考虑是否存在讽刺或反讽
5. 选择最能体现这些元素的选项

{question}
{choices}
"""

KEY_SINGLE_EN = """
Please act as an audio analysis expert to identify the key humorous elements in the following audio.
Let's analyze using these steps:
1. Identify the main scene and context
2. Find the turning point or contrast
3. Locate the source of humor
4. Consider any irony or sarcasm
5. Select the option that best captures these elements

{question}
{choices}
"""

KEY_MULTIPLE_ZH = """
请作为一名音频分析专家，分析以下音频中的多个关键幽默元素。
让我们按以下步骤分析：
1. 识别故事的主要场景和背景
2. 找出故事中的转折或对比点
3. 定位多个幽默来源
4. 考虑是否存在讽刺或反讽
5. 选择所有能体现这些元素的选项

{question}
{choices}
"""

KEY_MULTIPLE_EN = """
Please act as an audio analysis expert to identify multiple key humorous elements in the following audio.
Let's analyze using these steps:
1. Identify the main scene and context
2. Find the turning points or contrasts
3. Locate multiple sources of humor
4. Consider any irony or sarcasm
5. Select all options that capture these elements

{question}
{choices}
"""

CLASS_SINGLE_ZH = """
请作为一名幽默分类专家，分析以下音频中使用的主要幽默手法。
分析步骤：
1. 确定故事的主要场景和背景
2. 识别幽默的表现手法
3. 分析幽默的类型（如反讽、夸张、对比等）
4. 考虑文化和社会背景
5. 选择最符合的幽默分类

{question}
{choices}
"""

CLASS_SINGLE_EN = """
Please act as a humor classification expert to analyze the main humorous technique used in the following audio.
Analysis steps:
1. Determine the main scene and background
2. Identify the humorous expression technique
3. Analyze the type of humor (e.g., irony, exaggeration, contrast)
4. Consider cultural and social context
5. Select the most appropriate humor classification

{question}
{choices}
"""

CLASS_MULTIPLE_ZH = """
请作为一名幽默分类专家，分析以下音频中使用的多种幽默手法。
分析步骤：
1. 确定故事的主要场景和背景
2. 识别多种幽默的表现手法
3. 分析各种幽默类型（如反讽、夸张、对比等）
4. 考虑文化和社会背景
5. 选择所有符合的幽默分类

{question}
{choices}
"""

CLASS_MULTIPLE_EN = """
Please act as a humor classification expert to analyze multiple humorous techniques used in the following audio.
Analysis steps:
1. Determine the main scene and background
2. Identify multiple humorous expression techniques
3. Analyze various types of humor (e.g., irony, exaggeration, contrast)
4. Consider cultural and social context
5. Select all appropriate humor classifications

{question}
{choices}
"""

FEW_SHOT_SINGLE_ZH = """请根据以下示例回答单选题：
{examples}

现在请回答这个问题（请只选择一个最佳答案）：
问题：{question}
选项：{choices}
请给出一个字母作为答案（如：A）。"""

FEW_SHOT_MULTIPLE_ZH = """请根据以下示例回答多选题：
{examples}

现在请回答这个问题（可以选择多个正确答案）：
问题：{question}
选项：{choices}
请给出多个字母作为答案，用逗号分隔（如：A,C,F）。"""

FEW_SHOT_SINGLE_EN = """Please answer the single-choice question based on these examples:
{examples}

Now please answer this question (select only ONE best answer):
Question: {question}
Choices: {choices}
Please provide your answer as a single letter (e.g., A)."""

FEW_SHOT_MULTIPLE_EN = """Please answer the multiple-choice question based on these examples:
{examples}

Now please answer this question (you can select MULTIPLE correct answers):
Question: {question}
Choices: {choices}
Please provide your answers as multiple letters separated by commas (e.g., A,C,F)."""

# 为三种不同的 few-shot 类型添加提示模板
FEW_SHOT1_SINGLE_ZH = """请根据以下示例回答单选题：
{examples}

现在请回答这个问题（请只选择一个最佳答案）：
问题：{question}
选项：{choices}
请给出一个字母作为答案（如：A）。"""

FEW_SHOT1_MULTIPLE_ZH = """请根据以下示例回答多选题：
{examples}

现在请回答这个问题（可以选择多个正确答案）：
问题：{question}
选项：{choices}
请给出多个字母作为答案，用逗号分隔（如：A,C,F）。"""

FEW_SHOT1_SINGLE_EN = """Please answer the single-choice question based on these examples:
{examples}

Now please answer this question (select only ONE best answer):
Question: {question}
Choices: {choices}
Please provide your answer as a single letter (e.g., A)."""

FEW_SHOT1_MULTIPLE_EN = """Please answer the multiple-choice question based on these examples:
{examples}

Now please answer this question (you can select MULTIPLE correct answers):
Question: {question}
Choices: {choices}
Please provide your answers as multiple letters separated by commas (e.g., A,C,F)."""

FEW_SHOT2_SINGLE_ZH = """请根据以下示例回答单选题（示例组2）：
{examples}

现在请回答这个问题（请只选择一个最佳答案）：
问题：{question}
选项：{choices}
请给出一个字母作为答案（如：A）。"""

FEW_SHOT2_MULTIPLE_ZH = """请根据以下示例回答多选题（示例组2）：
{examples}

现在请回答这个问题（可以选择多个正确答案）：
问题：{question}
选项：{choices}
请给出多个字母作为答案，用逗号分隔（如：A,C,F）。"""

FEW_SHOT2_SINGLE_EN = """Please answer the single-choice question based on these examples (example group 2):
{examples}

Now please answer this question (select only ONE best answer):
Question: {question}
Choices: {choices}
Please provide your answer as a single letter (e.g., A)."""

FEW_SHOT2_MULTIPLE_EN = """Please answer the multiple-choice question based on these examples (example group 2):
{examples}

Now please answer this question (you can select MULTIPLE correct answers):
Question: {question}
Choices: {choices}
Please provide your answers as multiple letters separated by commas (e.g., A,C,F)."""

FEW_SHOT3_SINGLE_ZH = """请根据以下示例回答单选题（示例组3）：
{examples}

现在请回答这个问题（请只选择一个最佳答案）：
问题：{question}
选项：{choices}
请给出一个字母作为答案（如：A）。"""

FEW_SHOT3_MULTIPLE_ZH = """请根据以下示例回答多选题（示例组3）：
{examples}

现在请回答这个问题（可以选择多个正确答案）：
问题：{question}
选项：{choices}
请给出多个字母作为答案，用逗号分隔（如：A,C,F）。"""

FEW_SHOT3_SINGLE_EN = """Please answer the single-choice question based on these examples (example group 3):
{examples}

Now please answer this question (select only ONE best answer):
Question: {question}
Choices: {choices}
Please provide your answer as a single letter (e.g., A)."""

FEW_SHOT3_MULTIPLE_EN = """Please answer the multiple-choice question based on these examples (example group 3):
{examples}

Now please answer this question (you can select MULTIPLE correct answers):
Question: {question}
Choices: {choices}
Please provide your answers as multiple letters separated by commas (e.g., A,C,F).
"""