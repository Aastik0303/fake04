import os
import tensorflow as tf
import numpy as np
from langchain_groq import ChatGroq
from langchain_core.tools import Tool
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from tensorflow.keras.preprocessing import image

# Model Setup
MODEL_PATH = 'deepfake_detector_model.tflite'

def predict_deepfake(img_path):
    try:
        interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
        interpreter.allocate_tensors()
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        # Preprocessing
        img = image.load_img(img_path, target_size=(128, 128))
        img_array = image.img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0).astype(np.float32)

        interpreter.set_tensor(input_details[0]['index'], img_array)
        interpreter.invoke()
        prediction = interpreter.get_tensor(output_details[0]['index'])
        
        confidence = float(prediction[0][0])
        is_fake = confidence > 0.7
        status = "Deepfake" if is_fake else "Real"
        return f"Result: {status} ({confidence*100 if is_fake else (1-confidence)*100:.1f}% confidence)"
    except Exception as e:
        return f"Model Error: {str(e)}"

# Define Tool
deepfake_tool = Tool(
    name="DeepfakeDetectionTool",
    func=predict_deepfake,
    description="Analyzes an image file path to detect if it's a deepfake or real."
)

def get_agent():
    llm = ChatGroq(
        # ✅ Yahan model ka naam 3.1 se badal kar 3.3 kar diya gaya hai
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
    return create_react_agent(llm, tools=[deepfake_tool])
