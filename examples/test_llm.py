from openai import OpenAI
import time

# 配置连接到本地 Ollama
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # 随便填
)

print("1. 开始尝试连接 Ollama...")
start_time = time.time()

try:
    print("2. 正在发送请求，请耐心等待 LLM 思考需要时间)...")

    response = client.chat.completions.create(
        model="llama3.3:70b",
        messages=[
            {"role": "user", "content": "你好，请输出一个 SQL 语句：查询所有用户的名字。"}
        ],
        temperature=0
    )

    end_time = time.time()
    print(f"3. 成功收到回复！耗时: {end_time - start_time:.2f} 秒")
    print("-" * 30)
    print(response.choices[0].message.content)
    print("-" * 30)

except Exception as e:
    print("\n❌ 连接失败！报错信息如下：")
    print(e)