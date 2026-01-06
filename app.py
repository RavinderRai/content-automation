"""
LinkedIn Content Automation - Streamlit App
"""

import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv

from src.idea_generator import IdeaGenerator
from src.brief_post_generator import BriefPostGenerator

# Load environment variables from .env file
load_dotenv()


# Page config
st.set_page_config(
    page_title="LinkedIn Content Automation",
    page_icon="✍️",
    layout="wide"
)

# Initialize session state
if 'ideas' not in st.session_state:
    st.session_state.ideas = []
if 'selected_idea' not in st.session_state:
    st.session_state.selected_idea = None
if 'selected_day' not in st.session_state:
    # Default to today
    st.session_state.selected_day = datetime.now().strftime("%A")
if 'context' not in st.session_state:
    st.session_state.context = ""
if 'brief_posts' not in st.session_state:
    st.session_state.brief_posts = []


def get_api_key():
    """Get OpenAI API key from environment variables."""
    return os.getenv("OPENAI_API_KEY")


def main():
    st.title("✍️ LinkedIn Content Automation")
    st.markdown("---")
    
    # Get API key
    api_key = get_api_key()
    if not api_key:
        st.error("⚠️ OPENAI_API_KEY not found. Please set it in a .env file or as an environment variable.")
        st.stop()
    
    # Initialize generators
    idea_generator = IdeaGenerator(api_key=api_key)
    brief_post_generator = BriefPostGenerator(api_key=api_key)
    
    # Day selector
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    selected_day = st.selectbox(
        "📅 Select Day of Week",
        days,
        index=days.index(st.session_state.selected_day) if st.session_state.selected_day in days else 0
    )
    st.session_state.selected_day = selected_day
    
    # Display content pillar for selected day
    pillar = idea_generator._get_day_pillar(selected_day.lower())
    
    st.subheader(f"Content Pillar: {pillar['name']}")
    st.info(pillar['description'])
    
    st.markdown("---")
    
    # Context input
    st.subheader("📝 Additional Context (Optional)")
    st.caption("Add any relevant context about recent work, projects, or experiences that might inform the content ideas.")
    context_input = st.text_area(
        "Context",
        value=st.session_state.context,
        height=100,
        placeholder="e.g., Recently built an AI tool for X, working on Y project, just learned about Z...",
        label_visibility="collapsed"
    )
    st.session_state.context = context_input
    
    st.markdown("---")
    
    # Generate ideas button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎯 Generate Ideas", use_container_width=True, type="primary"):
            with st.spinner("Generating content ideas..."):
                try:
                    context = st.session_state.context.strip() if st.session_state.context else None
                    ideas = idea_generator.generate_ideas(
                        num_ideas=7, 
                        day_name=selected_day.lower(),
                        context=context
                    )
                    st.session_state.ideas = ideas
                    st.session_state.selected_idea = None
                    st.session_state.brief_posts = []  # Clear previous brief posts
                    st.success(f"✅ Generated {len(ideas)} ideas!")
                except Exception as e:
                    st.error(f"Error generating ideas: {str(e)}")
    
    st.markdown("---")
    
    # Display ideas if they exist
    if st.session_state.ideas:
        st.header("💡 Content Ideas")
        
        for i, idea in enumerate(st.session_state.ideas, 1):
            with st.container():
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    st.subheader(f"{i}. {idea.get('title', 'Untitled')}")
                    
                    if idea.get('description'):
                        st.markdown(f"**Description:** {idea['description']}")
                    
                    if idea.get('hook'):
                        st.markdown(f"**Hook angle:** {idea['hook']}")
                
                with col2:
                    if st.button("This one", key=f"select_{i}", use_container_width=True):
                        st.session_state.selected_idea = idea
                        st.session_state.brief_posts = []  # Clear previous brief posts
                        # Generate brief posts
                        with st.spinner("Generating brief post versions..."):
                            try:
                                context = st.session_state.context.strip() if st.session_state.context else None
                                brief_posts = brief_post_generator.generate_brief_posts(
                                    idea=idea,
                                    num_versions=5,
                                    day_name=selected_day.lower(),
                                    context=context
                                )
                                st.session_state.brief_posts = brief_posts
                                st.success(f"✅ Generated {len(brief_posts)} brief post versions!")
                            except Exception as e:
                                st.error(f"Error generating brief posts: {str(e)}")
                
                st.markdown("---")
    
    # Display brief posts if they exist
    if st.session_state.brief_posts and st.session_state.selected_idea:
        st.header("📝 Brief Post Versions")
        st.info(f"Selected idea: **{st.session_state.selected_idea.get('title', 'Untitled')}**")
        
        for i, post in enumerate(st.session_state.brief_posts, 1):
            with st.container():
                st.subheader(f"Version {i}")
                st.text_area(
                    f"Brief Post {i}",
                    value=post,
                    height=150,
                    key=f"brief_post_{i}",
                    label_visibility="collapsed"
                )
                st.markdown("---")


if __name__ == "__main__":
    main()

