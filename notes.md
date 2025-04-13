# FastAPI + Streamlit + Docker
FastAPI backend & streamlit frontend run using docker-compose
## 1.✅ Project Structure
```bash  
myproject/
├── app/
│   ├── server.py                  # FastAPI backend
│   └── voting_classifier_final.pkl
├── streamlit_app/
│   ├── frontend.py                # Streamlit frontend
│   ├── Features.csv  
│   ├── images/ 
│   └── .....
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
```
## 2.🐳 Dockerfile
```Dockerfile 
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["bash"]
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
fastapi
uvicorn
joblib
numpy==1.23.5
scikit-learn==1.2.2
xgboost==2.0.3
scipy
pydantic
streamlit
requests
```
## 5.🚀requirements.txt
```bash
docker-compose up --build
```
## 6.🐍 frontend.py
```python
import streamlit as st
import pandas as pd
import requests
from PIL import Image
import os
import base64

# --- Page Config ---
st.set_page_config(page_title="Intrusion Detection", layout="wide")

# --- Initialize Session State ---
if "page" not in st.session_state:
    st.session_state.page = "Main"

# --- Set Sidebar Background Image ---
def set_sidebar_background(image_path):
    with open(image_path, "rb") as img_file:
        encoded_string = base64.b64encode(img_file.read()).decode()
    sidebar_style = f"""
    <style>
        [data-testid="stSidebar"] > div:first-child {{
            background-image: url("data:image/jpeg;base64,{encoded_string}");
            background-size: cover;
            background-repeat: no-repeat;
            background-position: center;
        }}
    </style>
    """
    st.markdown(sidebar_style, unsafe_allow_html=True)

set_sidebar_background("streamlit_app/images/img.jpeg")

# --- Custom CSS Styling ---
st.markdown("""
    <style>
        /* App background and main color */
        .stApp {
            background-color: #fdf5df;
            color: #36162E;
            font-weight: bold;
        }

        /* Header styling */
        .header-tabs {
            background-color: #36162E;
            padding: 16px;
            display: flex;
            justify-content: center;
            gap: 40px;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        .header-tabs a {
            text-decoration: none;
            color: white;
            border: 2px solid white;
            padding: 10px 25px;
            border-radius: 12px;
            font-size: 18px;
            font-weight: bold;
            transition: 0.3s ease-in-out;
        }
        .header-tabs a:hover {
            background-color: white;
            color: #36162E;
        }
        .header-tabs .active {
            background-color: white;
            color: #36162E;
        }

        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #36162E !important;
        }
        .stSidebar .sidebar-content {
            background-color: #36162E !important;
            color: white;
        }

        /* Button styling */
        div.stButton > button {
            background-color: white !important;
            color: #36162E !important;
            border: 2px solid #F56A47;
            border-radius: 8px;
            padding: 0.5em 1em;
            font-weight: bold;
            font-size: 16px;
            transition: 0.3s ease-in-out;
        }
        div.stButton > button:hover {
            background-color: #36162E !important;
            color: white !important;
        }

        /* Slider label and thumb */
        .stSlider label {
            color: #F56A47 !important;
            font-weight: bold !important;
        }
        .css-14g5mt7 .stSlider > div > div > div > div[role="slider"] {
            background-color: #F56A47 !important;
        }
        .stSlider .css-1cpxqw2 {
            color: #36162E !important;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# --- Header Navigation Bar ---
current_page = st.session_state.page
st.markdown(f"""
    <div class="header-tabs">
        <a class="{ 'active' if current_page == 'Main' else '' }" href="?page=Main">🔐 Main</a>
        <a class="{ 'active' if current_page == 'Analysis' else '' }" href="?page=Analysis">📊 Analysis</a>
    </div>
""", unsafe_allow_html=True)

# --- MAIN PAGE ---
if current_page == "Main":
    st.markdown("<h1 style='text-align: center;'>🔐 Intrusion Detection System</h1>", unsafe_allow_html=True)

    df = pd.read_csv("streamlit_app/features.csv")
    selected_features = [
        "Bwd Pkt Len Mean",
        "Pkt Len Max",
        "ECE Flag Cnt",
        "Init Fwd Win Byts",
        "Init Bwd Win Byts",
        "Fwd Act Data Pkts"
    ]

    st.subheader("📊 Select Feature Values")
    feature_values = []
    for feature in selected_features:
        min_val = float(df[feature].min())
        max_val = float(df[feature].max())
        default_val = float(df[feature].mean())
        value = st.slider(
            label=feature,
            min_value=min_val,
            max_value=max_val,
            value=default_val,
            step=(max_val - min_val) / 100
        )
        feature_values.append(value)

    if st.button("Classify"):
        try:
            payload = {"features": feature_values}
            response = requests.post("http://backend:8000/predict", json=payload)
            result = response.json()
            st.success(f"The Response from the API = **{result['predicted_class']}**")
        except Exception as e:
            st.error(f"Something went wrong: {e}")

# --- ANALYSIS PAGE ---
elif current_page == "Analysis":
    st.markdown("<h1 style='text-align: center;'>📊 Analysis</h1>", unsafe_allow_html=True)

    image_files = [
        "attacks_distribution_percentage.png",
        "dst_ports.png",
        "protocols.png",
        "ftp_bruteforce_attacks.png",
        "ssh_bruteforce_attacks.png",
        "distribution_of_connections.png",
        "tcp_flags.png"
    ]

    for file_name in image_files:
        img_path = os.path.join("streamlit_app", "images", file_name)
        try:
            img = Image.open(img_path)
            caption = file_name.replace(".png", "").replace("_", " ").title()
            st.image(img, caption=caption)
        except FileNotFoundError:
            st.warning(f"Image not found: {img_path}")

```

### FastAPI at: `localhost:8000` 
* `backend` on port 8000
### Streamlit UI at: `localhost:8501`
* `frontend` on port 8501
