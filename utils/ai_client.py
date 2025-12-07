# -*- coding: utf-8 -*-

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class OpenAIClient:
    def __init__(self, api_key: str, base_url: str, model: str):
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        self.model = model
    

    def process(self, query: str) -> str:
        system_prompt = f"""You are a helpful assistant"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                stream=False
            )
            result = response.choices[0].message.content

            return result

        except Exception as e:
            raise ValueError(e)

# if __name__ == "__main__":
#     api_key = os.getenv("OPENAI_API_KEY")
#     base_url = os.getenv("OPENAI_BASE_URL")
#     model = os.getenv("OPENAI_MODEL")

#     client = OpenAIClient(api_key, base_url, model)
#     print(client.process("你是谁？"))