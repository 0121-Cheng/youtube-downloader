import os
import subprocess
from flask import Flask, render_template_string, request
import json
from pathlib import Path

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>YouTube Downloader</title>
</head>
<body>
    <h1>YouTube 下載工具</h1>
    <form method=\"POST\" id=\"url-form\">
        <label>貼上 YouTube 網址：</label><br>
        <input type=\"text\" name=\"url\" id=\"url\" style=\"width: 400px;\">
        <button type=\"submit\">下載影片</button>
        <button type=\"button\" id=\"download-mp3\">下載 MP3</button>
    </form>

    <div id=\"preview\" style=\"margin-top:20px;\"></div>

    <script>
        document.getElementById(\"url-form\").onsubmit = async function(e) {
            e.preventDefault();
            const url = document.getElementById(\"url\").value;
            document.getElementById(\"preview\").innerHTML = '⏳ 正在下載影片...';
            const response = await fetch('/download_auto', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });
            const data = await response.text();
            document.getElementById(\"preview\").innerHTML = data;
        };

        document.getElementById(\"download-mp3\").onclick = async function() {
            const url = document.getElementById(\"url\").value;
            document.getElementById(\"preview\").innerHTML = '🎵 正在下載 MP3...';
            const response = await fetch('/download_mp3', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });
            const data = await response.text();
            document.getElementById(\"preview\").innerHTML = data;
        };
    </script>
</body>
</html>
"""

def generate_unique_path(base_path):
    base = Path(base_path)
    if not base.exists():
        return str(base)
    stem, suffix = base.stem, base.suffix
    i = 1
    while True:
        new_path = base.with_name(f"{stem} ({i}){suffix}")
        if not new_path.exists():
            return str(new_path)
        i += 1

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/download_auto', methods=['POST'])
def download_auto():
    url = request.json.get('url')
    try:
        os.makedirs('downloads', exist_ok=True)
        temp_cmd = ['yt-dlp', '--get-filename', '-o', '%(title)s.%(ext)s', url]
        filename = subprocess.check_output(temp_cmd, text=True).strip()
        output_path = generate_unique_path(os.path.join('downloads', filename))
        subprocess.run(['yt-dlp', '-o', output_path, url])
        return "✅ 影片下載完成（請查看 downloads 資料夾）"
    except Exception as e:
        return f"❌ 錯誤：{str(e)}"

@app.route('/download_mp3', methods=['POST'])
def download_mp3():
    url = request.json.get('url')
    try:
        os.makedirs('downloads', exist_ok=True)
        temp_cmd = ['yt-dlp', '--get-filename', '-x', '--audio-format', 'mp3', '-o', '%(title)s.%(ext)s', url]
        filename = subprocess.check_output(temp_cmd, text=True).strip()
        output_path = generate_unique_path(os.path.join('downloads', filename))
        subprocess.run(['yt-dlp', '-x', '--audio-format', 'mp3', '-o', output_path, url])
        return "🎵 MP3 下載完成（請查看 downloads 資料夾）"
    except Exception as e:
        return f"❌ 錯誤：{str(e)}"

if __name__ == '__main__':
    os.makedirs('downloads', exist_ok=True)
    app.run(debug=True, port=5000)
