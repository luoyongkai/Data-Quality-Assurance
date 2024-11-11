from model.model import *
from prompt.language_prompt import *
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import re


input_excel_path = r"输入文件路径"
output_excel_path = r"输出文件路径"

# 读取 Excel 文件
df = pd.read_excel(input_excel_path)


# 定义你的 process 函数
def process(prompt, answer):
    # 假设 mes 和 gpt 已经定义
    message = mes.format(prompt_lang=prompt, answer_lang=answer)
    result = gpt(system_prompt=system_prompt, messages=message)
    return result


# 使用 ThreadPoolExecutor 来并发处理数据

# 使用 ThreadPoolExecutor 来并发处理数据
def extract_text_in_brackets(text):
    match = re.search(r'\[(.*?)\]', text)
    if match:
        return match.group(1)
    else:
        return "没有找到匹配的文本"

def process_data(prompts, answers, max_workers=10):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_index = {executor.submit(process, prompt, answer): index for index, (prompt, answer) in
                           enumerate(zip(prompts, answers))}
        results = [None] * len(prompts)

        for future in as_completed(future_to_index):
            index = future_to_index[future]
            try:
                result = future.result()
                results[index] = result
            except Exception as exc:
                print(f'Exception in processing row {index}: {exc}')
                results[index] = f'Exception: {exc}'

        # 将结果存入新列 '事实理由'
        return pd.DataFrame({'语言理由': results})

# 读取 Excel 文件
df = pd.read_excel(input_excel_path)

# 假设 Excel 文件中有一列名为 'prompt' 和 'answer'
prompts = df['prompt']
answers = df['answer']

# 处理数据
df_results = process_data(prompts, answers)

# 将处理结果合并到原始 DataFrame
df = pd.concat([df, df_results], axis=1)

# 提取括号内的文本到新列 '事实结论'
df['语言结论'] = df['语言理由'].apply(extract_text_in_brackets)

# 保存结果到 Excel
df.to_excel(output_excel_path, index=False)