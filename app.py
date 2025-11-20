#!/usr/python3
import streamlit as st
import chromadb 
from pypdf import PdfReader
from openai import OpenAI
import os

# ------------页面配置----------

st.set_page_config(page_title="pdf智能问答助手",layout="wide")
st.title("个人知识库助手")

api_keys = st.text_input("请输入api_key",type="password")

file_paths = st.file_uploader("文件上传按钮",type=["pdf"])

process_btn = st.button("开始处理入库")

st.divider()


#API_KEY = os.getenv("ALIYUN_API_KEY") 


# =================  核心函数区 (逻辑层) =================
# [C程序员必读] @st.cache_resource
# 这是一个"装饰器"。它的作用类似于 C 语言里的 "static" 变量或单例模式。
# 它告诉 Streamlit："这个数据库连接只初始化一次，不要每次网页刷新都重新连一遍。"
@st.cache_resource
def init_db():
    #初始化数据库
    # PersistentClient 会自动在当前目录下创建一个文件夹 'my_db' 来存数据
    print("正在连接本地知识库 (./my_db)...")
    db_client = chromadb.PersistentClient(path="./my_db")

    # 创建一个"集合" (Collection)，类似于 SQL 里的"表"
    # get_or_create 表示：如果表存在就读取，不存在就新建
    collection = db_client.get_or_create_collection(name = "manual_docs")
    return collection

'''从 PDF 文件中提取文本内容'''
def extract_text_from_pdf(file_path):
    '''从 PDF 文件中提取文本内容'''
      
    try:
        reader = PdfReader(file_path)
        print(f"正在读取PDF")
        print(f"PDF的页数为：{len(reader.pages)}")

        full_text = ""

    #循环遍历
    # enumerate 帮我们同时获取页码(i)和页面对象(page)
        for i,page in enumerate(reader.pages):
        #提取文字
            text = page.extract_text()

            if  text:
                full_text += text + "\n" 
                print(f" -第{i+1}页提取了{len(text)}个字符")
            else:
                print(f" - 第 {i+1} 页似乎是纯图片，无法提取文字")

        return full_text
    except Exception as e:
            print(f"解析失败：{e}")
            return None

'''将总文字切片'''
def split_text_into_chunks(text,chunk_size = 500,overlap = 50):

    """
    把长文本切成小块
    :param text: 完整的长文本
    :param chunk_size: 每块大约多少字
    :param overlap: 重叠部分 (防止一句话正好被切两半)
    :return: 切好的文本列表 list[str]
    """   
    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)

        start += (chunk_size - overlap)
    
    return chunks

'''1.配置阿里云,输入api_key才初始化'''
client_ai = None
if api_keys:
    client_ai = OpenAI(
        api_key=api_keys, 
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
'''2.调用阿里云生成向量'''
def get_embedding(text):
    response = client_ai.embeddings.create(
        input= text,
        model="text-embedding-v3"
    )
    return response.data[0].embedding

#--------------------业务逻辑区 (控制层) =================
#初始化数据库连接
collection = init_db()

if process_btn and file_paths and api_keys:
    with st.spinner("正在清洗数据入库。。。"):
        #1.读文字
        raw_text = extract_text_from_pdf(file_paths)

        #2.切片
        chunks = split_text_into_chunks(raw_text)

        #3.向量化入库
        process_bar = st.progress(0)

        ids = []
        embeddings = []

        for i,chunk in enumerate(chunks):
            vec = get_embedding(chunk)
            if vec :
                ids.append(f"id{i}")#索引做id
                embeddings.append(vec)
            #更新进度条
            process_bar.progress((i+1)/len(chunks))
        
        if embeddings:
            collection.add(documents=chunks,embeddings=embeddings,ids=ids)
            st.success(f"成功入库，共传入{len(chunks)}个片段")
        else:
            st.error(f"数据处理失败，未能生成向量！")
        
# [C程序员必读] st.session_state
# Streamlit 每次交互（比如点按钮）都会从头运行整个脚本。
# 局部变量会重置。如果你想"记住"之前的聊天记录，必须存在 session_state 里。
# 这类似于 C 语言里的 "全局变量" 或 "堆内存"。

if "messages" not in st.session_state:
    st.session_state.messages = []

#1.把历史记录画出来
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 2. 等待用户输入
# := 海象运算符，C语言里没有。意思是：赋值并判断是否非空
if prompt :=st.chat_input("请根据手册提问。。"):
    if not api_keys:
        st.warning("请先输入api key")
        st.stop()

    with st.chat_message("user"):
        st.markdown(prompt)
    #记在本子上
    st.session_state.messages.append({"role":"user","content":prompt})

    # --- RAG 核心检索逻辑 ---
    q_vec = get_embedding(prompt)
    if q_vec:
        results = collection.query(query_embeddings=[q_vec],n_results=5)

        if results['documents'] and results['documents'][0]:
            doc_list = results['documents'][0]
            best_context = "\n\n=======\n\n".join(doc_list)

            # 在界面上显示个小折叠框，告诉用户参考了哪段原文 (Debug用)
            with st.expander("🔍 AI 参考了以下 5 个原文片段 (Debug)"):
                st.info(best_context)
            
            messages_history = []
            for msg in st.session_state.messages:
                messages_history.append({"role":msg["role"],"content":msg["content"]})

            #调用大模型
            full_prompt = f"基于此知识：\n{best_context}\n\n回答用户的问题:{prompt}"
            messages_history.append({"role":"user","content":full_prompt})
            with st.chat_message("assistant"):
                stream = client_ai.chat.completions.create(
                    model="qwen3-max",
                    messages=messages_history,
                    stream=True # 开启打字机流式效果
                                                           
                )
                response = st.write_stream(stream)
            # 记下 AI 的回复
            st.session_state.messages.append({"role": "assistant", "content": response})    
        else:
            st.warning("未找到相关内容")










