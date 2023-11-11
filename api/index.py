from http.server import BaseHTTPRequestHandler
import cv2
import numpy as np
import requests
import io
import os

class handler(BaseHTTPRequestHandler):

   def do_GET(self):
        img_path = self.path[1:]
        env_origin_url = os.environ.get("ORIGIN_URL")
        origin_url = env_origin_url + img_path
        env_referer_url = os.environ.get("REFERER_URL")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.76', 'Referer': env_referer_url}
        response = requests.get(origin_url, stream=True, headers=headers)
        try:
            image = cv2.imdecode(np.frombuffer(response.content, np.uint8), cv2.IMREAD_UNCHANGED)
            _, ext = os.path.splitext(img_path.lower())
            if ext in [".jpg", ".jpeg"]:
                env_jpg_quality = os.environ.get("JPG_QUALITY")
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), env_jpg_quality]
            elif ext == ".webp":
                env_webp_quality = os.environ.get("WEBP_QUALITY")
                encode_param = [int(cv2.IMWRITE_WEBP_QUALITY), env_webp_quality]
            elif ext == ".png":
                env_png_compression = os.environ.get("PNG_COMPRESSION")
                encode_param = [int(cv2.IMWRITE_PNG_COMPRESSION), env_png_compression]
            else:
                raise ValueError("Unsupported image format")
            output = io.BytesIO()
            result, data = cv2.imencode(ext, image, encode_param)
            output.write(data)
            output.seek(0)
            self.send_response(200)
            self.send_header('Content-type', 'image/' + ext[1:])
            self.end_headers()
            self.wfile.write(output.read())
        except Exception as e:
            self.send_response(200)
            self.send_header('Content-type', response.headers['Content-Type'])
            self.end_headers()
            self.wfile.write(response.content)
