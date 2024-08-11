import os
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from data.data_handler import load_data

# --------------------- Funciones de carga desde MongoDB y entrenamiento del modelo (adaptada para colecciones por usuario) ---------------------
def train_model(user_id):
    X, y = load_data(user_id)
    
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    
    if X.shape[1] != 6:
        raise ValueError("X no tiene el número requerido de columnas.")
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(class_weight='balanced')
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, zero_division=0)
    conf_matrix = confusion_matrix(y_test, y_pred)

    print(f"Accuracy: {accuracy:.2f}")
    print("Classification Report:\n", report)
    print("Confusion Matrix:\n", conf_matrix)
    
    cv_scores = cross_val_score(model, X, y, cv=5)
    print(f"Cross-validation scores: {cv_scores}")
    print(f"Mean CV score: {cv_scores.mean()}")

    model_path = f'model_{user_id}.pkl'
    joblib.dump(model, model_path)
    return model

def load_model(user_id):
    model_path = f'model_{user_id}.pkl'
    if os.path.exists(model_path):
        return joblib.load(model_path)
    else:
        return train_model(user_id)

def compare_teams(team1_data, team2_data, model):
    combined_data = np.array(team1_data[:3] + team2_data[:3]).reshape(1, -1)
    prediction_proba = model.predict_proba(combined_data)[0]
    result = np.argmax(prediction_proba)
    return result, prediction_proba
