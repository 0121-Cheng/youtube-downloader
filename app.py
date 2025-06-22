import os
from flask import Flask, render_template_string, request
from pathlib import Path
from pytube import YouTube

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><title>YouTube Downloader</title></head>
<body>
    <h1>YouTube 下載工具</h1>
    <form method="POST" id="url-form">
        <label>貼上 YouTube 網址：</label><br>
        <input type="text" name="url" id="url" style="width: 400px;">
        <button type="submit">下載影片</button>
        <button type="button" id="download-mp3">下載 MP3</button>
    </form>
    <div id="preview" style="margin-top:20px;"></div>
    <script>
        document.getElementById("url-form").onsubmit = async function(e) {
            e.preventDefault();
            const url = document.getElementById("url").value;
            document.getElementById("preview").innerHTML = '⏳ 正在下載影片...';
            const response = await fetch('/download_auto', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });
            const data = await response.text();
            document.getElementById("preview").innerHTML = data;
        };
        document.getElementById("download-mp3").onclick = async function() {
            const url = document.getElementById("url").value;
            document.getElementById("preview").innerHTML = '🎵 正在下載 MP3...';
            const response = await fetch('/download_mp3', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });
            const data = await response.text();
            document.getElementById("preview").innerHTML = data;
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
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        filename = yt.title + ".mp4"
        output_path = generate_unique_path(os.path.join('downloads', filename))
        stream.download(output_path=Path(output_path).parent, filename=Path(output_path).name)
        return f"✅ 影片下載完成：{Path(output_path).name}"
    except Exception as e:
        return f"❌ 錯誤：{str(e)}"

@app.route('/download_mp3', methods=['POST'])
def download_mp3():
    url = request.json.get('url')
    try:
        os.makedirs('downloads', exist_ok=True)
        yt = YouTube(url)
        stream = yt.streams.filter(only_audio=True).first()
        filename = yt.title + ".mp3"
        output_path = generate_unique_path(os.path.join('downloads', filename))
        stream.download(output_path=Path(output_path).parent, filename=Path(output_path).name)
        return f"🎵 MP3 下載完成：{Path(output_path).name}"
    except Exception as e:
        return f"❌ 錯誤：{str(e)}"

if __name__ == '__main__':
    os.makedirs('downloads', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
