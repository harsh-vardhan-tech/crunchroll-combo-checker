from flask import Flask, render_template, request
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    if request.method == 'POST':
        combo_file = request.files['combo']
        filepath = os.path.join(UPLOAD_FOLDER, combo_file.filename)
        combo_file.save(filepath)
        results = process_combos(filepath)
    return render_template('index.html', results=results)

def process_combos(filepath):
    hits, fails, free, expired = [], [], [], []
    with open(filepath) as f:
        combos = f.readlines()
    for combo in combos:
        combo = combo.strip()
        # Dummy logic: Replace this with real checking
        if "pass" in combo:
            hits.append(combo)
        elif "free" in combo:
            free.append(combo)
        elif "expired" in combo:
            expired.append(combo)
        else:
            fails.append(combo)
    # Save results for download/view
    with open(os.path.join(RESULT_FOLDER, 'hits.txt'), 'w') as f:
        f.write('\n'.join(hits))
    with open(os.path.join(RESULT_FOLDER, 'fails.txt'), 'w') as f:
        f.write('\n'.join(fails))
    with open(os.path.join(RESULT_FOLDER, 'free.txt'), 'w') as f:
        f.write('\n'.join(free))
    with open(os.path.join(RESULT_FOLDER, 'expired.txt'), 'w') as f:
        f.write('\n'.join(expired))
    return {'hits': len(hits), 'fails': len(fails), 'free': len(free), 'expired': len(expired)}

if __name__ == '__main__':
    app.run(debug=True)
