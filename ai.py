import openai
import os


prompt = """请将图片内容转为规范的 markdown+latex。
特别的：
- 请忽略所有的页眉、页脚和代码框的行号。
- 请将图片中的所有公式、数字转为 latex 格式并使用美元符号包裹。
- 请将图片中的文件名、命令行参数、样例输入输出使用 markdown 代码块包裹。
- 请直接输出 markdown 源码，不要输出任何额外信息。"""


def image2md(base64_image):
    client = openai.OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    completion = client.chat.completions.create(
        model="qwen2.5-vl-72b-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                    },
                    {
                        "type": "text",
                        "text": prompt,
                    },
                ],
            }
        ],
    )
    return completion.choices[0].message.content
