from flask import Flask, request, jsonify, send_from_directory
import yt_dlp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ✅ HOMEPAGE (serves your index.html)
@app.route('/')
def homepage():
    return send_from_directory('.', 'index.html')


# ✅ API ROUTE
@app.route('/api/info', methods=['POST'])
def get_video_info():
    try:
        data = request.get_json()

        if not data or 'url' not in data:
            return jsonify({"success": False, "error": "No URL provided"}), 400

        url = data['url']

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            formats = []
            for f in info.get('formats', []):
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none':

                    size_mb = None
                    if f.get('filesize'):
                        size_mb = round(f['filesize'] / (1024 * 1024), 1)
                    elif f.get('filesize_approx'):
                        size_mb = round(f['filesize_approx'] / (1024 * 1024), 1)

                    formats.append({
                        "quality": f.get('resolution') or f"{f.get('height')}p" or "Unknown",
                        "ext": f.get('ext', 'mp4'),
                        "filesize": size_mb,
                        "url": f.get('url')
                    })

            return jsonify({
                "success": True,
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "duration": info.get('duration_string', 'Unknown'),
                "channel": info.get('uploader', 'Unknown'),
                "formats": formats[:15]
            })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ✅ REQUIRED FOR RENDER
if __name__ == '__main__':
    app.run()
