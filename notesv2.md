# FastAPI + Streamlit + Docker
FastAPI backend & streamlit frontend run using docker-compose
## 1.✅ Project Structure
```bash  
myproject/
├── app/
│   ├── server.py                  # FastAPI backend
│   └── model.pkl
├── streamlit_app/
│   ├── frontend.py                # Streamlit frontend
│   ├── style.css 
│   ├── images/ 
│   └── .....
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── model.py
└── model.pkl
```
## 2.🐳 Dockerfile
```Dockerfile 
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["streamlit", "run", "streamlit_app/frontend.py", "--server.port=8501", "--server.address=0.0.0.0"]


```
## 3.🐙 docker-compose.yml
```yaml
services:
  backend:
    build: .
    command: uvicorn app.server:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    restart: always

  frontend:
    build: .
    command: streamlit run streamlit_app/frontend.py --server.port 8501 --server.address 0.0.0.0
    ports:
      - "8501:8501"
    volumes:
      - .:/app
    depends_on:
      - backend
    restart: always
```

## 4.📜 requirements.txt
```txt
scikit-learn==1.2.2
fastapi
numpy==1.23.5  # Explicitly set NumPy to a stable version
uvicorn
joblib
xgboost==2.0.3
scipy
jinja2
python-multipart
requests
pydantic
pandas
streamlit
Pillow
streamlit-navigation-bar
xgboost
plotly==5.20.0
pymongo
joblib
```
## 5.📜 server.py
```python
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import joblib

from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import joblib

# Load trained model pipeline and class names
model = joblib.load("model.pkl")
classes = np.array(["Benign", "Malicious"])  # 0: Benign, 1: Malicious

app = FastAPI()

class Features(BaseModel):
    features: list[float]

@app.get("/")
def read_root():
    return {"message": "Model API is running."}

@app.post("/predict")
def predict(data: Features):
    try:
        features = np.array(data.features).reshape(1, -1)
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]

        return {
            "predicted_class": classes[prediction],
            "probabilities": {
                "Benign": float(probabilities[0]),
                "Malicious": float(probabilities[1])
            }
        }
    except Exception as e:
        return {"error": str(e)}
```
## 6.🚀modeling
```python
import numpy as np
from pyspark.ml.feature import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_selection import SelectKBest, f_classif
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report
import pandas as pd
import joblib
from sklearn.preprocessing import LabelEncoder
import seaborn as sns
import matplotlib.pyplot as plt
import os
import pickle as pickle
import zipfile
def unzip_selected_files(zip_path='datasets/archive.zip', extract_to='datasets/extracted'):
    selected_files = [
        '03-02-2018.csv',
        '03-01-2018.csv',
        '02-23-2018.csv',
        '02-14-2018.csv',
    ]

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file in selected_files:
            zip_ref.extract(file, path=extract_to)

def get_clean_data():
    unzip_selected_files()

    file_paths = [
        'datasets/extracted/03-02-2018.csv',
        'datasets/extracted/03-01-2018.csv',
        'datasets/extracted/02-23-2018.csv',
        'datasets/extracted/02-14-2018.csv',
    ]

    dataset_list = []
    for path in file_paths:
        df = pd.read_csv(path, low_memory=False)
        # Remove rows where "Protocol" column is literally "Protocol" (repeated header row)
        df = df[df["Protocol"] != "Protocol"]
        dataset_list.append(df)

    df = pd.concat(dataset_list, ignore_index=True)

    # Drop unwanted columns
    df = df.drop(columns=["Timestamp", "Dst Port"], errors='ignore')

    # Drop rows with specific Label value (replace value with your actual value, e.g., 2)
    value = 'Label'
    df = df.drop(df.index[df['Label'] == value])

    # Encode "Protocol" using LabelEncoder
    df["Protocol"] = df["Protocol"].astype(str)
    le_protocol = LabelEncoder()
    df["Protocol"] = le_protocol.fit_transform(df["Protocol"])

    # Encode the target column "Label" as binary
    le_label = LabelEncoder()
    df["Label"] = le_label.fit_transform(df["Label"])
    df["Label"] = np.where(df["Label"] == 0, 0, 1)

    # Remove rows with NaNs
    df = df.dropna()

    # Convert any remaining object columns to float
    string_columns = [col for col in df.columns if df[col].dtype == 'object']
    for col in string_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna()  # Drop rows with conversion issues

    # Remove negative values
    df = df[df.ge(0).all(axis=1)]

    # Drop duplicates
    df = df.drop_duplicates()

    # Replace inf with NaN and fill with median
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.fillna(df.median(numeric_only=True), inplace=True)
    return df

def create_model(data):
    X = data.drop(columns=['Label'])
    y = data['Label']

    # Normalize features
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    # Feature selection
    k_features = 10
    selector = SelectKBest(score_func=f_classif, k=k_features)
    X_selected = selector.fit_transform(X_scaled, y)

    # Split
    X_train, X_test, y_train, y_test = train_test_split(X_selected, y, test_size=0.2, random_state=42)

    # Train model
    model = XGBClassifier(
        use_label_encoder=False,
        eval_metric='logloss',
        random_state=42
    )
    model.fit(X_train, y_train)

    # Predict
    y_pred = model.predict(X_test)
    print(f"Accuracy Score: {accuracy_score(y_test, y_pred):.4f}")
    print("Classification Report:")
    print(classification_report(y_test, y_pred))

    return model, scaler, selector



def main():
    data = get_clean_data()
    model,scaler,selector = create_model(data)
    data['Label'].unique()

    # write the model with binary mode
    with open("model.pkl","wb") as f:
        joblib.dump(model, f)
    with open("scaler.pkl","wb") as f:
        joblib.dump(scaler, f)
    with open("selector.pkl","wb") as f:
        joblib.dump(selector, f)

if __name__=='__main__':
    main()
```
## 7.🐍 frontend.py
```python
import pickle
import streamlit as st
import pandas as pd
from PIL import Image
import base64
from io import BytesIO
from sklearn.preprocessing import LabelEncoder
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import requests
import os
import zipfile
from sklearn.preprocessing import StandardScaler
from math import pi
import plotly.graph_objects as go

st.set_page_config(page_title="Intrusion Detection", layout="wide")

import os
style_path = os.path.join(os.path.dirname(__file__), "style.css")

with open(style_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def unzip_selected_files(zip_path='datasets/archive.zip', extract_to='datasets/extracted'):
    selected_files = ['03-02-2018.csv', '03-01-2018.csv', '02-23-2018.csv', '02-14-2018.csv']
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file in selected_files:
            zip_ref.extract(file, path=extract_to)

def get_clean_data():
    unzip_selected_files()
    file_paths = [
        'datasets/extracted/03-02-2018.csv',
        'datasets/extracted/03-01-2018.csv',
        'datasets/extracted/02-23-2018.csv',
        'datasets/extracted/02-14-2018.csv',
    ]
    dataset_list = [pd.read_csv(path, low_memory=False, nrows=25000) for path in file_paths]
    df = pd.concat(dataset_list, ignore_index=True)
    df = df[df["Protocol"] != "Protocol"]
    df = df.drop(columns=["Timestamp", "Dst Port"], errors='ignore')
    df = df.drop(df.index[df['Label'] == 'Label'])
    df["Protocol"] = LabelEncoder().fit_transform(df["Protocol"].astype(str))
    df["Label"] = LabelEncoder().fit_transform(df["Label"])
    df["Label"] = np.where(df["Label"] == 0, 0, 1)
    df = df.dropna()
    for col in df.select_dtypes(include='object').columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna()
    df = df[df.ge(0).all(axis=1)]
    df = df.drop_duplicates()
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.fillna(df.median(numeric_only=True), inplace=True)
    return df

def radar_df():
    unzip_selected_files()
    file_paths = [
        'datasets/extracted/03-02-2018.csv',
        'datasets/extracted/03-01-2018.csv',
        'datasets/extracted/02-23-2018.csv',
        'datasets/extracted/02-14-2018.csv']
    df = pd.concat([pd.read_csv(path, low_memory=False, nrows=25000) for path in file_paths], ignore_index=True)
    df = df.dropna()
    df['AttackType'] = df['Label'].apply(lambda x: 'Benign' if x == 'Benign' else 'Malicious')
    features = ['Bwd Pkt Len Max', 'Bwd Pkt Len Mean', 'Bwd Pkt Len Std', 'Pkt Len Std',
                'RST Flag Cnt', 'ECE Flag Cnt', 'Bwd Seg Size Avg', 'Init Fwd Win Byts',
                'Init Bwd Win Byts', 'Fwd Seg Size Min']
    for feature in features:
        df[feature] = pd.to_numeric(df[feature], errors='coerce')
    df = df.dropna(subset=features)
    df_scaled = df.copy()
    scaler = StandardScaler()
    df_scaled[features] = scaler.fit_transform(df[features])
    classes = ['Benign', 'Bot', 'Infilteration', 'Brute Force -Web', 'Brute Force -XSS',
               'SQL Injection', 'FTP-BruteForce', 'SSH-Bruteforce']
    available_classes = df['Label'].unique()
    classes = [c for c in classes if c in available_classes]
    data = {label: df_scaled[df_scaled['Label'] == label][features].mean() for label in classes}
    radar_df = pd.DataFrame(data).T.T
    radar_df['feature'] = radar_df.index
    radar_df = pd.concat([radar_df, radar_df.iloc[[0]]])
    radar_df = radar_df.set_index('feature').T
    return radar_df, scaler


def get_radar_chart(radar_df, input_scaled_dict=None):
    fig = go.Figure()

    # Plot attack types from radar_df
    for index, row in radar_df.iterrows():
        fig.add_trace(go.Scatterpolar(
            r=row.tolist() + [row.tolist()[0]],
            theta=list(radar_df.columns) + [radar_df.columns[0]],
            fill='toself',
            name=index
        ))

    # Plot user input, if provided
    if input_scaled_dict:
        input_values = list(input_scaled_dict.values())
        theta = list(input_scaled_dict.keys())
        input_values.append(input_values[0])
        theta.append(theta[0])
        fig.add_trace(go.Scatterpolar(
            r=input_values,
            theta=theta,
            name="Your Input",
            line=dict(color='black', dash='dash')
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[-2, 2])),
        title="Radar Chart: Comparison of Attack Types",
        showlegend=True, width=800, height=700
    )
    return fig


@st.cache_resource
def load_model_and_scaler():
    return pickle.load(open("model.pkl", "rb")), pickle.load(open("scaler.pkl", "rb"))

def add_predictions(input_data):
    st.subheader("Attacks Predictions:")
    try:
        input_array = list(input_data.values())
        response = requests.post("http://backend:8000/predict", json={"features": input_array})
        if response.status_code != 200:
            st.error(f"API error: {response.status_code} - {response.text}")
            return
        result = response.json()
        predicted_class = result["predicted_class"]
        probabilities = result["probabilities"]
        st.success("Benign" if predicted_class == "Benign" else "Malicious")
        st.write("Probability of being Benign:", probabilities["Benign"])
        st.write("Probability of being Malicious:", probabilities["Malicious"])
    except Exception as e:
        st.error(f"Prediction failed: {e}")

if "page" not in st.session_state:
    st.session_state.page = "Main"

col1, col2, col3, col4 = st.columns([7, 1, 1, 1])
with col1:
    st.title("CyberGuard: Smart Security with AI")
with col2:
    if st.button("Main"):
        st.session_state.page = "Main"
with col3:
    if st.button("Model"):
        st.session_state.page = "Model"
with col4:
    if st.button("Analysis"):
        st.session_state.page = "Analysis"

if st.session_state.page == "Main":
    st.sidebar.title("CyberGuard: Intrusion Detection System using Machine Learning")
    st.sidebar.markdown("Built with: Docker, Streamlit, Scikit-learn, FastAPI, XGBoost")
    st.title("🏠 Welcome to the Intrusion Detection System")
    st.subheader("Use the navigation above to explore model classification or analysis.")
    image_path = "streamlit_app/images/img3.png"
    if os.path.exists(image_path):
        st.image(Image.open(image_path), caption="CyberGuard: Smart Security with AI")
    else:
        st.warning("Main page image not found.")

elif st.session_state.page == "Model":
    st.title("🔐 Intrusion Detection System")
    data = get_clean_data()

    def add_sidebar():
        st.sidebar.header("Network Logs")
        slider_labels = [
            ("Bwd Pkt Len Max (mean)", "Bwd Pkt Len Max"),
            ("Bwd Pkt Len Mean (mean)", "Bwd Pkt Len Mean"),
            ("Bwd Pkt Len Std (mean)", "Bwd Pkt Len Std"),
            ("Pkt Len Std (mean)", "Pkt Len Std"),
            ("RST Flag Cnt (mean)", "RST Flag Cnt"),
            ("ECE Flag Cnt (mean)", "ECE Flag Cnt"),
            ("Bwd Seg Size Avg (mean)", "Bwd Seg Size Avg"),
            ("Init Fwd Win Byts (mean)", "Init Fwd Win Byts"),
            ("Init Bwd Win Byts (mean)", "Init Bwd Win Byts"),
            ("Fwd Seg Size Min (mean)", "Fwd Seg Size Min")
        ]
        return {key: st.sidebar.slider(label, 0.0, float(data[key].max()), float(data[key].mean())) for label, key in slider_labels}

    input_data = add_sidebar()

    radar_data, scaler = radar_df()
    input_df = pd.DataFrame([input_data])

    input_df_scaled = scaler.transform(input_df)
    input_scaled_dict = dict(zip(input_df.columns, input_df_scaled[0]))

    col1, col2 = st.columns([4, 1])
    with col1:
        st.plotly_chart(get_radar_chart(radar_data, input_scaled_dict))
    with col2:
        add_predictions(dict(zip(input_df.columns, input_df_scaled[0])))



elif st.session_state.page == "Analysis":
    st.title("📊 Analysis")
    image_files = [
        "attacks_distribution_percentage.png", "dst_ports.png", "protocols.png",
        "ftp_bruteforce_attacks.png", "ssh_bruteforce_attacks.png",
        "distribution_of_connections.png", "tcp_flags.png"
    ]
    for file_name in image_files:
        img_path = os.path.join("streamlit_app", "images", file_name)
        if os.path.exists(img_path):
            st.image(Image.open(img_path), caption=file_name.replace(".png", "").replace("_", " ").title())
        else:
            st.warning(f"Image not found: {img_path}")
```
## 8. style.css
```css
.e1l1n2w82 {
    padding: 1rem;
    border-radius: 0.5rem;
    background-color: #7E99AB;
}
/* style.css */

/* Main background and text styling */
.stApp {
    background-color: #fdf5df;
    color: #36162E;
    font-weight: normal;
}

h1 {
    color: #594057 !important;
    font-size: 30px !important;
    font-weight: normal !important;
}
h2, h3 {
    color: #B14B4B !important;
    font-size: 23px !important;
    font-weight: normal !important;
}

/* Slider styles */
.stSlider label {
    color: #F56A47;
}
.stSlider div[data-baseweb="slider"] > div > div[role="slider"] {
    background-color: #F56A47;
}

/* Button styles */
div.stButton > button {
    padding: 0.6rem 1.2rem;
    background-color: #fdf5df;
    color: #594057;
    border-radius: 8px;
    cursor: pointer;
    margin: 0;
}
div.stButton > button:hover {
    padding: 0.6rem 1.2rem;
    border-bottom: 1px solid white;
    background-color: #594057;
    color: #fdf5df;
}

/* Custom Navbar */
.custom-navbar {
    position: sticky;
    top: 0;
    z-index: 1000;
    background-color: #0D0F16;
    display: flex;
    align-items: center;
}
.navbar-title {
    color: #594057;
    font-size: 20px;
    background-color: #0D0F16;
    padding: 0.4rem 1rem;
    border-radius: 8px;
    margin-right: 30px;
    font-weight: normal;
}
.navbar-tabs {
    display: flex;
    gap: 1;
    margin: 0;
}
.navbar-tabs button {
    background-color: #0D0F16;
    color: #594057;
    font-weight: bold;
    border-radius: 8px;
    cursor: pointer;
    margin: 0;
}
.navbar-tabs button:hover {
    padding: 1rem 2rem;
    border-bottom: 1px solid white;
    background-color: #594057;
    color: #fdf5df;
}
```


### FastAPI at: `localhost:8000` 
* `backend` on port 8000
### Streamlit UI at: `localhost:8501`
* `frontend` on port 8501
