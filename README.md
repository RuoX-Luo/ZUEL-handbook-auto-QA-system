# ZUEL-handbook-auto-QA-system 
# 中南财经政法大学学生自助问答手册
通过RAG（检索增强生成)，将中南财经政法大学学生手册2024作为知识库，引入GPT-4o-mini模型，制作成的校园学生手册自助问答系统

## 使用方法
1. 使用时打开`zuel_selfQA_system`文件夹所在终端  

2. 安装依赖：`pip install -r requirements.txt`  

3. 在`app.py`中替换 OpenAI API key  

4. 启动服务器：  
`uvicorn app:app --host 0.0.0.0 --port 8000`  

5. 这样设置后，用户可以通过浏览器访问 http://localhost:8000 来使用问答系统。  


### 系统特点：
1. 简洁的用户界面
2. 异步处理请求
3. 显示加载动画
4. 清晰展示答案和参考来源
5. 响应式设计，适配移动设备
