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
from io import BytesIO

# ------------------- Page Configuration ------------------- #
st.set_page_config(page_title="Intrusion Detection", layout="wide")

# ------------------- Handle Page Switching ------------------- #
# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "Main"

# Custom Navbar with Buttons using Session State
st.markdown("""
<style>
    .custom-navbar {
    background-color: #fdf5df;
    display: flex;
    align-items: center;

}

.navbar-title {
    color: #594057;
    font-size: 20px;
    background-color: #fdf5df;
    padding: 0.4rem 1rem;
    border-radius: 8px;
    margin-right: 30px; /* space between title and buttons */
    font-weight:normal;
}

.navbar-tabs {
    display: flex;
    gap: 1; /* reduce space between buttons */
    margin-left: 0; /* align buttons more left */
    margin: 0;
}

.navbar-tabs button {
    background-color: #fdf5df;
    color: #594057;
    font-weight: normal;
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
</style>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
with col1:
    st.markdown('<div class="navbar-title" >CyberGuard: Smart Security with AI 🛡️👁️‍🗨️⚙️</div>', unsafe_allow_html=True)
with col2:
    if st.button("Main"):
        st.session_state.page = "Main"
with col3:
    if st.button("Model"):
        st.session_state.page = "Model"
with col4:
    if st.button("Analysis"):
        st.session_state.page = "Analysis"



# ------------------- Sidebar Background ------------------- #
def set_sidebar_background(image_path):
    with open(image_path, "rb") as img_file:
        encoded_string = base64.b64encode(img_file.read()).decode()
    sidebar_style = f"""
    <style>
        [data-testid="stSidebar"] > div:first-child {{
            background-image: url("data:image/jpeg;base64,{encoded_string}");
            background-repeat: no-repeat;
           background-size: 120% auto;  /* adjust the size here */
           background-position: center 104%;  /* lower it toward the bottom */
            min-height: 40vh;
            color: white;
        }}
    </style>
    """
    st.markdown(sidebar_style, unsafe_allow_html=True)

set_sidebar_background("streamlit_app/images/img2.png")

# Sidebar content
st.sidebar.markdown("## 💻 CyberGuard: Intrusion Detection System using Machine Learning")
st.sidebar.markdown("""
This website was developed using:
- 🐳 Docker  
- 🔧 Streamlit  
- 🤖 Scikit-learn  
- 🌐 FastAPI (for backend API)  
- 🧠 Machine Learning models (e.g., XGBoost, Random Forest, Decision Tree)
""")

# ------------------- Custom CSS Styling ------------------- #
st.markdown("""
<style>
    .stApp {
        background-color: #fdf5df;
        color: #36162E;
         font-weight:normal;
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


    .stSlider label {
        color: #F56A47;
     
    }
    .stSlider div[data-baseweb="slider"] > div > div[role="slider"] {
        background-color: #F56A47;
    }
    div.stButton > button {
        padding: 0.6rem 1.2rem;
        background-color: #fdf5df;
        color: #594057;
        border-radius: 8px;
        cursor: pointer;
        margin: 0; /* remove default spacing */

    }
    div.stButton > button:hover {
     padding: 0.6rem 1.2rem;
    border-bottom: 1px solid white;
    background-color: #594057;
    color: #fdf5df;
 
    }
</style>
""", unsafe_allow_html=True)

# ------------------- Main Page ------------------- #
if st.session_state.page == "Main":
    st.markdown("<h1 style='text-align: center;'>🏠 Welcome to the Intrusion Detection System</h1>",
                unsafe_allow_html=True)
    st.markdown(
        "<h2 style='text-align: left; padding-left: 80px; font-weight: normal;'>Use the navigation above to explore model classification or analysis.</h2>",
        unsafe_allow_html=True)

    image_path = r"streamlit_app/images/img3.png"
    if os.path.exists(image_path):
        img = Image.open(image_path)
        # Resize while maintaining aspect ratio
        base_height = 450  # adjust height here
        h_percent = base_height / float(img.size[1])
        new_width = int(float(img.size[0]) * h_percent)
        resized_img = img.resize((new_width, base_height))
        #st.image(resized_img, caption="CyberGuard: Smart Security with AI", use_container_width=False)

        # Convert to base64
        buffered = BytesIO()
        resized_img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        # Center the image using HTML
        st.markdown(
            f"""       <div style="text-align: center;">
                           <img src="data:image/png;base64,{img_str}" width="{new_width}" height="{base_height}">
                           <p style="color: gray;">CyberGuard: Smart Security with AI</p>
                       </div>
                       """,
            unsafe_allow_html=True
        )

    else:
        st.warning("Main page image not found.")


# ------------------- Model Page ------------------- #
elif st.session_state.page == "Model":
    st.markdown("<h1 style='text-align: center;'>🔐 Intrusion Detection System</h1>", unsafe_allow_html=True)
    df = pd.read_csv("streamlit_app/features.csv")
    selected_features = [
        "Bwd Pkt Len Mean", "Pkt Len Max", "ECE Flag Cnt",
        "Init Fwd Win Byts", "Init Bwd Win Byts", "Fwd Act Data Pkts"
    ]
    st.markdown("<h2>📊 Select Feature Values</h2>", unsafe_allow_html=True)
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
elif st.session_state.page == "Analysis":
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
