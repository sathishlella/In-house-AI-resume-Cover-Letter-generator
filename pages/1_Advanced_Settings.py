import streamlit as st

st.set_page_config(page_title="Advanced Settings", page_icon="⚙️", layout="centered")

st.title("⚙️ Advanced Settings")
with st.expander("Model & Generation Settings", expanded=True):
    st.session_state.setdefault("temperature", 0.6)
    st.session_state["temperature"] = st.slider("Temperature", 0.0, 1.2, float(st.session_state["temperature"]), 0.05)
    st.session_state.setdefault("max_words", 700)
    st.session_state["max_words"] = st.slider("Target Words (soft cap)", 200, 1500, int(st.session_state["max_words"]), 50)
    st.write("These control creativity and length hints. The LLM may not obey hard caps but treats them as guidance.")

with st.expander("Style Presets", expanded=True):
    preset = st.selectbox("Preset", ["Professional", "Concise", "Story-driven", "Technical", "Leadership"])
    if st.button("Apply Preset"):
        if preset == "Professional":
            st.session_state["style_tone"] = "professional, confident, results-oriented"
        elif preset == "Concise":
            st.session_state["style_tone"] = "crisp, minimal, bullet-heavy"
        elif preset == "Story-driven":
            st.session_state["style_tone"] = "engaging, narrative, value-focused"
        elif preset == "Technical":
            st.session_state["style_tone"] = "precise, jargon-aware, quantified"
        elif preset == "Leadership":
            st.session_state["style_tone"] = "strategic, stakeholder-savvy, impact-led"
        st.success(f"Applied tone: {st.session_state['style_tone']}")

st.caption("Changes persist in session; return to the main page to generate documents.")
