"""
Brief Post Generator for LinkedIn Content Automation
Generates brief/short versions of LinkedIn posts based on a selected idea.
"""

import yaml
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from openai import OpenAI
import importlib.util


class BriefPostGenerator:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        Initialize the BriefPostGenerator.
        
        Args:
            api_key: OpenAI API key. If None, will try to get from environment.
            model: OpenAI model to use (default: gpt-4)
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.base_path = Path(__file__).parent.parent
        self.config_path = self.base_path / "config"
        self.prompts_path = self.base_path / "src" / "prompts"
        
    def _load_content_pillars(self) -> Dict:
        """Load content pillars from YAML file."""
        pillars_file = self.config_path / "content_pillars.yaml"
        with open(pillars_file, 'r') as f:
            return yaml.safe_load(f)
    
    def _get_day_pillar(self) -> Dict[str, str]:
        """
        Get today's content pillar based on the day of the week.
        
        Returns:
            Dict with 'name' and 'description' keys
        """
        pillars = self._load_content_pillars()
        day_name = datetime.now().strftime("%A").lower()
        
        pillar_data = pillars['content_pillars'].get(day_name, {})
        
        # Handle Friday's alternative option
        if day_name == 'friday' and 'alternative' in pillar_data:
            # For now, default to the main option
            return {
                'name': pillar_data['name'],
                'description': pillar_data['description']
            }
        
        return {
            'name': pillar_data.get('name', ''),
            'description': pillar_data.get('description', '')
        }
    
    def _load_prompt_template(self) -> str:
        """Load the brief post generation prompt template."""
        prompt_file = self.prompts_path / "brief_post_generation_prompt.py"
        spec = importlib.util.spec_from_file_location("brief_post_generation_prompt", prompt_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        return module.brief_post_generation_prompt
    
    def generate_brief_posts(self, idea: Dict[str, str], num_versions: int = 5) -> List[str]:
        """
        Generate brief versions of a LinkedIn post based on the selected idea.
        
        Args:
            idea: Dictionary with 'title', 'description', and optionally 'hook' keys
            num_versions: Number of brief versions to generate (default: 5)
            
        Returns:
            List of brief post strings
        """
        # Get today's pillar
        pillar = self._get_day_pillar()
        
        # Load prompt template
        prompt_template = self._load_prompt_template()
        
        # Format the prompt
        prompt = prompt_template.format(
            idea_title=idea.get('title', ''),
            pillar_name=pillar['name'],
            pillar_description=pillar['description']
        )
        
        # Call OpenAI API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a creative content writer helping a freelance ML engineer create engaging LinkedIn content that matches their unique voice."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,  # Higher temperature for more creative variations
        )
        
        # Parse the response
        posts_text = response.choices[0].message.content
        
        # Parse brief posts from the response
        brief_posts = self._parse_brief_posts(posts_text, num_versions)
        
        return brief_posts
    
    def _parse_brief_posts(self, posts_text: str, expected_count: int = 5) -> List[str]:
        """
        Parse brief posts from the AI response text.
        
        Args:
            posts_text: Raw text response from AI
            expected_count: Expected number of posts
            
        Returns:
            List of parsed brief post strings
        """
        posts = []
        
        # Split by numbered items (1., 2., etc.)
        import re
        # Pattern to match numbered items at the start of a line
        pattern = r'^\d+[\.\)]\s*'
        
        # Split the text by numbered sections
        sections = re.split(pattern, posts_text, flags=re.MULTILINE)
        
        # Filter out empty sections and clean them up
        for section in sections:
            section = section.strip()
            if section and len(section) > 20:  # Filter out very short sections
                posts.append(section)
        
        # If parsing didn't work well, try alternative method
        if len(posts) < expected_count:
            # Try splitting by double newlines or clear separators
            parts = posts_text.split('\n\n')
            posts = []
            for part in parts:
                part = part.strip()
                # Remove leading numbers if present
                part = re.sub(r'^\d+[\.\)]\s*', '', part, flags=re.MULTILINE)
                if part and len(part) > 20:
                    posts.append(part)
        
        # Limit to expected count
        return posts[:expected_count]


if __name__ == "__main__":
    # Example usage
    import os
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        exit(1)
    
    generator = BriefPostGenerator(api_key=api_key)
    
    # Example idea
    test_idea = {
        'title': 'The Real Cost of AI Hype',
        'description': 'A post about how AI hype cycles distract from real engineering work',
        'hook': 'Start with a sarcastic observation about the latest AI announcement'
    }
    
    brief_posts = generator.generate_brief_posts(test_idea)
    
    print(f"\nGenerated {len(brief_posts)} brief post versions:\n")
    for i, post in enumerate(brief_posts, 1):
        print(f"{'='*60}")
        print(f"Version {i}:")
        print(f"{'='*60}")
        print(post)
        print()

