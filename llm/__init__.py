from langchain_community.chat_models import ChatZhipuAI
from dotenv import load_dotenv
load_dotenv()
import os

model = ChatZhipuAI(
    model=os.environ["ZHIPUAI_MODEL_NAME"],
    api_key=os.environ["ZHIPUAI_API_KEY"],
    max_tokens=4095

)

def main():
    print(model.invoke("hello, what today is today?"))
    
# python -m llm.base
if __name__ == "__main__":
    main()
