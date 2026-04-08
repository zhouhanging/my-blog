import os
import re
import requests
from dotenv import load_dotenv
from wechaty import Wechaty, Contact, Message
from wechaty_puppet import FileBox

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api")

current_blog_id = None

class MyBlogBot(Wechaty):
    async def on_message(self, msg: Message):
        global current_blog_id
        
        if msg.type() != Message.Type.MESSAGE_TYPE_TEXT:
            return
        
        talker = msg.talker()
        text = msg.text().strip()
        
        generate_match = re.match(r'^生成[：:]\s*(.+)$', text) or re.match(r'^生成\s+(.+)$', text)
        if generate_match:
            topic = generate_match.group(1).strip()
            await talker.say(f'收到！正在为你生成关于「{topic}」的博客，请稍候...')
            
            try:
                res = requests.post(f'{BACKEND_URL}/blogs/generate', json={'topic': topic})
                res.raise_for_status()
                blog = res.json()
                current_blog_id = blog['id']
                
                content = blog['content']
                preview = content[:800] + ('...\n\n' if len(content) > 800 else '\n\n')
                
                await talker.say(f'✅ 生成完成！\n\n主题：{blog["topic"]}\n\n预览：\n{preview}')
                await talker.say('请回复：\n- 「通过」直接推送\n- 「修改：xxx」提优化意见')
                
            except requests.exceptions.RequestException as e:
                await talker.say(f'❌ 生成失败：{str(e)}')
            except Exception as e:
                await talker.say(f'❌ 发生错误：{str(e)}')
        
        elif text == '通过' or text == '通过了':
            if not current_blog_id:
                await talker.say('没有待审核的博客，请先发送「生成：xxx」生成一篇')
                return
            
            await talker.say('正在推送...')
            try:
                res = requests.post(f'{BACKEND_URL}/blogs/{current_blog_id}/approve')
                res.raise_for_status()
                await talker.say('✅ 推送成功！博客和公众号已更新')
                current_blog_id = None
            except requests.exceptions.RequestException as e:
                await talker.say(f'❌ 推送失败：{str(e)}')
        
        elif text.startswith('修改'):
            if not current_blog_id:
                await talker.say('没有待优化的博客，请先发送「生成：xxx」生成一篇')
                return
            
            feedback_match = re.match(r'^修改[：:]\s*(.+)$', text) or re.match(r'^修改\s+(.+)$', text)
            if not feedback_match:
                await talker.say('请输入修改意见，格式：「修改：这里加个代码示例」')
                return
            
            feedback = feedback_match.group(1).strip()
            await talker.say(f'收到修改意见，正在优化...')
            
            try:
                res = requests.post(
                    f'{BACKEND_URL}/blogs/{current_blog_id}/optimize',
                    json={'blog_id': current_blog_id, 'feedback': feedback}
                )
                res.raise_for_status()
                blog = res.json()
                
                content = blog['content']
                preview = content[:800] + ('...\n\n' if len(content) > 800 else '\n\n')
                
                await talker.say(f'✅ 优化完成！\n\n预览：\n{preview}')
                await talker.say('请回复：\n- 「通过」直接推送\n- 「修改：xxx」继续提意见')
                
            except requests.exceptions.RequestException as e:
                await talker.say(f'❌ 优化失败：{str(e)}')
        
        elif text == '帮助' or text == 'help':
            help_text = """
🤖 AI 博客助手使用说明：

1️⃣ 生成博客
发送：「生成：Vue3 最佳实践」

2️⃣ 审核通过
发送：「通过」

3️⃣ 提修改意见
发送：「修改：这里加个代码示例」

4️⃣ 查看帮助
发送：「帮助」
            """.strip()
            await talker.say(help_text)

if __name__ == '__main__':
    print('🤖 AI 博客助手正在启动...')
    print('请扫描下方二维码登录微信：')
    bot = MyBlogBot()
    bot.run()
