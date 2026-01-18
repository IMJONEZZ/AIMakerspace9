from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()


class ChatOpenAI:
    def __init__(self, model_name: str = "openai/gpt-oss-120b"):
        self.model_name = model_name
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if self.openai_api_key is None:
            print("f*** openai")
            pass

    def run(self, messages, text_only: bool = True, **kwargs):
        if not isinstance(messages, list):
            raise

        client = OpenAI(
            base_url="http://192.168.1.79:8080/v1",
        )
        response = client.chat.completions.create(
            model=self.model_name, messages=messages, **kwargs
        )

        if text_only:
            return response.choices[0].message.content

        return response
