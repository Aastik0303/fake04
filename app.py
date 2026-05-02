import streamlit as st
import os
from agents import get_agent
from langchain_core.messages import HumanMessage, SystemMessage
from PIL import Image

# UI Configuration
st.set_page_config(page_title="Deepfake Detector AI", page_icon="🔍", layout="centered")

st.title("🔍 Deepfake Detection System")
st.markdown("### AI-Powered Authenticity Analysis with LangGraph & Groq")

# Initialize Agent
if 'agent' not in st.session_state:
    try:
        st.session_state.agent = get_agent()
    except Exception as e:
        st.error(f"Agent Initialization Failed: {e}")

# File Upload
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Preview Image
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded Image", use_column_width=True)
    
    if st.button("🔬 Analyze Image"):
        with st.spinner("Our AI agent is examining the image..."):
            # ✅ Temp file ko directly bahar hi save kar rahe hain (koi 'uploads' folder nahi banega)
            temp_path = uploaded_file.name
            
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            try:
                # Agent Execution
                system_msg = SystemMessage(content="You are a deepfake expert. Explain the technical findings of the detection tool clearly.")
                user_msg = HumanMessage(content=f"Analyze this image: {temp_path}")
                
                response = st.session_state.agent.invoke({"messages": [system_msg, user_msg]})
                
                # Show Results
                st.success("Analysis Complete!")
                st.markdown("#### AI Insights:")
                st.write(response["messages"][-1].content)
                
            except Exception as e:
                st.error(f"Analysis Failed: {e}")
            finally:
                # Cleanup (Image analyze hone ke baad automatically delete ho jayegi)
                if os.path.exists(temp_path):
                    os.remove(temp_path)

st.divider()
st.info("How it works: This system uses a CNN-based TFLite model for pixel analysis and a LangGraph ReAct agent for context-aware explanations.")
