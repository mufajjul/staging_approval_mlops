import os
import joblib
import numpy as np
import argparse

from sklearn.svm import SVC
from azureml.core import Model
from azureml.monitoring import ModelDataCollector
from inference_schema.schema_decorators import input_schema, output_schema
from inference_schema.parameter_types.numpy_parameter_type import NumpyParameterType
from inference_schema.parameter_types.standard_py_parameter_type import StandardPythonParameterType

def init():
    global model
    global inputs_dc, prediction_dc
    model_file_name = "iris-model.pkl"
    model_path = os.path.join(os.environ.get("AZUREML_MODEL_DIR"), model_file_name)
    model = joblib.load(model_path)
    inputs_dc = ModelDataCollector("sample-model", designation="inputs", feature_names=["feat1", "feat2", "feat3", "feat4"])
    prediction_dc = ModelDataCollector("sample-model", designation="predictions", feature_names=["prediction"])

@input_schema('data', NumpyParameterType(np.array([[0.1, 1.2, 2.3, 3.4]])))
@output_schema(StandardPythonParameterType({'predict': [['Iris-virginica']]}))
def run(data):
    # Use the model object loaded by init().
    result = model.predict(data)
    inputs_dc.collect(data) #this call is saving our input data into Azure Blob
    prediction_dc.collect(result) #this call is saving our input data into Azure Blob

    # You can return any JSON-serializable object.
    return { "predict": result.tolist() }
