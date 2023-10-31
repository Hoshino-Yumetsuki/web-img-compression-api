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
       headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'}
       response = requests.get(origin_url, stream=True, headers=headers)
       try:
           image = cv2.imdecode(np.frombuffer(response.content, np.uint8), 1)
           _, ext = os.path.splitext(img_path)
           if ext in [".jpg", ".jpeg"]:
               env_jpg_quality = os.environ.get("JPG_QUALITY")
               # 设置jpg格式图片的压缩质量（数字越大质量越高，最大为100）
               encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), env_jpg_quality]
               img_type = "image/jpeg"
           elif ext == ".webp":
               env_webp_quality = os.environ.get("WEBP_QUALITY")
               # 设置webp格式图片的压缩质量（数字越大质量越高，最大为100）
               encode_param = [int(cv2.IMWRITE_WEBP_QUALITY), env_webp_quality]
               img_type = "image/webp"
           elif ext == ".png":
               env_png_compression = os.environ.get("PNG_COMPRESSION")
               # 设置png格式图片的压缩质量（数字越大质量越高，最大为9）
               encode_param = [int(cv2.IMWRITE_PNG_COMPRESSION), env_png_compression]
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