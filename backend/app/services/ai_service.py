import os
from dotenv import load_dotenv
from langchain import LLMChain, PromptTemplate
from langchain_community.llms import Tongyi
from langchain_community.utilities import SerpAPIWrapper
from langchain.agents import initialize_agent, Tool, AgentType

load_dotenv()

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

llm = Tongyi(
    model="qwen-max",
    dashscope_api_key=DASHSCOPE_API_KEY,
    temperature=0.7
)

search = SerpAPIWrapper(serpapi_api_key=SERPAPI_API_KEY)
tools = [
    Tool(
        name="Search",
        func=search.run,
        description="用于搜索最新的相关信息，当需要实时数据或背景知识时使用"
    )
]

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

BLOG_GENERATE_PROMPT = """
你是一个专业的技术博客作者。请根据以下主题和搜索到的信息，生成一篇高质量的技术博客。

要求：
1. 结构清晰，包含标题、引言、正文、总结
2. 语言专业但易懂，适合技术读者
3. 包含代码示例（如果适用）
4. 字数在 1500-2500 字之间
5. 输出格式为 Markdown

主题：{topic}
搜索信息：{search_info}

请开始生成博客：
"""

BLOG_OPTIMIZE_PROMPT = """
你是一个专业的技术编辑。请根据以下反馈意见，优化这篇博客。

原始博客：
{content}

反馈意见：
{feedback}

请输出优化后的博客（Markdown 格式）：
"""

class AIService:
    @staticmethod
    async def generate_blog(topic: str) -> str:
        search_result = search.run(f"最新 {topic} 技术信息 最佳实践")
        
        prompt = PromptTemplate(
            input_variables=["topic", "search_info"],
            template=BLOG_GENERATE_PROMPT
        )
        
        chain = LLMChain(llm=llm, prompt=prompt)
        result = chain.run(topic=topic, search_info=search_result)
        
        return result

    @staticmethod
    async def optimize_blog(content: str, feedback: str) -> str:
        prompt = PromptTemplate(
            input_variables=["content", "feedback"],
            template=BLOG_OPTIMIZE_PROMPT
        )
        chain = LLMChain(llm=llm, prompt=prompt)
        result = chain.run(content=content, feedback=feedback)
        return result
