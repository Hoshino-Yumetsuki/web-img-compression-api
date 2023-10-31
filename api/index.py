from http.server import BaseHTTPRequestHandler
import cv2
import numpy as np
import requests
import io
import os

class handler(BaseHTTPRequestHandler):

   def do_GET(self):
       img_path = self.path[1:]
       origin_url = os.environ.get("ORIGIN_URL") + img_path
       headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.69'}
       response = requests.get(origin_url, stream=True, headers=headers)
       try:
           image = cv2.imdecode(np.frombuffer(response.content, np.uint8), 1)
           _, ext = os.path.splitext(img_path)
           if ext in [".jpg", ".jpeg"]:
               # 设置jpg格式图片的压缩质量（数字越大质量越高，最大为100）
               encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 80]
               img_type = "image/jpeg"
           elif ext == ".webp":
               # 设置webp格式图片的压缩质量（数字越大质量越高，最大为100）
               encode_param = [int(cv2.IMWRITE_WEBP_QUALITY), 80]
               img_type = "image/webp"
           elif ext == ".png":
               # 设置png格式图片的压缩质量（数字越大质量越高，最大为9）
               encode_param = [int(cv2.IMWRITE_PNG_COMPRESSION), 6]
               img_type = "image/png"
           else:
               raise ValueError("Unsupported image format")
           output = io.BytesIO()
           result, data = cv2.imencode(ext, image, encode_param)
           output.write(data)
           output.seek(0)
           self.send_response(200)
           self.send_header('Content-type', img_type)
           self.end_headers()
           self.wfile.write(output.read())
       except Exception as e:
           self.send_response(200)
           self.send_header('Content-type', response.headers['Content-Type'])
           self.end_headers()
           self.wfile.write(response.content)