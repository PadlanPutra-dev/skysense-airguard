Struktur Project

```text
skysense/
│
├── public/
│   ├── css/
│   ├── js/
│   ├── camera.html
│   ├── grafik.html
│   ├── index.html
│   ├── prediksi.html
│   └── riwayat.html
│
├── routes/
│   ├── cameraRoute.js
│   ├── predictionRoute.js
│   └── sensorRoute.js
│
├── services/
│   └── mlServices.js
│
├── ml/
│   ├── data/
│   │   └── Dataset_cuaca_clean.xlsx
│   │
│   ├── evaluation/
│   │   ├── evaluation_final.csv
│   │   ├── evaluation_timeseries.csv
│   │   └── actual_vs_predicted/
│   │
│   ├── models/
│   │   └── random_forest_*.pkl
│   │
│   └── src/
│       ├── api.py
│       ├── predictor.py
│       ├── train.py
│       ├── evaluate_model.py
│       ├── evaluate_timeseries.py
│       ├── analyze_data.py
│       └── feature_engineering.py
│
├── bmkg.js
├── db.js
├── mqtt.js
├── server.js
├── package.json
├── requirements.txt
└── .gitignore


Cara Menjalankan Project
1. Clone Repository
git clone https://github.com/skysense100/skysense.git
cd skysense
2. Install Dependency Node.js
npm install
3. Membuat Virtual Environment Python
Windows:
python -m venv .venv

Aktifkan:

.\.venv\Scripts\Activate.ps1

Jika menggunakan CMD:

.venv\Scripts\activate

4. Install Dependency Machine Learning
pip install -r ml/requirements.txt

5. Menjalankan FastAPI
Buka terminal pertama:

uvicorn ml.src.api:app --reload

FastAPI berjalan pada:
http://127.0.0.1:8000

Tes API:
http://127.0.0.1:8000/

Tes forecast 7 hari:
http://127.0.0.1:8000/forecast?days=7

6. Menjalankan Website
Buka terminal kedua.
Pastikan berada di folder utama project:
cd skysense

Kemudian:
node server.js

Website berjalan pada:
http://localhost:5000

Halaman prediksi:
http://localhost:5000/prediksi.html