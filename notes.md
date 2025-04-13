# FastAPI + Streamlit + Docker
FastAPI backend & streamlit frontend run using docker-compose
## 1.✅ Project Structure
```bash  
myproject/
├── app/
│   ├── server.py                  # FastAPI backend
│   └── voting_classifier_final.pkl
├── streamlit_app/
│   └── frontend.py                # Streamlit frontend
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
### FastAPI at: `localhost:8000` 
* `backend` on port 8000
### Streamlit UI at: `localhost:8501`
* `frontend` on port 8501
