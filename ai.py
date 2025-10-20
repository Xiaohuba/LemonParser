import openai
import os
from dotenv import load_dotenv

load_dotenv()

prompt = """请将图片内容转为规范的 markdown，题目名使用三级标题，每节（如题目描述、输入格式等）小标题使用四级标题。

特别的：
- 请忽略所有的页眉、页脚和代码框的行号。
- 对于表格中跨越多行的单元格，请在 markdown 表格中每行都重复一遍。
- 请将图片中的所有公式、数字转为 latex 格式并使用美元符号包裹。
- 请将图片中的命令行参数、样例输入输出使用 markdown 代码块包裹。
- 请直接输出转化完成的 markdown 文本，不要输出任何多余文字。

**重要：你的回答应该直接从 `### <题目名>` 开始，不要输出其他内容。**
"""


async def image2md(base64_images):
    print("INFO: Sending request...")
    client = openai.AsyncOpenAI(
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
    )
    image_contents = [
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{base64_image}"},
        }
        for base64_image in base64_images
    ]
    completion = await client.chat.completions.create(
        model="qwen/qwen3-vl-235b-a22b-instruct",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                ],
            },
            {
                "role": "user",
                "content": image_contents,
            },
        ],
        stream=True,
        stream_options={"include_usage": True},
        # extra_body={"enable_thinking": False},
    )
    response = ""
    token_count = 0
    async for chunk in completion:
        if chunk.choices:
            if chunk.choices[0].delta.content:
                response += chunk.choices[0].delta.content
        else:
            token_count += chunk.usage.total_tokens
            break
    # print(f"INFO: Recieved response, {token_count} tokens used.")
    return response
