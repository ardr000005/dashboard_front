import streamlit as st
import pandas as pd
import requests
from dotenv import load_dotenv
import os

# -------------------------
# Load .env
# -------------------------
load_dotenv()

BASE = os.getenv("FLASK_URL")

st.title("📊 Clinical Data Quality Monitor")

# ----------- Scorecard -----------
st.header("Portfolio Scorecard")
score = requests.get(f"{BASE}/scorecard").json()
for k, v in score.items():
    st.metric(k.replace("_"," ").title(), v)

# ----------- Study Drilldown -----------
study_id = st.selectbox("Select Study:", sorted(range(1,26)))
data = requests.get(f"{BASE}/study/{study_id}").json()

st.subheader(f"Study {study_id} Summary")
for k, v in data.items():
    st.write(f"**{k}**: {v}")

# ----------- High Risk Subjects -----------
if st.checkbox("Show High-Risk Subjects"):
    risk = requests.get(f"{BASE}/highrisk").json()
    risk_df = pd.DataFrame(risk)
    st.dataframe(risk_df.head(100))

# ----------- Benchmarks -----------
if st.checkbox("Show Study DQI Ranking"):
    bench = requests.get(f"{BASE}/benchmarks").json()
    st.bar_chart(bench)

# ----------- Heatmap ----------
if st.checkbox("Show DQI Relationship Heatmap"):
    corr = requests.get(f"{BASE}/heatmap").json()
    corr_df = pd.DataFrame(corr)
    st.subheader("📌 Correlation Matrix")
    st.dataframe(corr_df)

    st.subheader("🔥 Heatmap")
    st.write("Darker = stronger relationship")
    st.heatmap = st.dataframe(corr_df.style.background_gradient(cmap="coolwarm"))

# ----------- AI Insight on Heatmap ----------
if st.button("Explain Heatmap"):
    try:
        resp = requests.get(f"{BASE}/heatmap-ai").json()
        if "analysis" in resp:
            st.subheader("🧠 AI Insight")
            st.write(resp["analysis"])
        else:
            st.error(resp.get("error", "Unknown error"))
    except Exception as e:
        st.error(e)


# ----------- AI Agent -----------
st.header("🤖 AI Assistant")
if st.button("Generate CRA Email"):
    try:
        resp = requests.get(f"{BASE}/cra-email/{study_id}")
        
        # If server returned non-JSON (e.g., 500 HTML), show it
        if resp.status_code != 200:
            st.error(f"Server Error {resp.status_code}")
            st.text(resp.text)
        else:
            data = resp.json()

            # If backend returned an error message JSON
            if "error" in data:
                st.error("❌ AI failed: " + data["error"])
                st.write("📌 Prompt:", data.get("prompt", ""))
            else:
                st.write("📌 Prompt:", data["prompt"])
                st.write("---")
                st.subheader("✉️ Generated Email")
                st.write(data["email"])

    except Exception as e:
        st.error("Streamlit failed to reach backend")
        st.write(e)

