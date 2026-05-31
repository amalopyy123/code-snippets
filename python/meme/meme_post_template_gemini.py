import os
import json
import mimetypes
from contextlib import ExitStack
import requests

def generate_meme(
    meme_key: str,
    texts: list = None,
    image_paths: list = None,
    args: dict = None,
    output_filename: str = "output.gif",
    api_base_url: str = "http://127.0.0.1:2233"
):
    """
    通用表情包生成函数
    
    :param meme_key: 表情包的唯一标识符（例如: 'capoo_say', 'petpet', 'make_friend' 等）
    :param texts: 文本列表，例如 ["第一行文字", "第二行文字"]
    :param image_paths: 本地图片路径列表，例如 ["path/to/avatar1.jpg", "path/to/avatar2.png"]
    :param args: 额外参数字典，例如 {"color": "#ff0000"}
    :param output_filename: 生成的表情包保存路径（建议根据表情包类型使用 .gif 或 .jpg/.png 尾缀）
    :param api_base_url: 接口的基础服务地址
    """
    # 默认值处理
    texts = texts or []
    image_paths = image_paths or []
    args = args or {}
    
    # 构建最终的 API 请求地址
    url = f"{api_base_url.rstrip('/')}/memes/{meme_key}/"
    
    # 1. 构造普通表单字段 (texts 和 args)
    # 针对可能重名的 key (多个 texts)，我们需要使用元组列表传入
    data = []
    for t in texts:
        data.append(("texts", t))
    
    # 额外参数字典需要转为 JSON 字符串
    data.append(("args", json.dumps(args)))

    # 2. 构造文件上传字段 (images)
    # 使用 ExitStack 确保不论请求成功与否，所有打开的图片文件都能被安全关闭
    with ExitStack() as stack:
        files = []
        for path in image_paths:
            if not os.path.exists(path):
                print(f"警告: 图片路径不存在 -> {path}")
                continue
            
            # 打开文件并注册到 stack 中
            file_obj = stack.enter_context(open(path, "rb"))
            # 获取文件名与 MIME 类型
            filename = os.path.basename(path)
            mime_type, _ = mimetypes.guess_type(path)
            mime_type = mime_type or "application/octet-stream"
            
            # 组装为 requests 接受的文件格式元组
            files.append(("images", (filename, file_obj, mime_type)))

        print(f"正在请求表情包 [{meme_key}]...")
        print(f"文字: {texts}")
        print(f"图片: {image_paths}")
        if args:
            print(f"额外参数: {args}")

        try:
            # 发送请求。requests 库在检测到 files 存在时，会自动组装成标准的 multipart/form-data 报文
            response = requests.post(url, data=data, files=files, timeout=20)
            
            if response.status_code == 200:
                with open(output_filename, "wb") as f:
                    f.write(response.content)
                print(f"生成成功！保存路径为: {os.path.abspath(output_filename)}\n")
                return True
            else:
                print(f"生成失败，HTTP 状态码: {response.status_code}")
                try:
                    print(f"错误详情: {response.json()}")
                except Exception:
                    print(f"原始响应内容: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"网络请求发生异常: {e}\n")
            return False


# =====================================================================
# 调用示例
# =====================================================================
if __name__ == "__main__":
    # 在运行以下代码前，请确保：
    # 1. 本地启动了服务：meme run
    # 2. 本地准备好了相应的图片（如 avatar1.png, avatar2.png 等）
    
    # 示例 1: 生成 Capoo Say (单行字，无图)
    # generate_meme(
    #     meme_key="capoo_say",
    #     texts=["测试通用模板"],
    #     output_filename="capoo_test.gif"
    # )

    # 示例 2: 生成摸头表情包 Petpet (需要 1 张图，无文字)
    # generate_meme(
    #     meme_key="petpet",
    #     image_paths=["my_avatar.png"],  # 传入你的头像路径
    #     output_filename="petpet_test.gif"
    # )

    # 示例 3: 你应该致电 You Should Call (需要 1 张图，两行字)
    # generate_meme(
    #     meme_key="you_should_call",
    #     texts=["你应该致电"],
    #     image_paths=["friend_avatar.jpg"],
    #     output_filename="you_should_call_test.jpg"
    # )

    # 示例 3: 五年怎么过的 (需要4行字)
    generate_meme(
        meme_key="wunian",
        texts=['五年', '你知道我这五年是怎么过的吗', '我每天躲在家里玩魔物娘', '你知道有多好玩吗'],
        output_filename="wunian_test.gif"
    )
