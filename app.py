from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd
from tensorflow.keras.models import load_model
import json
from flask_cors import CORS
import sklearn
import sys
import types
import os

# ---- Compatibility shims for older sklearn versions ----
try:
    from sklearn.compose._column_transformer import _RemainderColsList  # noqa: F401
except Exception:
    module_name = "sklearn.compose._column_transformer"
    if module_name not in sys.modules:
        sys.modules[module_name] = types.ModuleType(module_name)
    mod = sys.modules[module_name]

    if not hasattr(mod, "_RemainderColsList"):
        class _RemainderColsList:
            """Stub for older sklearn pickle compatibility."""
            pass
        setattr(mod, "_RemainderColsList", _RemainderColsList)

# Patch missing attribute used by newer sklearn pipelines
from sklearn.compose import ColumnTransformer

if not hasattr(ColumnTransformer, "_name_to_fitted_passthrough"):
    def _dummy(self):
        return {}
    ColumnTransformer._name_to_fitted_passthrough = property(_dummy)
# ---- End shims ----

app = Flask(__name__)
CORS(app)

print(f"✅ scikit-learn version: {sklearn.__version__}")

# Load preprocessing pipeline
try:
    updated_preprocessor = joblib.load('updated_preprocessing_pipeline.pkl')
    print("✅ Preprocessing pipeline loaded successfully.")
except Exception as e:
    print("\n❌ Failed to load 'updated_preprocessing_pipeline.pkl'")
    print("👉 It might have been trained with a different scikit-learn version.")
    print("   If issues persist, install scikit-learn==1.5.2 on Python 3.9+.\n")
    raise

# Load trained model
try:
    loaded_model = load_model('heart_attack.h5')
    print("✅ Keras model loaded successfully.")
except Exception as e:
    print("\n❌ Failed to load 'heart_attack.h5'")
    raise

# Load column names
try:
    with open("columns.json", "r") as f:
        selected_feature_names = json.load(f)['data_columns']
    print("✅ Feature columns loaded successfully.")
except Exception as e:
    print("\n❌ Failed to load 'columns.json' or parse 'data_columns'.")
    raise


@app.route('/')
def index():
    return render_template('index.html', columns=selected_feature_names)


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        feature_values = [data.get(feature, "Missing") for feature in selected_feature_names]

        # Check for missing inputs
        if "Missing" in feature_values:
            missing_features = [
                selected_feature_names[i] for i, value in enumerate(feature_values) if value == "Missing"
            ]
            return jsonify({"error": f"Missing features: {missing_features}"}), 400

        # Create DataFrame
        input_df = pd.DataFrame([feature_values], columns=selected_feature_names)

        # Preprocess
        processed_input = updated_preprocessor.transform(input_df)
        processed_input = processed_input.astype('float32')

        # Predict
        risk_score = loaded_model.predict(processed_input)[0][0]
        prediction = "High Risk" if risk_score >= 0.5 else "Low Risk"

        return jsonify({
            "risk_score": float(risk_score),
            "prediction": prediction
        })

    except Exception as e:
        print(f"\n⚠️ Error in /predict: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # ✅ Render fix: Bind to all interfaces and dynamic port
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
