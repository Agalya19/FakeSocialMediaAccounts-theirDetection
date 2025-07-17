import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os

if not os.path.exists("fake_accounts.csv"):
    print("Error: 'fake_accounts.csv' not found.")
    exit()

data = pd.read_csv("fake_accounts.csv")

required_columns = ["followers", "following", "posts", "verified", "label"]
if not all(col in data.columns for col in required_columns):
    print("CSV must include: followers, following, posts, verified, label")
    exit()

X = data[["followers", "following", "posts", "verified"]]
y = data["label"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

accuracy = accuracy_score(y_test, model.predict(X_test))
print(f"Model Accuracy: {accuracy:.2f}")

joblib.dump(model, "fake_account_detector.pkl")
print("Model saved as 'fake_account_detector.pkl'")
