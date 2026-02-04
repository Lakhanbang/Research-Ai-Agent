import os
from dotenv import load_dotenv
from ddgs import DDGS
import streamlit as st
from datetime import datetime

load_dotenv()

# Set default max results
DEFAULT_MAX_RESULTS = 5

st.set_page_config(page_title="Research & Report Builder", layout="wide")

# Apply custom CSS for background, banner, and styling
st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(90deg, #000000, #1e3c72, #ffffff);
            color: #ffffff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .banner {
            background: linear-gradient(90deg, #004080, #0073e6);
            color: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 20px;
        }
        .banner h1 {
            font-size: 2.5em;
            margin: 0;
        }
        .banner p {
            font-size: 1.2em;
            margin: 5px 0 0 0;
        }
        h1, h2, h3, h4, h5, h6 {
            color: white;
        }
        .stButton button {
            background-color: #004080;
            color: white;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: bold;
            transition: background-color 0.3s ease;
        }
        .stButton button:hover {
            background-color: #0059b3;
        }
        .css-1d391kg p, .css-1d391kg span, .css-1d391kg div {
            font-size: 16px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Custom banner
st.markdown(
    """
    <div class="banner">
        <h1>✨ ReportGenie ✨</h1>
        <p> Magical, fast report creation</p>
        <p>Search • Summarize • Write • Save</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("<span style='color:#FFF;'>Enter a topic, fetch top search results, build a markdown report, and save/download it.", unsafe_allow_html=True)

# Sidebar: options
with st.sidebar:
    st.header("⚙️ Options")
    max_results = st.number_input("Max search results", min_value=1, max_value=20, value=DEFAULT_MAX_RESULTS)
    include_snippets = st.checkbox("Include snippets in auto-summary", value=True)
    use_groq = st.checkbox("Enable Groq/LLM integration (optional)", value=False)
    groq_api_key = st.text_input("LLM API key (if using)", type="password") if use_groq else None
    st.markdown("---")
    st.markdown("**💡 Tip:** Use the editor to refine the generated markdown before saving.")

# Main UI
topic = st.text_input("🔍 Topic", placeholder="Enter the topic you want a report on...")
col1, col2 = st.columns([1, 1])

with col1:
    if st.button("🔎 Search"):
        if not topic.strip():
            st.warning("⚠️ Please enter a topic first.")
        else:
            with st.spinner("Searching DuckDuckGo..."):
                try:
                    ddgs = DDGS()
                    results = list(ddgs.text(topic, max_results=max_results, region='us-en'))
                except Exception as e:
                    st.error(f"❌ Search failed: {e}")
                    results = []

            if results:
                st.success(f"✅ Found {len(results)} results")
                st.session_state["search_results"] = results
            else:
                st.info("ℹ️ No results found.")

with col2:
    if st.button("📝 Auto-generate report"):
        if "search_results" not in st.session_state or not topic.strip():
            st.warning("⚠️ You need to perform a search first and provide a topic.")
        else:
            results = st.session_state.get("search_results", [])
            md_lines = []
            md_lines.append(f"# Research report: {topic}\n")
            md_lines.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
            md_lines.append("## Executive summary\n")

            md_lines.append("Brief summary synthesized from top search results:\n")
            for i, r in enumerate(results, start=1):
                title = r.get('title', 'No title')
                href = r.get('href', '')
                body = r.get('body', '')
                md_lines.append(f"### {i}. {title}\n")
                if href:
                    md_lines.append(f"Source: {href}\n")
                if include_snippets and body:
                    md_lines.append(f"> {body}\n")

            md_lines.append("\n## Key findings\n- (Edit this list to highlight the most important conclusions)\n")
            md_lines.append("\n## References\n")
            for r in results:
                title = r.get('title', 'No title')
                href = r.get('href', '')
                md_lines.append(f"- [{title}]({href})")

            generated_md = "\n".join(md_lines)
            st.session_state['generated_md'] = generated_md
            st.success("📝 Draft report generated — edit below as needed.")

if "search_results" in st.session_state:
    st.subheader("📄 Search results")
    for i, r in enumerate(st.session_state['search_results'], start=1):
        with st.expander(f"{i}. {r.get('title', 'No title')}"):
            st.write(r.get('body', ''))
            href = r.get('href', None)
            if href:
                st.markdown(f"🔗 Source: [{href}]({href})")

st.markdown("---")

st.subheader("🖊️ Report editor")
initial_md = st.session_state.get('generated_md', f"# Research report: {topic}\n\n(Use the 'Auto-generate report' button.)")
edited_md = st.text_area("Edit your markdown report below", value=initial_md, height=400)

# Define safe_topic globally once, so it is always available
safe_topic = "_".join(topic.strip().split())[:50] or "report"

col_save, col_download = st.columns([1, 1])
with col_save:
    if st.button("💾 Save report to file"):
        filename = f"report_{safe_topic}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(edited_md)
            st.success(f"✅ Saved report as {filename}")
            st.session_state['last_saved'] = filename
        except Exception as e:
            st.error(f"❌ Failed to save: {e}")

with col_download:
    st.download_button("⬇️ Download report (.md)", data=edited_md, file_name=f"report_{safe_topic}.md", mime="text/markdown")

if 'last_saved' in st.session_state:
    st.info(f"📂 Last saved: {st.session_state['last_saved']}")

st.markdown("---")
st.caption("🌐 Built with Streamlit • DuckDuckGo search (duckduckgo_search) • Optional LLM integration placeholder")

def summarize_with_llm(text_chunks, api_key=None):
    return "".join(text_chunks[:3])