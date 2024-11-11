from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import re
from model.model import *
from prompt.spell_check_prompt import *

input_excel_path = r"输入文件路径"
output_excel_path = r"输出文件路径"

# 读取 Excel 文件
df = pd.read_excel(input_excel_path)

# 定义 process 函数，仅处理 answer 列
def process(answer):
    # 假设 mes 和 gpt 已经定义
    message = mes.format(prompt1=answer)
    result = gpt(system_prompt=system_prompt, messages=message)
    return result

# 提取括号内的文本
def extract_text_in_brackets(text):
    match = re.search(r'\[(.*?)\]', text)
    return match.group(1) if match else "没有找到匹配的文本"

# 使用 ThreadPoolExecutor 来并发处理 answer 列
def process_data(answers, max_workers=10):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_index = {executor.submit(process, answer): index for index, answer in enumerate(answers)}
        results = [None] * len(answers)

        for future in as_completed(future_to_index):
            index = future_to_index[future]
            try:
                result = future.result()
                results[index] = result
            except Exception as exc:
                print(f'Exception in processing row {index}: {exc}')
                results[index] = f'Exception: {exc}'

        # 返回处理结果的 DataFrame
        return pd.DataFrame({'错别字理由': results})

# 处理数据，仅传入 answer 列
answers = df['answer']
df_results = process_data(answers)

# 将处理结果合并到原始 DataFrame
df = pd.concat([df, df_results], axis=1)

# 提取括号内的文本到新列 '语言结论'
df['错别字结论'] = df['错别字理由'].apply(extract_text_in_brackets)

# 保存结果到 Excel
df.to_excel(output_excel_path, index=False)