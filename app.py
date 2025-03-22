# app.py

import streamlit as st
import json
import random
from backend import generate_response

# Set page configuration
st.set_page_config(
    page_title="SipSync - Herbal Tea Matchmaker",
    page_icon="🍵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Main content styling */
    .main {
        background-color: #f5f5f5;
        padding: 2rem;
        border-radius: 10px;
    }
    h1, h2, h3 {
        color: #2E7D32;
        font-family: 'Georgia', serif;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        border-radius: 20px;
        padding: 10px 20px;
        font-size: 16px;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #45a049;
    }
    .recipe-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .sidebar .sidebar-content {
        background-color: #e8f5e9;
        padding: 20px;
        border-radius: 10px;
    }
    .sidebar h2 {
        color: #1B5E20;
    }
    .sidebar p {
        color: #2E7D32;
    }
</style>
""", unsafe_allow_html=True)

# Main title and description
st.title("🍵 SipSync - Daily Herbal Tea Matchmaker")
st.markdown("""
Welcome to **SipSync**, your personal herbal tea matchmaker! Whether you're feeling under the weather or just need a moment of relaxation, 
we'll help you find the perfect herbal tea to soothe your mind and body. Simply describe your ailment, and we'll recommend the best tea for you.
""")

# User input for ailment
user_input = st.text_input(
    "What's bothering you today?",
    placeholder="e.g., sore throat, can't sleep, headache"
)

# Button to find tea recommendation
if st.button("Find My Tea"):
    if not user_input:
        st.warning("Please enter an ailment.")
    else:
        with st.spinner("Finding your perfect tea..."):
            recommendation = generate_response(user_input)

            if recommendation:
                # Display tea recommendation
                st.markdown(f"## 🍵 {recommendation['tea_data']['tea']} for {recommendation['ailment'].title()}")
                st.markdown(f"*{recommendation['personalized_message']}*")

                # Benefits section
                with st.expander("✨ Benefits"):
                    for benefit in recommendation["tea_data"]["benefits"]:
                        st.markdown(f"- {benefit}")

                # Ingredients section
                with st.expander("📜 Ingredients"):
                    for ingredient in recommendation["tea_data"]["ingredients"]:
                        st.markdown(f"- {ingredient}")

                # Recipe section
                with st.expander("📝 Instructions"):
                    for step in recommendation["tea_data"]["recipe"]:
                        st.markdown(f"- {step}")

                # Brewing tip
                st.markdown(f"**🍶 Brewing Tip:** {recommendation['brewing_tip']}")

                # YouTube videos
                st.markdown("### 📺 Learn More: YouTube Videos")
                cols = st.columns(3)
                for idx, video in enumerate(recommendation["videos"]):
                    with cols[idx % 3]:
                        st.markdown(f"""
                        <div class="recipe-card">
                            <h4>{video['title']}</h4>
                            <img src="{video['thumbnail']}" alt="Thumbnail" style="width:100%; border-radius:10px;">
                            <p><b>Channel:</b> {video['channel']}</p>
                            <p><b>Description:</b> {video['description']}</p>
                            <a href="{video['url']}" target="_blank">Watch Video</a>
                        </div>
                        """, unsafe_allow_html=True)

            else:
                st.error("No tea recommendation found. Try a different ailment.")

# Sidebar for Tea of the Day
st.sidebar.header("🍵 Tea of the Day")
with open("tea_data.json", "r") as f:
    TEA_MATCHES = json.load(f)

random_tea = random.choice(list(TEA_MATCHES.values()))
st.sidebar.subheader(random_tea["tea"])
st.sidebar.markdown(f"**Perfect for:** {', '.join(random_tea['benefits'][:2])}")
st.sidebar.markdown(f"**Ingredients:** {', '.join(random_tea['ingredients'][:3])}...")
st.sidebar.markdown(f"**Recipe:** {random_tea['recipe'][0]}...")

# Disclaimer
st.sidebar.markdown("---")
st.sidebar.info("""
**Disclaimer:** This app is for educational purposes only. 
Consult a healthcare professional for medical advice.
""")

# Fun fact
st.sidebar.markdown("---")
st.sidebar.markdown("**Did you know?**")
st.sidebar.markdown("Tea is the second most consumed beverage in the world after water! 🫖")
