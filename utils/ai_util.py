# -*- coding: utf-8 -*- 

from typing import Any, AsyncGenerator
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from core.config import settings
from core.logger import logger


class AIClient:
    """
    AI客户端类，用于与OpenAI API交互。
    """

    def __init__(self):
        self.model = ChatOpenAI(
            api_key=lambda: settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL,
            base_url=settings.OPENAI_BASE_URL,
            temperature=0.7,
            streaming=True
        )

    async def process(self, query: str)  -> AsyncGenerator[str, Any]:
        """
        处理查询并返回流式响应

        参数:
        - query (str): 用户查询。

        返回:
        - AsyncGenerator[str, Any]: 流式响应内容。
        """
        system_prompt = """你是一个有用的AI助手，可以帮助用户回答问题和提供帮助。请用中文回答用户的问题。"""

        try:
            # 使用LangChain的异步流式生成
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=query)
            ]
            
            # 使用LangChain的流式响应
            async for chunk in self.model.astream(messages):
                yield chunk.text

        except Exception as e:
            # 记录详细错误，返回友好提示
            logger.error(f"AI处理查询失败: {str(e)}")
            yield f"抱歉，处理您的请求时出现了错误: {str(e)}"