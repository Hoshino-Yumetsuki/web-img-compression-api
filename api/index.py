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

        try:
            response = requests.get(origin_url, stream=True, headers=headers)
            response.raise_for_status()  # Raise HTTPError for bad responses
            image = cv2.imdecode(np.frombuffer(response.content, np.uint8), 1)
            _, ext = os.path.splitext(img_path)

            encode_param, img_type = self.get_encode_param_and_type(ext)

            output = io.BytesIO()
            result, data = cv2.imencode(ext, image, encode_param)
            output.write(data)
            output.seek(0)
            self.send_response(200)
            self.send_header('Content-type', img_type)
            self.end_headers()
            self.wfile.write(output.read())

        except requests.exceptions.HTTPError as e:
            self.send_error(400, message="Bad Request: {}".format(str(e)))

        except Exception as e:
            self.send_error(500, message="Internal Server Error: {}".format(str(e)))

    def get_encode_param_and_type(self, ext):
        if ext in [".jpg", ".jpeg"]:
            env_jpg_quality = int(os.environ.get("JPG_QUALITY"))
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), env_jpg_quality]
            img_type = "image/jpeg"
        elif ext == ".webp":
            env_webp_quality = int(os.environ.get("WEBP_QUALITY"))
            encode_param = [int(cv2.IMWRITE_WEBP_QUALITY), env_webp_quality]
            img_type = "image/webp"
        elif ext == ".png":
            env_png_compression = int(os.environ.get("PNG_COMPRESSION"))
            encode_param = [int(cv2.IMWRITE_PNG_COMPRESSION), env_png_compression]
            img_type = "image/png"
        else:
            raise ValueError("Unsupported image format")
        return encode_param, img_type
