import streamlit as st
import pandas as pd

st.set_page_config(page_title="Product Scanner", layout="wide")

st.title(" TikTok Product Scanner")

#  REFRESH BUTTON (replaces scan)
if st.button(" Refresh Results"):
    st.rerun()

# 🔹 LOAD DATA
try:
    df = pd.read_csv("results.csv")

    #  STATS
    col1, col2, col3 = st.columns(3)
    col1.metric("Winners", len(df[df["verdict"] == "SELL THIS"]))
    col2.metric("Tests", len(df[df["verdict"] == "TEST"]))
    col3.metric("Skipped", len(df[df["verdict"] == "SKIP"]))

    #  FILTER
    min_conf = st.slider("Minimum Confidence", 0, 100, 50)
    df = df[df["confidence"] >= min_conf]

    #  SORT
    df = df.sort_values(by="score", ascending=False)

    #  TOP 5
    st.subheader(" Top 5 Products")
    top5 = df[df["verdict"] != "SKIP"].head(5)

    for i, row in enumerate(top5.itertuples(), 1):
        st.markdown(f"""
        ### #{i} — {row.name}
        **Score:** {row.score}  
        **Confidence:** {row.confidence}%  
        **Verdict:** {row.verdict}
        """)

    #  COLOR FUNCTION
    def color_verdict(val):
        if val == "SELL THIS":
            return "background-color: #16a34a; color: white;"
        elif val == "TEST":
            return "background-color: #eab308; color: black;"
        else:
            return "background-color: #dc2626; color: white;"

    styled_df = df.style.applymap(color_verdict, subset=["verdict"])

    st.subheader(" All Results")
    st.dataframe(styled_df, use_container_width=True)

except:
    st.warning("No results yet. Run app.py first to generate results.")