"""
LinkedIn Content Automation - Streamlit App
"""

import streamlit as st
import os
from datetime import datetime
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from idea_generator import IdeaGenerator


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


def get_api_key():
    """Get OpenAI API key from environment or Streamlit secrets."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key and hasattr(st, "secrets") and "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
    return api_key


def main():
    st.title("✍️ LinkedIn Content Automation")
    st.markdown("---")
    
    # Get API key
    api_key = get_api_key()
    if not api_key:
        st.error("⚠️ OPENAI_API_KEY not found. Please set it as an environment variable or in Streamlit secrets.")
        st.stop()
    
    # Initialize generator
    generator = IdeaGenerator(api_key=api_key)
    
    # Display today's content pillar
    pillar = generator._get_day_pillar()
    day_name = datetime.now().strftime("%A")
    
    st.header(f"📅 Today is {day_name}")
    st.subheader(f"Content Pillar: {pillar['name']}")
    st.info(pillar['description'])
    
    st.markdown("---")
    
    # Generate ideas button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎯 Generate Ideas", use_container_width=True, type="primary"):
            with st.spinner("Generating content ideas..."):
                try:
                    ideas = generator.generate_ideas(num_ideas=7)
                    st.session_state.ideas = ideas
                    st.session_state.selected_idea = None
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
                    # Placeholder button - does nothing for now
                    if st.button("This one", key=f"select_{i}", use_container_width=True):
                        st.session_state.selected_idea = idea
                        st.info(f"Selected: {idea.get('title', 'Untitled')} (functionality coming soon!)")
                
                st.markdown("---")


if __name__ == "__main__":
    main()

