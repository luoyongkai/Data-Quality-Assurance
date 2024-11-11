from model.model import gpt,chat
from prompt.fact_check_prompt import prompt_extract_point,human_prompt,summary_prompt
import re
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

input_excel_path = r"C:\Users\你好\Desktop\新建 XLSX 工作表.xlsx"
output_excel_path = r"C:\Users\你好\Desktop\新建 XLSX 工作表.xlsx"

def process(prompt, answer):
    # 生成消息内容
    message = human_prompt.format(question_fact=prompt, answer_fact=answer)

    # 使用GPT生成文本
    text = gpt(system_prompt=prompt_extract_point, messages=message)

    # 分割句子
    sentences = [re.sub(r'^[^\u4e00-\u9fa5]*|[^\u4e00-\u9fa5]*$', '', s) for s in re.split(r'。', text)]


    # 对每个句子处理，并将原始句子和处理结果存储为字典
    sentence_results = [{'sentence': sentence.strip(), 'result': chat(sentence.strip())}
                        for sentence in sentences if sentence.strip()]


    print(sentence_results)

    # 使用GPT生成摘要
    summary_result = gpt(system_prompt=summary_prompt, messages=str(sentence_results))

    return summary_result




# 读取 Excel 文件
df = pd.read_excel(input_excel_path)

# 假设 Excel 文件中有一列名为 'prompt' 和 'answer'
prompts = df['prompt']
answers = df['answer']





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
        return pd.DataFrame({'事实理由': results})

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
df['事实结论'] = df['事实理由'].apply(extract_text_in_brackets)

# 保存结果到 Excel
df.to_excel(output_excel_path, index=False)