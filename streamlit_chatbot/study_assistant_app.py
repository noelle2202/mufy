import streamlit as st
import openai
import os
import fitz  # PyMuPDF
import pandas as pd
import altair as alt
from langdetect import detect
from newspaper import Article

# 🔐 Your OpenAI API key here (replace with your real key)
OPENAI_API_KEY = "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"

# Initialize OpenAI client with API key directly
client = openai.OpenAI(api_key=OPENAI_API_KEY)

st.set_page_config(page_title="📚 AI Study Assistant", layout="wide")
st.title("📚 AI-Powered Study Assistant (One File Version)")

# --- Functions ---
def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return "".join([page.get_text() for page in doc])

def extract_text_from_url(url):
    article = Article(url)
    article.download()
    article.parse()
    return article.text

def summarize_structured_with_chart(text):
    prompt = f"""
Summarize this content into:
1. Bullet points
2. A comparison table if applicable
3. Chart data (CSV): Label,Value

Text:
{text}
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()

def generate_flashcards(notes):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Create 5 Q&A flashcards based on this:\n\n{notes}"}],
        max_tokens=1024,
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()

def extract_chart_data(structured_text):
    try:
        lines = structured_text.split("Label,Value")[-1].strip().splitlines()
        data = [line.split(",") for line in lines if "," in line]
        df = pd.DataFrame(data, columns=["Label", "Value"])
        df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
        return df.dropna()
    except Exception:
        return pd.DataFrame()

# --- App State ---
if "raw_text" not in st.session_state:
    st.session_state.raw_text = ""
if "notes" not in st.session_state:
    st.session_state.notes = ""
if "flashcards" not in st.session_state:
    st.session_state.flashcards = ""
if "chart_df" not in st.session_state:
    st.session_state.chart_df = pd.DataFrame()

# --- UI ---
input_method = st.radio("Input method:", ["📄 Upload PDF", "🌐 URL", "📝 Paste Text"])

if input_method == "📄 Upload PDF":
    file = st.file_uploader("Upload a PDF", type=["pdf"])
    if file:
        st.session_state.raw_text = extract_text_from_pdf(file)

elif input_method == "🌐 URL":
    url = st.text_input("Enter a URL:")
    if url:
        try:
            st.session_state.raw_text = extract_text_from_url(url)
        except:
            st.error("❌ Unable to extract from URL")

else:
    st.session_state.raw_text = st.text_area("Paste your text:", height=250)

if st.session_state.raw_text:
    st.success("✅ Text loaded.")

    if st.button("✍️ Generate Study Notes"):
        with st.spinner("Generating..."):
            st.session_state.notes = summarize_structured_with_chart(st.session_state.raw_text)
            st.session_state.flashcards = generate_flashcards(st.session_state.notes)
            st.session_state.chart_df = extract_chart_data(st.session_state.notes)

    if st.session_state.notes:
        st.subheader("🧩 Study Notes")
        st.markdown(st.session_state.notes)

    if st.session_state.flashcards:
        st.subheader("🧠 Flashcards")
        st.markdown(st.session_state.flashcards)

    if not st.session_state.chart_df.empty:
        st.subheader("📊 Chart")
        chart = alt.Chart(st.session_state.chart_df).mark_bar().encode(
            x="Label", y="Value", tooltip=["Label", "Value"]
        )
        st.altair_chart(chart, use_container_width=True)
