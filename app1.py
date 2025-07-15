#!/usr/bin/env python3
"""
Reddit User Persona Analyzer - Streamlit Web Interface
A user-friendly web interface for analyzing Reddit user profiles and generating personas.
"""

import streamlit as st
import os
import sys
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from reddit_persona_analyzer import RedditPersonaAnalyzer

# Page configuration
st.set_page_config(
    page_title="Reddit User Persona Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Consolidated CSS styles


def load_css():
    """Load all CSS styles for the application."""
    st.markdown("""
    <style>
    /* Base styles */
    html, body, [data-testid="stAppViewContainer"] {
        background: #ffffff !important;
        color: #111 !important;
        font-family: "Inter", "Helvetica", sans-serif;
        font-size: 0.9rem;
    }

    /* Headers */
    .main-header {
        font-size: 2rem;
        font-weight: 600;
        text-align: center;
        margin-bottom: 1.5rem;
        color: #111;
    }

    .sub-header {
        font-size: 1rem;
        font-weight: 500;
        color: #111;
        margin-bottom: 0.75rem;
    }

    /* Cards and sections */
    .metric-card, .persona-section {
        background: #f7f7f7;
        padding: 1rem 1.25rem;
        border-left: 3px solid #ccc;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #f0f0f0 !important;
        color: #111 !important;
        border-right: 1px solid #ddd;
    }

    /* Buttons */
    .stButton > button, .stDownloadButton > button {
        background: #f0f0f0;
        color: #111;
        border: 1px solid #999;
        border-radius: 0.3rem;
        font-size: 0.9rem;
    }

    .stButton > button:hover, .stDownloadButton > button:hover {
        background: #e0e0e0;
    }

    /* Input fields */
    .stTextInput > div > input {
        border: 1px solid #999;
        border-radius: 0.3rem;
        background: #fff;
        color: #111;
        padding: 0.4rem 0.8rem;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab"] {
        font-size: 0.9rem;
        color: #111;
        background: #f0f0f0;
    }

    /* Dividers */
    hr {
        border: none;
        border-top: 1px solid #ddd;
        margin: 1.5rem 0 1rem 0;
    }

    /* Dashboard styles */
    .dashboard-container {
        background: #181A1B;
        padding: 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
    }

    .section-card {
        background: #232526;
        padding: 1.5rem;
        border-radius: 0.75rem;
        margin-bottom: 1.5rem;
        border: 1px solid #4CAF50;
    }

    .section-title {
        color: #4CAF50;
        font-size: 1.5rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #4CAF50;
    }

    .trait-card {
        background: #181A1B;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border: 1px solid #4CAF50;
    }

    .trait-label {
        color: #4CAF50;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }

    .trait-value {
        color: #F3F4F6;
        font-size: 1rem;
        line-height: 1.5;
    }

    .trait-citation {
        color: #888;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }

    .confidence-badge {
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.85rem;
    }

    .high-confidence { background: #4CAF50; }
    .medium-confidence { background: #76d7c4; }
    .low-confidence { background: #d4efdf; }

    .trait-link {
        color: #4CAF50;
        text-decoration: none;
    }

    .trait-link:hover {
        text-decoration: underline;
    }

    /* Activity styles */
    .activity-item {
        background: #232526;
        padding: 1.25rem;
        border-radius: 0.75rem;
        margin-bottom: 1.25rem;
        border-left: 3px solid #4CAF50;
    }

    .activity-header {
        color: #4CAF50;
        margin-bottom: 0.75rem;
        font-size: 1.25rem;
    }

    .activity-content {
        color: #F3F4F6;
        line-height: 1.6;
        font-size: 1rem;
    }

    .activity-meta {
        color: #888;
        font-size: 0.9rem;
        margin-top: 0.75rem;
    }

    .activity-score {
        color: #4CAF50;
        font-weight: bold;
    }

    .section-header {
        color: #4CAF50;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }

    /* Dark mode overrides */
    @media (prefers-color-scheme: dark) {
        html, body, [data-testid="stAppViewContainer"] {
            background: #181A1B !important;
            color: #F3F4F6 !important;
        }

        [data-testid="stAppViewContainer"] * {
            color: #F3F4F6 !important;
        }

        .metric-card, .persona-section {
            background: #232526;
            border-left: 3px solid #444;
        }

        section[data-testid="stSidebar"] {
            background: #232526 !important;
            color: #F3F4F6 !important;
            border-right: 1px solid #333;
        }

        .stButton > button, .stDownloadButton > button {
            background: #232526;
            color: #F3F4F6;
            border: 1px solid #555;
        }

        .stButton > button:hover, .stDownloadButton > button:hover {
            background: #333;
        }

        .stTextInput > div > input {
            background: #181A1B;
            color: #F3F4F6;
            border: 1px solid #555;
        }

        .stTabs [data-baseweb="tab"] {
            background: #232526;
            color: #F3F4F6;
        }

        hr {
            border-top: 1px solid #333;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def human_readable_account_age(created_utc):
    """Convert UTC timestamp to human-readable account age."""
    now = datetime.utcnow()
    created = datetime.utcfromtimestamp(created_utc)
    delta = now - created
    years = delta.days // 365
    months = (delta.days % 365) // 30
    days = (delta.days % 365) % 30

    parts = []
    if years > 0:
        parts.append(f"{years} year{'s' if years != 1 else ''}")
    if months > 0:
        parts.append(f"{months} month{'s' if months != 1 else ''}")
    if days > 0 or not parts:
        parts.append(f"{days} day{'s' if days != 1 else ''}")

    return ' '.join(parts)


def setup_sidebar():
    """Setup the sidebar with API status and settings."""
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.markdown("<hr>", unsafe_allow_html=True)

        # API Status
        st.subheader("API Status")
        try:
            analyzer = RedditPersonaAnalyzer()
            st.success("✅ APIs Connected")
        except Exception as e:
            st.error(f"❌ API Error: {str(e)}")
            st.info("Please check your config.env file")
            return None, None, None

        st.markdown("<hr>", unsafe_allow_html=True)

        # Analysis Settings
        st.subheader("Analysis Settings")
        post_limit = st.slider("Posts to analyze", 10, 100, 30)
        comment_limit = st.slider("Comments to analyze", 20, 200, 50)
        st.markdown("<hr>", unsafe_allow_html=True)

        return analyzer, post_limit, comment_limit


def display_quick_stats():
    """Display quick statistics in the sidebar."""
    if 'analysis_results' not in st.session_state:
        st.info("Run an analysis to see statistics here")
        return

    results = st.session_state.analysis_results
    user_data = results.get('user_data', {})

    # Display basic stats
    st.metric("Total Posts", len(user_data.get('posts', [])))
    st.metric("Total Comments", len(user_data.get('comments', [])))

    if 'profile' in user_data:
        profile = user_data['profile']
        st.metric(
            "Account Age",
            human_readable_account_age(
                profile.get(
                    'created_utc',
                    0)))
        st.metric("Total Karma", f"{profile.get('total_karma', 0):,}")


def analyze_user(profile_url: str, post_limit: int, comment_limit: int):
    """Analyze a Reddit user and store results in session state."""
    try:
        # Initialize analyzer
        analyzer = RedditPersonaAnalyzer()

        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Step 1: Extract username
        status_text.text("🔍 Extracting username...")
        progress_bar.progress(20)
        username = analyzer.extract_username_from_url(profile_url)

        # Step 2: Fetch user data
        status_text.text("📊 Fetching user activity...")
        progress_bar.progress(40)
        user_data = analyzer.get_user_activity(
            username, post_limit, comment_limit)

        # Step 3: Generate persona
        status_text.text("🧠 Analyzing persona...")
        progress_bar.progress(70)
        persona_data = analyzer.analyze_user_persona(user_data)

        # Step 4: Generate report
        status_text.text("📝 Generating report...")
        progress_bar.progress(90)
        report = analyzer.generate_persona_report(persona_data, username)

        # Step 5: Save report
        md_file = analyzer.save_persona_report(report, username)

        # Step 6: Generate persona card
        status_text.text("🎨 Creating persona card...")
        progress_bar.progress(95)
        card_file = analyzer.generate_persona_card(persona_data, username)

        # Complete
        progress_bar.progress(100)
        status_text.text("✅ Analysis complete!")

        # Store results in session state
        st.session_state.analysis_results = {
            'username': username,
            'user_data': user_data,
            'persona_data': persona_data,
            'report': report,
            'markdown_file': md_file,
            'card_file': card_file
        }

        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()

    except Exception as e:
        st.error(f"❌ Analysis failed: {str(e)}")
        st.info("Please check the URL and try again")


def display_results():
    """Display the analysis results in tabs."""
    if 'analysis_results' not in st.session_state:
        return

    results = st.session_state.analysis_results
    username = results['username']

    if 'error' in results:
        st.error(results['error'])
        return

    st.success(f"✅ Analysis completed for u/{username}")

    # Download button
    with open(results['markdown_file'], 'r') as f:
        st.download_button(
            label="📥 Download Full Report",
            data=f.read(),
            file_name=f"persona_{username}.txt",
            mime="text/plain",
            use_container_width=True
        )

    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(
        ["📊 Overview", "📝 Full Report", "📈 Activity History"])

    with tab1:
        display_overview_tab(results)

    with tab2:
        display_full_report_tab(results)

    with tab3:
        display_activity_tab(results)


def display_overview_tab(results):
    """Display overview information."""
    user_data = results['user_data']
    persona_data = results['persona_data']

    # Create columns for overview
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("📊 Account Statistics")

        if 'profile' in user_data:
            profile = user_data['profile']
            st.metric(
                "Account Age",
                human_readable_account_age(
                    profile.get(
                        'created_utc',
                        0)))
            st.metric("Total Karma", f"{profile.get('total_karma', 0):,}")
            st.metric("Posts Analyzed", len(user_data.get('posts', [])))
            st.metric("Comments Analyzed", len(user_data.get('comments', [])))

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("🏆 Top Subreddits")

        # Calculate top subreddits
        subreddits = {}
        for post in user_data.get('posts', []):
            subreddit = post.get('subreddit', 'Unknown')
            subreddits[subreddit] = subreddits.get(subreddit, 0) + 1

        for comment in user_data.get('comments', []):
            subreddit = comment.get('subreddit', 'Unknown')
            subreddits[subreddit] = subreddits.get(subreddit, 0) + 1

        top_subreddits = sorted(
            subreddits.items(),
            key=lambda x: x[1],
            reverse=True)[
            :5]

        for subreddit, count in top_subreddits:
            st.write(f"r/{subreddit}: {count} activities")

        st.markdown('</div>', unsafe_allow_html=True)


def display_full_report_tab(results):
    """Display the full report with enhanced visual structure and organization."""
    persona_data = results['persona_data']

    st.markdown("""
    <style>
    /* Report Container */
    .report-container {
        background: #181A1B;
        padding: 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
    }

    /* Section Styles */
    .report-section {
        background: #232526;
        padding: 1.5rem;
        border-radius: 0.75rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255,255,255,0.1);
    }

    .section-header {
        color: #fff;
        font-size: 1.75rem;
        margin-bottom: 1.25rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid rgba(255,255,255,0.1);
        font-weight: 600;
    }

    .section-subheader {
        color: #fff;
        font-size: 1.25rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }

    /* Trait Cards */
    .trait-card {
        background: #181A1B;
        padding: 1.25rem;
        border-radius: 0.75rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        transition: transform 0.2s;
    }

    .trait-card:hover {
        transform: translateY(-2px);
    }

    .trait-label {
        color: #fff;
        font-weight: bold;
        font-size: 1.1rem;
        margin-bottom: 0.75rem;
    }

    .trait-value {
        color: #fff;
        font-size: 1rem;
        line-height: 1.6;
        margin-bottom: 0.75rem;
    }

    .trait-citation {
        color: #888;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }

    /* Confidence Badges */
    .confidence-badge {
        display: inline-block;
        padding: 0.35rem 0.75rem;
        border-radius: 0.35rem;
        font-size: 0.9rem;
        font-weight: 500;
        margin-left: 0.5rem;
    }

    .high-confidence { 
        background: rgba(255,255,255,0.1); 
        color: #fff;
    }

    .medium-confidence { 
        background: rgba(255,255,255,0.05); 
        color: #fff;
    }

    .low-confidence { 
        background: rgba(255,255,255,0.03); 
        color: #fff;
    }

    /* Links */
    .trait-link {
        color: #fff;
        text-decoration: none;
        font-weight: 500;
    }

    .trait-link:hover {
        text-decoration: underline;
        color: #fff;
    }

    /* Download Section */
    .download-section {
        text-align: right;
        margin-bottom: 1.5rem;
        padding: 1rem;
        background: #232526;
        border-radius: 0.75rem;
    }

    .download-button {
        background: rgba(255,255,255,0.1);
        color: #fff;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 0.4rem;
        cursor: pointer;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.2s;
    }

    .download-button:hover {
        background: rgba(255,255,255,0.2);
        transform: translateY(-1px);
    }

    /* Stats Grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
        margin-bottom: 1.5rem;
    }

    .stat-card {
        background: #232526;
        padding: 1.5rem;
        border-radius: 0.75rem;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
    }

    .stat-label {
        color: #fff;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }

    .stat-value {
        color: #fff;
        font-size: 2rem;
        font-weight: bold;
        line-height: 1;
    }

    /* Charts */
    .chart-container {
        background: #232526;
        padding: 1.5rem;
        border-radius: 0.75rem;
        margin-bottom: 1.5rem;
    }

    .chart-title {
        color: #fff;
        font-size: 1.25rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="report-container">', unsafe_allow_html=True)

    # Display download button at the top
    st.markdown('<div class="download-section">', unsafe_allow_html=True)
    with open(results['markdown_file'], 'r') as f:
        st.download_button(
            label="💾 Download Full Report",
            data=f.read(),
            file_name=f"persona_{results['username']}.txt",
            mime="text/plain",
            key="download_button",
            use_container_width=False,
            help="Download a text version of this full report"
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # Display raw analysis text
    if 'raw_analysis' in persona_data:
        st.markdown('<div class="report-section">', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-header">📝 Raw Analysis</div>',
            unsafe_allow_html=True)

        # Split analysis into sections
        analysis_text = persona_data['raw_analysis']
        sections = analysis_text.split('\n\n')

        for section in sections:
            if section.strip():
                st.markdown('<div class="trait-card">', unsafe_allow_html=True)
                st.markdown(
                    '<div class="trait-value">',
                    unsafe_allow_html=True)
                st.write(section)
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # Display traits section
    if 'traits' in persona_data:
        st.markdown('<div class="report-section">', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-header">📊 Key Traits</div>',
            unsafe_allow_html=True)

        traits = persona_data['traits']

        # Create a grid layout for trait categories
        cols = st.columns(2)

        # Split categories between columns
        categories = [
            'demographics',
            'psychology',
            'online behavior',
            'expertise',
            'social dynamics']
        mid = len(categories) // 2
        left_categories = categories[:mid]
        right_categories = categories[mid:]

        # Display left column
        with cols[0]:
            for trait_type in left_categories:
                if trait_type in traits:
                    st.markdown(
                        f'<div class="section-subheader">{
                            trait_type.replace(
                                "_",
                                " ").title()}</div>',
                        unsafe_allow_html=True)

                    # Sort traits by confidence level
                    sorted_traits = sorted(
                        traits[trait_type],
                        key=lambda x: x.get('confidence', 'Low'),
                        reverse=True
                    )

                    for trait in sorted_traits:
                        st.markdown(
                            '<div class="trait-card">',
                            unsafe_allow_html=True)
                        st.markdown(
                            f'<div class="trait-label">{
                                trait.get(
                                    "trait",
                                    "Unknown")}</div>',
                            unsafe_allow_html=True)

                        confidence = trait.get('confidence', 'Unknown')
                        confidence_class = {
                            'High': 'high-confidence',
                            'Medium': 'medium-confidence',
                            'Low': 'low-confidence'
                        }.get(confidence, 'low-confidence')

                        value_text = f"{trait.get('value', 'Unknown')}"
                        if confidence != 'Unknown':
                            value_text += f" <span class='confidence-badge {confidence_class}'>[{confidence}]</span>"

                        st.markdown(
                            f'<div class="trait-value">{value_text}</div>',
                            unsafe_allow_html=True)

                        citation = trait.get(
                            'citation', 'No citation provided')
                        if citation.startswith('http'):
                            st.markdown(
                                f'<div class="trait-citation"><a href="{citation}" class="trait-link" target="_blank">[Source]</a></div>',
                                unsafe_allow_html=True)
                        else:
                            st.markdown(
                                f'<div class="trait-citation">{citation}</div>',
                                unsafe_allow_html=True)

                        st.markdown('</div>', unsafe_allow_html=True)

        # Display right column
        with cols[1]:
            for trait_type in right_categories:
                if trait_type in traits:
                    st.markdown(
                        f'<div class="section-subheader">{
                            trait_type.replace(
                                "_",
                                " ").title()}</div>',
                        unsafe_allow_html=True)

                    # Sort traits by confidence level
                    sorted_traits = sorted(
                        traits[trait_type],
                        key=lambda x: x.get('confidence', 'Low'),
                        reverse=True
                    )

                    for trait in sorted_traits:
                        st.markdown(
                            '<div class="trait-card">',
                            unsafe_allow_html=True)
                        st.markdown(
                            f'<div class="trait-label">{
                                trait.get(
                                    "trait",
                                    "Unknown")}</div>',
                            unsafe_allow_html=True)

                        confidence = trait.get('confidence', 'Unknown')
                        confidence_class = {
                            'High': 'high-confidence',
                            'Medium': 'medium-confidence',
                            'Low': 'low-confidence'
                        }.get(confidence, 'low-confidence')

                        value_text = f"{trait.get('value', 'Unknown')}"
                        if confidence != 'Unknown':
                            value_text += f" <span class='confidence-badge {confidence_class}'>[{confidence}]</span>"

                        st.markdown(
                            f'<div class="trait-value">{value_text}</div>',
                            unsafe_allow_html=True)

                        citation = trait.get(
                            'citation', 'No citation provided')
                        if citation.startswith('http'):
                            st.markdown(
                                f'<div class="trait-citation"><a href="{citation}" class="trait-link" target="_blank">[Source]</a></div>',
                                unsafe_allow_html=True)
                        else:
                            st.markdown(
                                f'<div class="trait-citation">{citation}</div>',
                                unsafe_allow_html=True)

                        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # Display user statistics
    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-header">📊 User Statistics</div>',
        unsafe_allow_html=True)

    # Create stats grid
    st.markdown('<div class="stats-grid">', unsafe_allow_html=True)

    # Posts and Comments
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(
            '<div class="stat-label">Total Posts</div>',
            unsafe_allow_html=True)
        st.markdown(
            f'<div class="stat-value">{
                results.get(
                    "post_count",
                    0)}</div>',
            unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(
            '<div class="stat-label">Total Comments</div>',
            unsafe_allow_html=True)
        st.markdown(
            f'<div class="stat-value">{
                results.get(
                    "comment_count",
                    0)}</div>',
            unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Display activity distribution chart
    if 'activity_distribution' in results:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown(
            '<div class="chart-title">Activity Distribution</div>',
            unsafe_allow_html=True)

        # Create pie chart
        labels = list(results['activity_distribution'].keys())
        values = list(results['activity_distribution'].values())

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.3,
            textinfo='label+percent',
            textfont=dict(color='#F3F4F6'),
            marker=dict(colors=px.colors.sequential.Blugrn)
        )])

        fig.update_layout(
            paper_bgcolor='#232526',
            plot_bgcolor='#232526',
            font_color='#F3F4F6',
            showlegend=True,
            legend=dict(
                font=dict(color='#F3F4F6'),
                bgcolor='#232526'
            )
        )

        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def display_activity_tab(results):
    """Display activity history."""
    user_data = results['user_data']

    posts = user_data.get('posts', [])[:5]
    comments = user_data.get('comments', [])[:5]

    if not posts and not comments:
        st.info("No activity data available")
        return

    # Display recent posts
    if posts:
        st.markdown(
            '<h3 class="section-header">📝 Recent Posts</h3>',
            unsafe_allow_html=True)
        for post in posts:
            display_post_item(post)

    # Display recent comments
    if comments:
        st.markdown(
            '<h3 class="section-header">💬 Recent Comments</h3>',
            unsafe_allow_html=True)
        for comment in comments:
            display_comment_item(comment)


def display_post_item(post):
    """Display a single post item."""
    post_url = f"https://www.reddit.com{post['permalink']}"

    st.markdown('<div class="activity-item">', unsafe_allow_html=True)
    st.markdown('<div class="activity-header">', unsafe_allow_html=True)
    st.markdown(
        f'<a href="{post_url}" target="_blank">{post["title"][:100]}...</a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="activity-meta">', unsafe_allow_html=True)
    st.markdown(
        f'<span class="activity-score">{
            post["score"]} points</span> • r/{
            post["subreddit"]}',
        unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if post.get('selftext'):
        st.markdown('<div class="activity-content">', unsafe_allow_html=True)
        st.write(f"{post['selftext'][:200]}...")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def display_comment_item(comment):
    """Display a single comment item."""
    comment_url = f"https://www.reddit.com{comment['permalink']}"

    st.markdown('<div class="activity-item">', unsafe_allow_html=True)
    st.markdown('<div class="activity-header">', unsafe_allow_html=True)
    st.markdown(
        f'<a href="{comment_url}" target="_blank">Comment in r/{
            comment["subreddit"]}</a>',
        unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="activity-meta">', unsafe_allow_html=True)
    st.markdown(
        f'<span class="activity-score">{
            comment["score"]} points</span>',
        unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="activity-content">', unsafe_allow_html=True)
    st.write(f"{comment['body'][:200]}...")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def main():
    """Main Streamlit application."""
    # Load CSS styles
    load_css()

    # Header
    st.markdown(
        '<h1 class="main-header">🔍 Reddit User Persona Analyzer</h1>',
        unsafe_allow_html=True)
    st.markdown("---")

    # Setup sidebar
    analyzer, post_limit, comment_limit = setup_sidebar()
    if analyzer is None:
        return

    # Main content
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<div class="persona-section">', unsafe_allow_html=True)
        st.markdown(
            '<h2 class="sub-header">Enter Reddit Profile URL</h2>',
            unsafe_allow_html=True)

        # URL input
        profile_url = st.text_input(
            "Reddit Profile URL",
            placeholder="https://www.reddit.com/user/username/",
            help="Enter a Reddit user profile URL to analyze"
        )

        # Example URLs
        with st.expander("💡 Example URLs"):
            st.code("""
https://www.reddit.com/user/kojied/
https://www.reddit.com/user/Hungry-Move-6603/
            """)

        # Analysis button
        if st.button(
            "🚀 Analyze User",
            type="primary",
                use_container_width=True):
            if not profile_url:
                st.error("Please enter a Reddit profile URL")
            else:
                analyze_user(profile_url, post_limit, comment_limit)

        st.markdown('</div>', unsafe_allow_html=True)

        # Display results if available
        if 'analysis_results' in st.session_state:
            display_results()

    with col2:
        st.markdown('<div class="persona-section">', unsafe_allow_html=True)
        st.markdown(
            '<h2 class="sub-header">📈 Quick Stats</h2>',
            unsafe_allow_html=True)
        display_quick_stats()
        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
