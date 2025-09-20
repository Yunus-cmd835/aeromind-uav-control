import streamlit as st
import pandas as pd
import pydeck as pdk
from utils import get_live_drone_data, predict_paths, detect_anomalies, load_historical_data
from datetime import datetime

st.set_page_config(page_title="AeroMind", layout="wide")

# 🌐 Language Toggle
language = st.sidebar.selectbox("🌐 Language", ["English", "தமிழ்", "हिन्दी"])

# 🗣️ Translation Dictionary
translations = {
    "English": {
        "title": "🛸 AeroMind: UAV Traffic Control System",
        "mission_status": "Airspace monitoring active.",
        "no_anomalies": "✅ No anomalies detected. All systems nominal.",
        "anomalies_found": "🚨 Anomalies detected! Immediate attention required.",
        "replay_mode": "⏪ Mission Replay Mode",
        "select_timestamp": "Select Replay Timestamp",
        "selected_time": "Selected timestamp",
        "live_map": "📍 Live Drone Map",
        "predictions": "🧠 Predicted Paths & Risk Zones",
        "alerts": "⚠️ Anomaly Alerts",
        "control_panel": "🧭 Mission Control Panel",
        "identity_panel": "🔐 Drone Identity & Security"
    },
    "தமிழ்": {
        "title": "🛸 AeroMind: வான்வழி ட்ரோன் கண்காணிப்பு அமைப்பு",
        "mission_status": "வான்வழி கண்காணிப்பு செயல்பாட்டில் உள்ளது.",
        "no_anomalies": "✅ எந்த சிக்கலும் இல்லை. அனைத்து அமைப்புகளும் சாதாரணமாக இயங்குகின்றன.",
        "anomalies_found": "🚨 சிக்கல்கள் கண்டறியப்பட்டுள்ளன! உடனடி கவனம் தேவை.",
        "replay_mode": "⏪ மிஷன் மீள்பார்வை",
        "select_timestamp": "மீள்பார்வை நேரத்தை தேர்ந்தெடுக்கவும்",
        "selected_time": "தேர்ந்தெடுக்கப்பட்ட நேரம்",
        "live_map": "📍 ட்ரோன் வரைபடம்",
        "predictions": "🧠 எதிர்பார்க்கப்பட்ட பாதைகள் மற்றும் அபாய மதிப்பீடு",
        "alerts": "⚠️ சிக்கல் எச்சரிக்கைகள்",
        "control_panel": "🧭 மிஷன் கட்டுப்பாட்டு பேனல்",
        "identity_panel": "🔐 ட்ரோன் அடையாளம் மற்றும் பாதுகாப்பு"
    },
    "हिन्दी": {
        "title": "🛸 AeroMind: यूएवी ट्रैफिक कंट्रोल सिस्टम",
        "mission_status": "हवाई क्षेत्र निगरानी सक्रिय है।",
        "no_anomalies": "✅ कोई विसंगति नहीं मिली। सभी सिस्टम सामान्य हैं।",
        "anomalies_found": "🚨 विसंगतियाँ मिलीं! तुरंत ध्यान देने की आवश्यकता है।",
        "replay_mode": "⏪ मिशन रिप्ले मोड",
        "select_timestamp": "रिप्ले टाइमस्टैम्प चुनें",
        "selected_time": "चयनित समय",
        "live_map": "📍 लाइव ड्रोन मानचित्र",
        "predictions": "🧠 अनुमानित मार्ग और जोखिम क्षेत्र",
        "alerts": "⚠️ विसंगति अलर्ट",
        "control_panel": "🧭 मिशन नियंत्रण पैनल",
        "identity_panel": "🔐 ड्रोन पहचान और सुरक्षा"
    }
}

# Sidebar Branding & Controls
st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Thales_Logo.svg/2560px-Thales_Logo.svg.png",
    width=180
)
st.sidebar.title("🧭 AeroMind Control Panel")
selected_role = st.sidebar.selectbox("User Role", ["ATC Operator", "Admin"])
refresh_rate = st.sidebar.slider("Refresh Rate (sec)", 1, 30, 5)

st.sidebar.markdown("### 🛰️ Mission Status")
st.sidebar.success(translations[language]["mission_status"])
st.sidebar.info(f"Last update: {pd.Timestamp.now().strftime('%H:%M:%S')}")

st.sidebar.markdown("### 🎖️ Domain Impact")
st.sidebar.markdown("""
- 🛡️ **Defence & Security**  
- ✈️ **Aeronautics & Space**  
- 🔐 **Cybersecurity & Digital Identity**
""")

# Header
st.title(translations[language]["title"])
st.markdown("""
AeroMind is a next-gen UAV traffic control system designed for Thales’s aerospace missions.  
It delivers real-time drone tracking, AI-powered path prediction, and anomaly alerts—secure, scalable, and ready for deployment.
""")

# Load Data
drone_df = get_live_drone_data()
hist_df = load_historical_data()
hist_df["timestamp"] = pd.to_datetime(hist_df["timestamp"])
timestamps = hist_df["timestamp"].dropna().sort_values().dt.to_pydatetime().tolist()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    translations[language]["live_map"],
    translations[language]["replay_mode"],
    translations[language]["predictions"],
    translations[language]["identity_panel"]
])

# 📍 Live Map Tab
with tab1:
    st.subheader(translations[language]["live_map"])
    map_color = '[0, 255, 255, 160]' if selected_role == "Admin" else '[255, 165, 0, 160]'
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/dark-v10',
        initial_view_state=pdk.ViewState(
            latitude=drone_df['lat'].mean(),
            longitude=drone_df['lon'].mean(),
            zoom=6,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=drone_df,
                get_position='[lon, lat]',
                get_color=map_color,
                get_radius=1000,
            ),
        ],
    ))
    st.dataframe(drone_df)

# ⏪ Mission Replay Tab
with tab2:
    st.subheader(translations[language]["replay_mode"])
    if timestamps:
        selected_time = st.slider(
            translations[language]["select_timestamp"],
            min_value=timestamps[0],
            max_value=timestamps[-1],
            value=timestamps[0],
            format="YYYY-MM-DD HH:mm:ss"
        )
        replay_df = hist_df[
            hist_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S") ==
            selected_time.strftime("%Y-%m-%d %H:%M:%S")
        ]
        st.info(f"{translations[language]['selected_time']}: {selected_time.strftime('%Y-%m-%d %H:%M:%S')}")
        st.map(replay_df[["lat", "lon"]])
        st.dataframe(replay_df)
    else:
        st.warning("No valid timestamps found in historical data.")

# 🧠 Predictions & Alerts Tab
with tab3:
    st.subheader(translations[language]["predictions"])
    predictions = predict_paths(drone_df)
    st.dataframe(predictions.style.highlight_max(axis=0), use_container_width=True)

    st.subheader(translations[language]["alerts"])
    anomalies = detect_anomalies(drone_df)
    if anomalies.empty:
        st.success(translations[language]["no_anomalies"])
    else:
        st.error(translations[language]["anomalies_found"])
        st.dataframe(anomalies.style.highlight_null(color='red'), use_container_width=True)

# 🔐 Identity & Control Tab
with tab4:
    with st.expander(translations[language]["control_panel"]):
        st.button("Pause All Drones")
        st.button("Activate Emergency Protocol")
        st.selectbox("Reroute Drone", drone_df["drone_id"])

    with st.expander(translations[language]["identity_panel"]):
        st.dataframe(drone_df[["drone_id", "public_key", "role"]])
        selected_drone = st.selectbox("Select Drone for Secure Command", drone_df["drone_id"])
        st.text_input("🔑 Enter Command (e.g., REROUTE, EMERGENCY)")
        st.button("🔒 Simulate Encrypted Dispatch")

# Footer
st.markdown("---")
st.markdown("✅ **Built for Thales GenTech Hackathon 2025**")
st.markdown("🔧 Powered by Streamlit, Python, and open-source intelligence")
st.caption("Designed for real-world deployment across Defence, Aerospace, and Cybersecurity domains.")