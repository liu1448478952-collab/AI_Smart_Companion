import streamlit as st
import os
from openai import OpenAI
from datetime import datetime
import json

from requests import delete
from streamlit import session_state

#设置页面的配置项
st.set_page_config(
    page_title="AI智能伴侣",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)

# 保存会话信息函数
def save_session():
    if st.session_state.current_session:
        # 构建新的会话对象
        session_date = {
            "nick_name": st.session_state.nick_name,
            "nature": st.session_state.nature,
            "current_session": st.session_state.current_session,
            "message": st.session_state.message
        }
        # 如果sessions文件夹不存在,则创建
        if not os.path.exists("sessions"):
            os.mkdir("sessions")
        # 保存会话数据
        with open(f"sessions/{st.session_state.current_session}.json", "w", encoding="utf-8") as f:
            json.dump(session_date, f, ensure_ascii=False, indent=2)
#生成回话时间函数
def generate_session_name():
    return datetime.now().strftime("%Y-%m-%d %H-%M-%S")

#加载所有会话信息
def load_sessions():
    session_list = []
    #加载sessions文件夹下的所有json文件
    if os.path.exists("sessions"):
        file_list = os.listdir("sessions")
        for filename in file_list:
            if filename.endswith(".json"):
                session_list.append(filename[:-5])
    return session_list[::-1]

#加载指定会话信息
def load_session(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            with open(f"sessions/{session_name}.json", "r", encoding="utf-8") as f:
                session_data = json.load(f)
                st.session_state.nick_name = session_data["nick_name"]
                st.session_state.nature = session_data["nature"]
                st.session_state.current_session = session_name
                st.session_state.message = session_data["message"]
    except Exception as e:
        st.error("会话信息加载失败! 请检查会话文件是否存在且格式正确。")

#删除指定会话信息
def delete_session(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            os.remove(f"sessions/{session_name}.json")
            st.success("会话信息删除成功！")
            #如果删除的会话是当前会话,则重新生成会话
            if session_name == st.session_state.current_session:
                st.session_state.message = []
                st.session_state.current_session = generate_session_name()
    except Exception:
        st.error("会话信息删除失败! 请检查会话文件是否存在且格式正确。")




# 显示标题
st.title("AI智能伴侣")
# 显示logo
st.logo("resourse/rensheng.jpg")

# 系统提示词
system_prompt = """
    你叫 %s ,现在是用户的男朋友,请完全带入男朋友角色.:"
    规则:
    1. 请用男朋友的语气回答用户的问题;
    2. 请用中文回答用户的问题;
    3. 请用真诚的语气回答用户的问题;
    4. 回复简短,像微信聊天一样;
    5. 匹配用户的语言;
    6. 每次只回1条消息;
    7. 禁止任何场景或状态描述性文字;
    8. 有需要的话可以使用emoji表情;
    9. 回复的内容要充分体现男朋友的性格特征
    男朋友的性格特征:
        %s
    你必须严格遵守上述规则来回答用户的问题.
    """

#初始化聊天信息
if 'message' not in st.session_state:
    st.session_state.message = []

#昵称
if "nick_name" not in st.session_state:
    st.session_state.nick_name = "帅龙"

#性格
if "nature" not in st.session_state:
    st.session_state.nature = "真诚,热情,关心,体贴,爱护,尊重,理解,支持,鼓励,爱"

#会话的名字
if "current_session" not in st.session_state:
    st.session_state.current_session = generate_session_name()

#加载会话信息
st.text(f"会话名称:{st.session_state.current_session}")

#展示聊天信息
for message in st.session_state.message:                 #{"role": "user", "content": "你好"}
    st.chat_message(message["role"]).write(message["content"])
    # if message["role"] == "user":
    #     st.chat_message("user").write(message["content"])
    # elif message["role"] == "assistant":
    #     st.chat_message("assistant").write(message["content"])

#创建与AI大模型交互的客户端对象(DEEPSEEK_API_KEY是环境变量的名字,对应的值是deepseek的api_key)
client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com")

#左侧的侧边栏
with st.sidebar:
    #会话信息
    st.subheader("AI控制面板")


    #1.新建会话部分
    #添加按钮("新建会话")
    if st.button("新建会话",width = "stretch",icon = "✏️"):
        #1. 保存当前会话数据
        save_session()

        #2. 创建新的会话
        if st.session_state.message:
            st.session_state.current_session = generate_session_name()
            st.session_state.message = []
            save_session()
            st.rerun()                        # 重新运行当前页面

    #2.展示历史会话列表
    st.subheader("历史会话")
    #添加按钮
    session_list = load_sessions()
    for session in session_list:
        col1, col2 = st.columns([4,1])
        with col1:
            #加载会话信息
            if st.button(session, width="stretch", icon="🗒️", key = f"load_{session}", type='primary' if session == st.session_state.current_session else 'secondary'):
                load_session(session)
                st.rerun()
        with col2:
            #删除会话信息
            if st.button("", width="stretch", icon="❌", key = f"delete_{session}"):
                delete_session(session)
                st.rerun()

    #分割线
    st.divider()

    #3.男朋友信息
    st.subheader("男朋友信息")
    #昵称输入框:
    nick_name = st.text_input("昵称",placeholder="请输入昵称",value=st.session_state.nick_name)
    if nick_name:
        st.session_state.nick_name = nick_name
    #性格输入框:
    nature = st.text_area("性格",placeholder="请输入性格",value=st.session_state.nature)
    if nature:
        st.session_state.nature = nature



#聊天输入框
prompt = st.chat_input("请输入您的问题")
if prompt:                               #字符串会自动转换为布尔值，非空字符串为True
    st.chat_message(f"user").write(prompt)
    print("-------> 调用AI大模型.提示词:", prompt)
    # 添加用户消息到会话状态
    st.session_state.message.append({"role": "user", "content": prompt})

    #调用ai大模型,交互
    # 与AI大模型的交互
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt % (st.session_state.nick_name, st.session_state.nature)},
            *st.session_state.message
        ],
        stream=True,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}}
    )
    # # 输出AI大模型回复的结果(非流式输出的解析方式)
    # print("<------- 大模型返回:", response.choices[0].message.content)
    # st.chat_message(f"assistant").write(response.choices[0].message.content)

    # 输出AI大模型回复的结果(流式输出的解析方式)
    response_message = st.empty()   # 创建一个空的聊天消息容器,用于展示AI大模型的回复
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            full_response += content
            response_message.write(full_response)

    #
    st.session_state.message.append({"role": "assistant", "content": full_response})
    save_session()

