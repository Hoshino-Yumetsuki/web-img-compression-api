from http.server import BaseHTTPRequestHandler
import cv2
import numpy as np
import requests
import io
import os

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        ORIGIN_URL = os.environ.get('ORIGIN_URL')
        JPGE_QUALITY = os.environ.get('JPGE_QUALITY')
        WEBP_QUALITY = os.environ.get('WEBP_QUALITY')
        PNG_COMPRESSION = os.environ.get('PNG_COMPRESSION')
        img_path = self.path[1:]
        origin_url = ORIGIN_URL + img_path
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.69'}
        response = requests.get(origin_url, stream=True, headers=headers)
        image = cv2.imdecode(np.frombuffer(response.content, np.uint8), 1)
        _, ext = os.path.splitext(img_path)
        if ext in [".jpg", ".jpeg"]:
            # 设置jpg格式图片的压缩质量（数字越大质量越高，最大为100）
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), JPGE_QUALITY]
            img_type = "image/jpeg"
        elif ext == ".webp":
            # 设置webp格式图片的压缩质量（数字越大质量越高，最大为100）
            encode_param = [int(cv2.IMWRITE_WEBP_QUALITY), WEBP_QUALITY]
            img_type = "image/webp"
        elif ext == ".png":
            # 设置png格式图片的压缩质量（数字越大质量越高，最大为9）
            encode_param = [int(cv2.IMWRITE_PNG_COMPRESSION), PNG_COMPRESSION]
            img_type = "image/png"
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write("Unsupported image format".encode())
            return
        output = io.BytesIO()
        result, data = cv2.imencode(ext, image, encode_param)
        output.write(data)
        output.seek(0)
        self.send_response(200)
        self.send_header('Content-type', img_type)
        self.end_headers()
        self.wfile.write(output.read())
