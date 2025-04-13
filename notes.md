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

# ------------------- Page Configuration ------------------- #
st.set_page_config(page_title="Intrusion Detection", layout="wide")

# ------------------- Handle Page Switching ------------------- #
query_params = st.query_params
page = query_params.get("page", ["Main"])[0]

# ------------------- Dynamic Navbar Styling ------------------- #
main_active = "background-color: white; color: #36162E;" if page == "Main" else ""
analysis_active = "background-color: white; color: #36162E;" if page == "Analysis" else ""

st.markdown(f"""
    <style>
        .custom-navbar {{
            background-color: #fdf5df;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 2rem;
            border-bottom: 1px solid #ccc;
        }}
        .navbar-title {{
            color: #36162e;
            font-size: 24px;
            font-weight: bold;
        }}
        .navbar-tabs button {{
            margin-left: 10px;
            padding: 0.6rem 1.2rem;
            background-color: #fdf5df;
            color: #36162E;
            border-radius: 8px;
        }}
        .navbar-tabs button:hover {{
            margin-left: 10px;
            border: 2px solid white;
            border-radius: 8px;
            padding: 0.5em 1em;
            font-weight: bold;
            font-size: 16px;
            transition: 0.3s ease-in-out;
            backgroud-color:white;
        }}
    </style>
    <div class="custom-navbar">
        <div class="navbar-title">Intrusion Detection System</div>
        <div class="navbar-tabs">
            <form method="get">
                <button type="submit" name="page" value="Main" style="{main_active}">Main</button>
                <button type="submit" name="page" value="Analysis" style="{analysis_active}">Analysis</button>
            </form>
        </div>
    </div>
""", unsafe_allow_html=True)

# ------------------- Sidebar Background ------------------- #
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
            min-height: 100vh;
            color:#36162e;
        }}
    </style>
    """
    st.markdown(sidebar_style, unsafe_allow_html=True)


set_sidebar_background("streamlit_app/images/img.jpeg")
# Sidebar content
st.sidebar.markdown("## CyberGuard: Intrusion Detection System using Machine Learning")
st.sidebar.write("""Key Technologies:
- **Machine Learning** for classification and threat detection
- **Docker** for containerization
- **Streamlit** for interactive web interface (frontend)
- **fastAPI** for data handling (backend)
- **Requests** to integrate with backend APIs for predictions

### How It Works:
- The user selects feature values from the network traffic data.
- A machine learning model predicts whether the traffic is malicious or normal.
- The system also provides visual analysis of attack patterns and network traffic characteristics.
""")
# ------------------- Custom CSS Styling ------------------- #
st.markdown("""
    <style>
        .stApp {
            background-color: #fdf5df;
            color: #36162E;
            font-weight: bold;
        }
        h1, h2, h3 {
            color: #594057;
        }
        .stSlider label {
            color: #F56A47 ;
            font-weight: bold ;
        }
        .stSlider div[data-baseweb="slider"] > div > div[role="slider"] {
            background-color: #F56A47 ;
        }
        div.stButton > button {
            padding: 0.6rem 1.2rem;
            background-color: #fdf5df;
            color: #36162E;
            border-radius: 8px;
            cursor: pointer;
            border: 2px solid white;
        }
        div.stButton > button:hover {
            background-color: #fdf5df ;
            color: #36162E ;
            padding: 0.5em 1em;
            font-weight: bold;
            font-size: 16px;
            transition: 0.3s ease-in-out;
            border: 2px solid white;
        }
    </style>
""", unsafe_allow_html=True)

# ------------------- Main Page ------------------- #
if page == "Main":
    st.markdown("<h1 style='text-align: center;'>🔐 Intrusion Detection System</h1>", unsafe_allow_html=True)
    df = pd.read_csv("streamlit_app/features.csv")
    selected_features = [
        "Bwd Pkt Len Mean", "Pkt Len Max", "ECE Flag Cnt",
        "Init Fwd Win Byts", "Init Bwd Win Byts", "Fwd Act Data Pkts"
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
            payload = {"features": feature_values}
            response = requests.post("http://backend:8000/predict", json=payload)
            result = response.json()
            st.success(f"The Response from the API = **{result['predicted_class']}**")

# ------------------- Analysis Page ------------------- #
elif page == "Analysis":
    st.markdown("<h1 style='text-align: center;'>📊 Analysis</h1>", unsafe_allow_html=True)
    image_files = [
        "attacks_distribution_percentage.png", "dst_ports.png", "protocols.png",
        "ftp_bruteforce_attacks.png", "ssh_bruteforce_attacks.png",
        "distribution_of_connections.png", "tcp_flags.png"
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
