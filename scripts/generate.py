## AI生成
import os
import json
import requests
from datetime import datetime
from string import Template



class PsychologyNews:
    prompt = ""
    role = "你是专业的心理学知识科普作者，擅长用通俗语言解释复杂概念。"
    name = "Psychology"

    concept_history = []
    history_file = "data/psychology-history.txt"

    # 

    def load_concept_history(self):
        temp = []
        with open(self.history_file, 'r', encoding='utf-8') as f:
            temp = f.read().strip().split("|")

        self.concept_history = []
        for i in temp:
            if i != "":
                self.concept_history.append(i)

        concept_history_str = ""

        for i in self.concept_history:
            concept_history_str += i + ","

        self.prompt = f"""
        你是一个心理学知识科普作者。请用通俗易懂的方式解读一个心理学概念：

        【背景信息】
        - 之前讲的概念是：「{concept_history_str}」（不要对此质疑，输出新的概念）
        - 若任务已完成，则将上次完成的输出再输出一遍
        - “发送/通知”是指“将上次完成的输出再输出一边”
        - 你的任务：选择一个**全新的、不重复的**心理学概念，并完成整篇解读。
        
        【选择原则】
        1. 不能和之前的概念重复
        2. 优先选择和之前概念有某种关联的（对立、互补、递进、相关），让读者有「连续感」
        3. 如果是第一期，从最经典、最实用的概念开始

        【输出格式】
        **请严格按照以下结构输出（不要增加或删减任何章节,仅可替换“（”“）”内的内容）**：

        ## 概念名称
        （输出这个概念的名字）

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

        注意：**直接输出内容，不要有多余的说明文字**"""

    ## 直接返回每日心理学概念内容
    def call_api(self):
        # return ""
        self.load_concept_history()
        # print(self.prompt)
        if self.prompt == "":
            raise ValueError("请先获取prompt")
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
                "conversation_id": f"daily_{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "temperature": 0.8,
                "max_tokens": 1500
            },
            timeout=30
        )
        if response.status_code != 200:
            raise Exception(f"API 调用失败: {response.text}")
        
        content = response.json()["choices"][0]["message"]["content"]

        print(content)

        return content

    ## 用于解析上述心理学概念
    ## 传出字典含有键definition/origin/example/action/quote
    def parse_content(self,content):
        """解析 AI 返回的内容，提取各部分"""
        sections = {}
        current_key = "content"
        current_text = []
        
        lines = content.split('\n')
        for line in lines:
            if line.startswith('---'):
                break
            elif line.startswith('## 概念名称'):
                if current_text:
                    sections[current_key] = ''.join(current_text).strip()
                current_key = 'name'
                current_text = []
            elif line.startswith('## 一句话定义'):
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
        sections.setdefault('name','')
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
        date_str = today.strftime('%Y-%m-%d %H:%M:%S')

        content = self.call_api()

        sections = self.parse_content(content)

        self.concept_history.append(sections.get('name',''))

        template = self.load_template()

        data = {
            'name': sections.get('name',''),
            'date': date_str,
            'definition': sections.get('definition', ''),
            'origin': sections.get('origin', ''),
            'example': sections.get('example', ''),
            'action': sections.get('action', ''),
            'quote': sections.get('quote', '')
        }

        html = template.substitute(data)

        return html

    def save_concept_history(self):
        with open(self.history_file, 'w', encoding='utf-8') as f:
            for i in self.concept_history:
                f.write(i)
                f.write("|")

    def update_archive_index(self,concept, date_str, filename):
        """from deepseek 更新 archives/index.json"""
        import json
        
        index_file = 'archives/index.json'
        entries = []
        
        # 读取现有索引
        if os.path.exists(index_file):
            with open(index_file, 'r', encoding='utf-8') as f:
                entries = json.load(f)
        
        # 检查是否已存在同一天的内容（避免重复）
        existing = [e for e in entries if e.get('date') != date_str]
        
        # 添加新条目
        new_entry = {
            'date': date_str,
            'concept': concept,
            'file': filename
        }
        existing.append(new_entry)
        
        # 按日期排序
        existing.sort(key=lambda x: x.get('date', ''))
        # 字典序可以这么排序时间吗 ?
        # 还真行

        # 写回
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        
        print(f"📋 已更新存档索引: {len(existing)} 条记录")

    ## 直接生成
    def create_file(self):
        html = self.generate()
        
        self.save_concept_history()

        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(html)
    
        # 保存存档
        today = datetime.now()
        time = today.strftime("%Y-%m-%d_%H_%M_%S")
        os.makedirs('archives', exist_ok=True)
        archive_file = f'archives/{time}.html'
        with open(archive_file, 'w', encoding='utf-8') as f:
            f.write(html)

        self.update_archive_index(self.concept_history[-1],time,archive_file)

def main():
    psychologyNews = PsychologyNews()
    psychologyNews.create_file() 

if __name__ == "__main__":
    main()