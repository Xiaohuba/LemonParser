import openai
import os


prompt = """请将图片内容转为规范的 markdown+latex，标题从一级开始。
特别的：
- 请忽略所有的页眉、页脚和代码框的行号。
- 对于表格中跨越多行的单元格，请在 markdown 表格中每行都重复一遍。
- 请将图片中的所有公式、数字转为 latex 格式并使用美元符号包裹。
- 请将图片中的文件名、命令行参数、样例输入输出使用 markdown 代码块包裹。
- 请直接输出转化完成的 markdown 文本，不要输出任何多余文字。"""


async def image2md(base64_images):
    print("INFO: Sending request...")
    client = openai.AsyncOpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    image_contents = [
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{base64_image}"},
        }
        for base64_image in base64_images
    ]
    completion = await client.chat.completions.create(
        model="qwen2.5-vl-32b-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                ]
                + image_contents,
            }
        ],
    )
    print("INFO: Recieved response.")
    return completion.choices[0].message.content
