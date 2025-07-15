"""
Reddit User Persona Analyzer - Streamlit Web Interface
"""
import streamlit as st
import os
import textwrap
from reddit_persona_analyzer import RedditPersonaAnalyzer

# --- Page Configuration ---
st.set_page_config(
    page_title="Reddit Persona Analyzer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Functions ---

def load_css(file_name):
    """Load an external CSS file."""
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def run_analysis(_analyzer, profile_url, post_limit, comment_limit):
    """Runs the full analysis pipeline."""
    username = _analyzer.extract_username_from_url(profile_url)
    user_data = _analyzer.get_user_activity(username, post_limit, comment_limit)
    persona_data = _analyzer.analyze_user_persona(user_data)
    
    if "error" in persona_data:
        return None, persona_data, None
    
    card_path = _analyzer.generate_persona_card(persona_data, user_data)
    
    return card_path, persona_data, user_data

def card_page():
    """Renders the main persona card page."""
    st.title("🤖 Reddit Persona Analyzer")
    st.markdown("Generate a visual persona summary from a Reddit user's profile.")

    try:
        analyzer = RedditPersonaAnalyzer()
    except Exception as e:
        st.error(f"Initialization Failed: Check API keys in config.env. Details: {e}")
        return

    with st.sidebar:
        st.header("⚙️ Analysis Controls")
        post_limit = st.slider("Posts", 10, 100, 30)
        comment_limit = st.slider("Comments", 20, 200, 50)

    profile_url = st.text_input("Enter Reddit Profile URL", placeholder="e.g., https://www.reddit.com/user/spez")

    if st.button("🚀 Generate Persona", type="primary"):
        if profile_url:
            with st.spinner("Analyzing user activity and crafting persona..."):
                card_path, persona_data, user_data = run_analysis(analyzer, profile_url, post_limit, comment_limit)
                st.session_state.card_path = card_path
                st.session_state.persona_data = persona_data
                st.session_state.user_data = user_data
                st.session_state.error = persona_data.get('error')
        else:
            st.warning("Please enter a URL.")

    if st.session_state.get('error'):
        st.error(f"Analysis Error: {st.session_state.error}")

    if st.session_state.get('card_path'):
        card_path = st.session_state.card_path
        if os.path.exists(card_path):
            st.header("Persona Card Summary")
            st.image(card_path, use_column_width=True)
            with open(card_path, "rb") as file:
                st.download_button("📥 Download Card (JPG)", file, os.path.basename(card_path), "image/jpeg")

def detailed_analysis_page():
    """Renders the detailed analysis page with citations."""
    st.title("📄 Detailed Analysis")
    
    if not st.session_state.get('persona_data') or st.session_state.get('error'):
        st.info("Run an analysis on the 'Persona Card' page to view details here.")
        return

    persona_data = st.session_state.persona_data
    
    # --- Helper function to render entries ---
    def render_entry(item_dict):
        if not isinstance(item_dict, dict):
            st.markdown(f"- {item_dict}")
            return

        trait = item_dict.get('trait') or item_dict.get('goal') or item_dict.get('point') or item_dict.get('interest') or 'Summary'
        value = item_dict.get('value') or item_dict.get('weight')
        citation = item_dict.get('citation', '#')
        confidence = item_dict.get('confidence')

        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            st.markdown(f"**{trait.title()}**")
        with col2:
            st.markdown(str(value) if value else 'N/A')
        with col3:
            if confidence:
                st.markdown(f"_{confidence}_ | [Source]({citation})")
            else:
                st.markdown(f"[Source]({citation})")

    # --- Iterate and display persona data ---
    for section_title, data in persona_data.items():
        st.subheader(section_title.replace("_", " ").title())
        
        if isinstance(data, list):
            for item in data:
                render_entry(item)
        elif isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list):
                    st.markdown(f"**{key.title()}**")
                    for item in value:
                        render_entry(item)
                elif isinstance(value, dict):
                     render_entry(value) # For single entries like 'oneLiner'
        
        st.markdown("---")


def activity_page():
    """Renders the recent activity page."""
    st.title("📊 Recent Activity")

    if not st.session_state.get('user_data') or st.session_state.get('error'):
        st.info("Run an analysis on the 'Persona Card' page to view recent activity.")
        return
        
    user_data = st.session_state.user_data
    
    st.subheader("Recent Posts")
    for post in user_data.get('posts', [])[:5]:
        with st.container():
            st.markdown(f"**{post['title']}**")
            st.markdown(f"_{textwrap.shorten(post.get('selftext', ''), width=200, placeholder='...')} [Link]({post['permalink']})_")
            st.markdown("---")

    st.subheader("Recent Comments")
    for comment in user_data.get('comments', [])[:5]:
        with st.container():
            st.markdown(f"_{textwrap.shorten(comment['body'], width=250, placeholder='...')} [Link]({comment['permalink']})_")
            st.markdown("---")

# --- Main App Router ---
def main():
    load_css("style.css")
    
    PAGES = {
        "Persona Card": card_page,
        "Detailed Analysis": detailed_analysis_page,
        "Recent Activity": activity_page
    }
    
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", list(PAGES.keys()))
    
    page = PAGES[selection]
    page()

if __name__ == "__main__":
    main()
