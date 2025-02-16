# app.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import torch
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from openai import OpenAI
import os
from pathlib import Path

# 初始化 FastAPI 应用
app = FastAPI(title="ZUEL Student Handbook QA System")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 基本配置
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
CURRENT_DIR = os.getcwd()
VECTOR_STORE_PATH = os.path.join(CURRENT_DIR, "vector_store")

# 初始化OpenAI客户端
client = OpenAI(
    api_key="sk-4ZSzhNuBKtIUzICHSKPAIkF4NwgaNFbuAgoWmpifgoQAS5RR",
    base_url="https://api.chatanywhere.tech/v1"
)

# 初始化嵌入模型
os.environ['TRANSFORMERS_CACHE'] = 'E:/ML/model_cache'
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-large-zh-v1.5",
    model_kwargs={'device': DEVICE},
    encode_kwargs={'normalize_embeddings': True}
)

# 加载向量存储
vector_store = Chroma(
    persist_directory=VECTOR_STORE_PATH,
    embedding_function=embeddings
)

class Question(BaseModel):
    text: str

def ask_gpt(question: str, context: str) -> str:
    """向 OpenAI GPT发送请求"""
    messages = [
        {"role": "system", "content": "你是中南财经政法大学的学生助手，请根据提供的学生手册内容回答问题。请确保回答准确、简洁，并严格基于提供的内容。"},
        {"role": "user", "content": f"""
相关内容：
{context}

问题：{question}
"""}
    ]
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )
        
        if response and response.choices:
            return response.choices[0].message.content.strip()
        else:
            return "抱歉，没有获得有效回答"
            
    except Exception as e:
        print(f"API调用错误: {str(e)}")
        return f"发生错误: {str(e)}"

@app.post("/api/ask")
async def ask_question(question: Question):
    try:
        # 检索相关文档
        docs = vector_store.similarity_search(question.text, k=3)
        context = "\n\n".join([doc.page_content for doc in docs]) if docs else "未找到相关内容"

        # 获取答案
        answer = ask_gpt(question.text, context)
        
        return {
            "answer": answer,
            "sources": [doc.page_content for doc in docs] if docs else []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 挂载静态文件
app.mount("/", StaticFiles(directory="static", html=True), name="static")