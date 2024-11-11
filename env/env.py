import jupyter_client
import sys
from io import StringIO
import copy
import time
import nbformat
from functools import partial
import traceback
import re
import os
import json
def get_key_info(text):
    x = []
    for v in text.split('\n'):
        if "->" in v:
            x.append(v)
    return '\n'.join(x)
def strip_ansi(text):
    stripped = re.sub(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]', '', text)
    return stripped

def error_line(lines):
    error_hint = ""
    for line in ('\n'.join(lines)).split('\n'):
        if len(re.findall(r'\-\-\->', line.strip())) > 0:
            error_hint += '\n' + re.sub(r'.*\-\-\->', '', line).strip()
    return error_hint

class ExpEnv(object):
    def __init__(self,workspace, kernel_name='Python3', name = 'exp'):
        self.name = name
        self.workspace = workspace
        self.manager = jupyter_client.KernelManager(kernel_name = kernel_name)
        self.manager.start_kernel(cwd = self.workspace)
        self.client = self.manager.client()
        self.client.start_channels()
        self.nb_obj = nbformat.v4.new_notebook(nbformat_minor=0)
        self.max_length = 512
    def output_hook_default(self, exec_results,plain_text,msg):
        msg_type = msg["header"]["msg_type"]
        content = msg["content"]
        if msg_type == "stream":
            exec_results.append(nbformat.v4.new_output(msg_type, text = content['text'], name = content['name']))
            plain_text.append(content['text'])
        elif msg_type == "display_data":
            exec_results.append(nbformat.v4.new_output(msg_type , data = content['data']))
            plain_text.append(content['data'].get('text/plain',''))
        elif msg_type == "execute_result":
            exec_results.append(nbformat.v4.new_output(msg_type , data = content['data'], execution_count = content.get('execution_count')))
            plain_text.append(content['data'].get('text/plain',''))
        elif msg_type == "error":
            exec_results.append(nbformat.v4.new_output(msg_type , **content))
            plain_text.append("\n".join([get_key_info(strip_ansi(v)) for v in content["traceback"][:-1]]
                                        +[strip_ansi(content["traceback"][-1])]))
        if len(plain_text)>0 and len(plain_text[-1]) > self.max_length:
            plain_text[-1] = plain_text[-1][:self.max_length//2] +'\n(...)\n'+ plain_text[-1][-self.max_length//2:]
    def stdin_hook(self, msg):
        raise TimeoutError
    def interact(self, code, timeout=10):
        code_cell = nbformat.v4.new_code_cell(source = code)
        output_content = []
        try:
            self.client.execute_interactive(code,timeout=timeout,stdin_hook=self.stdin_hook,output_hook = partial(self.output_hook_default, code_cell.outputs, output_content))
        except TimeoutError:
            code_cell.outputs.append(nbformat.v4.new_output("error", traceback = str(traceback.format_exc()).split('\n'), ename = "TimeoutError"))
            output_content.append(str(traceback.format_exc()).strip().split('\n')[-1])
            self.manager.interrupt_kernel()
            time.sleep(0.5)
        self.nb_obj.cells.append(code_cell)
        return self.nb_obj.cells[-1], output_content
    def add_annotations(self,text):
        self.nb_obj.cells.append(nbformat.v4.new_markdown_cell(source = text))
        return self.nb_obj.cells[-1]
    def restart(self):
        self.nb_obj = nbformat.v4.new_notebook(nbformat_minor=0)
        self.manager.restart_kernel(cwd = self.workspace)
        time.sleep(0.2)
    def save(self, path='test.ipynb'):
        with open(self.workspace+'/'+path, 'w') as f:
            f.write(nbformat.writes(self.nb_obj))
    def close(self):
        self.client.stop_channels()
        self.manager.shutdown_kernel()
        del self.client
if __name__ == "__main__":
    # Env预设置

    env_path = "./ci_env"
    if not os.path.exists(env_path):
        os.makedirs(env_path)
    env = ExpEnv(env_path, kernel_name='python3')
    query = "result = 1 + 5\nresult\n"
    output_cell, output_content = env.interact(query)
    print(output_cell)
    print(output_content)
    env.close()
