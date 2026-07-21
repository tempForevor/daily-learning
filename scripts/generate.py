## 大部分为AI生成的
import os
import json
import requests
from datetime import datetime
from string import Template



class PsychologyNews:
    prompt = f"""你是一个心理学知识科普作者。请用通俗易懂的方式解读一个心理学概念（请由你随机选定，需要每天都不一样）：

    请按以下格式输出（严格遵守）：

    ## 一句话定义
    （用一句话说清楚这个概念是什么）

    ## 经典来源 / 背景
    （这个概念的提出者、实验或理论背景，100字左右）

    ## 生活例子
    （一个具体的、贴近日常的例子，让人一听就懂）

    ## 今日行动处方
    （一个今天就能做的具体行动建议）

    ## 今日金句
    （一句帮你记住这个概念的话，20字以内）

    注意：直接输出内容，不要有多余的说明文字。"""
    role = "你是专业的心理学知识科普作者，擅长用通俗语言解释复杂概念。"
    name = "Psychology"

    ## 直接返回每日心理学概念内容
    def call_api(self):
        # return ""
        ## 目前使用api : clawbrain-flash
        ## 未来计划 : gemeni || cloudflare
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("请设置 DEEPSEEK_API_KEY 环境变量")
        response = requests.post(
            "	https://api.factorhub.cn/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "clawbrain-flash",
                "messages": [
                    {"role": "system", "content": self.role},
                    {"role": "user", "content": self.prompt}
                ],
                "temperature": 0.8,
                "max_tokens": 1500
            },
            timeout=30
        )
        if response.status_code != 200:
            raise Exception(f"API 调用失败: {response.text}")
        
        return response.json()["choices"][0]["message"]["content"]

    ## 用于解析上述心理学概念
    ## 传出字典含有键definition/origin/example/action/quote
    def parse_content(self,content):
        """解析 AI 返回的内容，提取各部分"""
        sections = {}
        current_key = "content"
        current_text = []
        
        lines = content.split('\n')
        for line in lines:
            if line.startswith('## 一句话定义'):
                if current_text:
                    sections[current_key] = '\n'.join(current_text).strip()
                current_key = 'definition'
                current_text = []
            elif line.startswith('## 经典来源'):
                if current_text:
                    sections[current_key] = '\n'.join(current_text).strip()
                current_key = 'origin'
                current_text = []
            elif line.startswith('## 生活例子'):
                if current_text:
                    sections[current_key] = '\n'.join(current_text).strip()
                current_key = 'example'
                current_text = []
            elif line.startswith('## 今日行动处方'):
                if current_text:
                    sections[current_key] = '\n'.join(current_text).strip()
                current_key = 'action'
                current_text = []
            elif line.startswith('## 今日金句'):
                if current_text:
                    sections[current_key] = '\n'.join(current_text).strip()
                current_key = 'quote'
                current_text = []
            else:
                current_text.append(line)
        
        if current_text:
            sections[current_key] = '\n'.join(current_text).strip()
        
        # 补全缺失字段
        sections.setdefault('definition', '')
        sections.setdefault('origin', '')
        sections.setdefault('example', '')
        sections.setdefault('action', '')
        sections.setdefault('quote', '')
        
        return sections
    
    ## 加载模板文件
    def load_template(self):
        template_path = "templates/" + self.name + ".html"
        with open(template_path, 'r', encoding='utf-8') as f:
            return Template(f.read())

     ## 返回对应网页html文本
    def generate(self):
        today = datetime.now()
        date_str = today.strftime('%Y/%m/%d')

        content = self.call_api()

        sections = self.parse_content(content)

        template = self.load_template()

        data = {
            'date': date_str,
            'definition': sections.get('definition', ''),
            'origin': sections.get('origin', ''),
            'example': sections.get('example', ''),
            'action': sections.get('action', ''),
            'quote': sections.get('quote', '')
        }

        html = template.substitute(data)

        return html

    ## 直接生成
    def create_file(self):
        html = self.generate()
        
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(html)
    
        # 保存存档
        today = datetime.now()
        os.makedirs('archives', exist_ok=True)
        archive_file = f'archives/{today.strftime("%Y-%m-%d")}.html'
        with open(archive_file, 'w', encoding='utf-8') as f:
            f.write(html)

def main():
    psychologyNews = PsychologyNews()
    psychologyNews.create_file() 

if __name__ == "__main__":
    main()