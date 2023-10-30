from http.server import BaseHTTPRequestHandler
import cv2
import numpy as np
import requests
import io
import os

env_origin_url = os.getenv('ORIGIN_URL')
env_jpeg_quality = os.getenv('JPEG_QUALITY')
env_webp_quality = os.getenv('WEBP_QUALITY')
env_png_compression = os.getenv('PNG_COMPRESSION')

class handler(BaseHTTPRequestHandler):
   def do_GET(self):
       img_path = self.path[1:]
       origin_url = env_origin_url + img_path
       headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.69'}

       try:
           response = requests.get(origin_url, stream=True, headers=headers)
           response.raise_for_status()

           image = cv2.imdecode(np.frombuffer(response.content, np.uint8), 1)
           _, ext = os.path.splitext(img_path)

           if ext in [".jpg", ".jpeg"]:
               encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), env_jpeg_quality]
               img_type = "image/jpeg"
           elif ext == ".webp":
               encode_param = [int(cv2.IMWRITE_WEBP_QUALITY), env_webp_quality]
               img_type = "image/webp"
           elif ext == ".png":
               encode_param = [int(cv2.IMWRITE_PNG_COMPRESSION), env_png_compression]
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

       except requests.exceptions.RequestException as e:
           self.send_response(500)
           self.send_header('Content-type', 'text/plain')
           self.end_headers()
           self.wfile.write(f"Request Error: {str(e)}".encode())

       except cv2.error as e:
           self.send_response(500)
           self.send_header('Content-type', 'text/plain')
           self.end_headers()
           self.wfile.write(f"Image Processing Error: {str(e)}".encode())

       except Exception as e:
           self.send_response(500)
           self.send_header('Content-type', 'text/plain')
           self.end_headers()
           self.wfile.write(f"Internal Server Error: {str(e)}".encode())