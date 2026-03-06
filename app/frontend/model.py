import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report
import os

def load_and_clean_data():
    file_paths = [
        'datasets/extracted/03-02-2018.csv',
        'datasets/extracted/03-01-2018.csv',
        'datasets/extracted/02-23-2018.csv',
        'datasets/extracted/02-14-2018.csv',
    ]

    df_list = []
    for path in file_paths:
        df = pd.read_csv(path, low_memory=False)
        df = df[df["Protocol"] != "Protocol"]
        df_list.append(df)

    df = pd.concat(df_list, ignore_index=True)

    # Drop columns
    df = df.drop(columns=["Timestamp", "Dst Port"], errors='ignore')

    # Drop irrelevant label rows
    df = df[df["Label"] != "Label"]

    # Label encoding
    df["Protocol"] = df["Protocol"].astype(str)
    df["Protocol"] = LabelEncoder().fit_transform(df["Protocol"])
    df["Label"] = LabelEncoder().fit_transform(df["Label"])
    df["Label"] = np.where(df["Label"] == 0, 0, 1)

    # Remove invalid and missing values
    df = df.dropna()
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.fillna(df.median(numeric_only=True), inplace=True)
    df = df[df.ge(0).all(axis=1)]
    df = df.drop_duplicates()

    # Convert any remaining object columns
    for col in df.select_dtypes(include='object').columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df.dropna(inplace=True)

    return df

def build_pipeline():
    pipeline = Pipeline([
        ('scaler', MinMaxScaler()),
        ('selector', SelectKBest(score_func=f_classif, k=10)),
        ('classifier', XGBClassifier(
            use_label_encoder=False,
            eval_metric='logloss',
            random_state=42
        ))
    ])
    return pipeline

def train_and_evaluate(data):
    X = data.drop(columns=["Label"])
    y = data["Label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print("Classification Report:\n", classification_report(y_test, y_pred))

    return pipeline

def save_model(pipeline, path="final_model.pkl"):
    with open(path, "wb") as f:
        joblib.dump(pipeline, f)

def main():
    data = load_and_clean_data()
    model_pipeline = train_and_evaluate(data)
    save_model(model_pipeline)

if __name__ == "__main__":
    main()
