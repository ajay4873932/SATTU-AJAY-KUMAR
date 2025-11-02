import os
import pandas as pd
import sqlite3
from flask import Flask, request, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['excel_file']
    if file:
        # Save uploaded file
        input_folder = 'data/input/'
        os.makedirs(input_folder, exist_ok=True)
        filepath = os.path.join(input_folder, file.filename)
        file.save(filepath)

        # Read Excel file
        sheets = pd.read_excel(filepath, sheet_name=None)

        # Save as JSON
        output_folder = 'data/output/'
        os.makedirs(output_folder, exist_ok=True)
        for sheet, df in sheets.items():
            json_path = os.path.join(output_folder, f"{sheet}.json")
            df.to_json(json_path, orient='records', indent=4)

        # Save to SQLite
        db_path = 'data/database/app.db'
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path)
        for sheet, df in sheets.items():
            df.to_sql(sheet, conn, if_exists='replace', index=False)
        conn.close()

        # Prepare preview for each sheet
        previews = {sheet: df.head().to_html(classes="table table-bordered", index=False)
                    for sheet, df in sheets.items()}

        return render_template('success.html', previews=previews)
    else:
        return "❌ No file uploaded", 400


if __name__ == '__main__':
    app.run(debug=True)
