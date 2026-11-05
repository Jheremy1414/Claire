"""
Servidor HTTP Local con Soporte Completo de Audio Streaming (HTTP 206 Partial Content)
Ideal para probar el Baby Shower en Chrome, Edge y Móvil sin errores de conexión.
"""

import os
import re
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler

class RangeFileWrapper:
    def __init__(self, f, length):
        self.f = f
        self.remaining = length

    def read(self, size=-1):
        if self.remaining <= 0:
            return b''
        if size < 0 or size > self.remaining:
            size = self.remaining
        chunk = self.f.read(size)
        self.remaining -= len(chunk)
        return chunk

    def close(self):
        self.f.close()

class BabyShowerRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, must-revalidate')
        super().end_headers()

    def send_head(self):
        path = self.translate_path(self.path)
        if not os.path.isfile(path):
            return super().send_head()

        file_size = os.path.getsize(path)

        # Si el navegador solicita un fragmento de audio (HTTP Range)
        if 'Range' in self.headers:
            range_header = self.headers['Range']
            match = re.match(r'bytes=(\d+)-(\d*)', range_header)
            if match:
                start = int(match.group(1))
                end = int(match.group(2)) if match.group(2) else file_size - 1

                if start >= file_size or start > end:
                    self.send_error(416, 'Requested Range Not Satisfiable')
                    return None

                self.send_response(206)
                ctype = self.guess_type(path)
                self.send_header('Content-Type', ctype)
                self.send_header('Content-Range', f'bytes {start}-{end}/{file_size}')
                self.send_header('Content-Length', str(end - start + 1))
                self.send_header('Last-Modified', self.date_time_string(os.path.getmtime(path)))
                self.end_headers()

                f = open(path, 'rb')
                f.seek(start)
                return RangeFileWrapper(f, end - start + 1)

        return super().send_head()

    def log_message(self, format, *args):
        # Muestra peticiones limpias sin spam ni errores de desconexión normal
        sys.stdout.write(f"[{self.log_date_time_string()}] {format % args}\n")

def run(port=8000):
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server_address = ('', port)
    httpd = HTTPServer(server_address, BabyShowerRequestHandler)
    print("=" * 60)
    print(f" 🍼 Baby Shower Web Server Activo!")
    print(f" 👉 Abre en tu navegador: http://localhost:{port}")
    print(f" 🎵 Streaming de audio fluido sin cortes activado (HTTP 206)")
    print(f" 🛑 Presiona Ctrl + C en esta ventana para detenerlo")
    print("=" * 60)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor cerrado correctamente.")
        httpd.server_close()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run(port)

