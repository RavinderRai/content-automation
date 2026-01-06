"""
Idea Generator for LinkedIn Content Automation
Generates content ideas based on the day's content pillar and voice profile.
"""

import yaml
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from openai import OpenAI
import importlib.util


class IdeaGenerator:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        Initialize the IdeaGenerator.
        
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
    
    def _load_voice_profile(self) -> Dict:
        """Load voice profile from YAML file."""
        profile_file = self.config_path / "voice_profile.yaml"
        with open(profile_file, 'r') as f:
            return yaml.safe_load(f)
    
    def _load_prompt_template(self) -> str:
        """Load the idea generation prompt template."""
        prompt_file = self.prompts_path / "idea_generation_prompt.py"
        spec = importlib.util.spec_from_file_location("idea_generation_prompt", prompt_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        return module.idea_generation_prompt
    
    def _get_day_pillar(self, day_name: Optional[str] = None) -> Dict[str, str]:
        """
        Get content pillar for a specific day of the week.
        
        Args:
            day_name: Day of the week (e.g., 'monday', 'tuesday'). 
                     If None, uses today's date.
        
        Returns:
            Dict with 'name' and 'description' keys
        """
        pillars = self._load_content_pillars()
        
        if day_name is None:
            day_name = datetime.now().strftime("%A").lower()
        else:
            # Normalize day name to lowercase
            day_name = day_name.lower()
        
        pillar_data = pillars['content_pillars'].get(day_name, {})
        
        # Handle Friday's alternative option
        if day_name == 'friday' and 'alternative' in pillar_data:
            # For now, default to the main option
            # Could be made interactive later
            return {
                'name': pillar_data['name'],
                'description': pillar_data['description']
            }
        
        return {
            'name': pillar_data.get('name', ''),
            'description': pillar_data.get('description', '')
        }
    
    def generate_ideas(self, num_ideas: int = 7, day_name: Optional[str] = None, context: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Generate content ideas for a specific day's pillar.
        
        Args:
            num_ideas: Number of ideas to generate (default: 7)
            day_name: Day of the week (e.g., 'monday', 'tuesday'). 
                     If None, uses today's date.
            context: Optional additional context relevant to today's content pillar
            
        Returns:
            List of idea dictionaries with 'title', 'description', and 'hook' keys
        """
        # Get pillar for the specified day
        pillar = self._get_day_pillar(day_name)
        
        # Load prompt template
        prompt_template = self._load_prompt_template()
        
        # Format additional context section
        if context and context.strip():
            additional_context = f"ADDITIONAL CONTEXT:\n{context.strip()}\n"
        else:
            additional_context = ""
        
        # Format the prompt
        prompt = prompt_template.format(
            pillar_name=pillar['name'],
            pillar_description=pillar['description'],
            additional_context=additional_context
        )
        
        # Call OpenAI API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a creative content strategist helping a freelance ML engineer create engaging LinkedIn content."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,  # Higher temperature for more creative ideas
        )
        
        # Parse the response
        ideas_text = response.choices[0].message.content
        
        # Parse ideas from the response
        ideas = self._parse_ideas(ideas_text)
        
        return ideas
    
    def _parse_ideas(self, ideas_text: str) -> List[Dict[str, str]]:
        """
        Parse ideas from the AI response text.
        
        Args:
            ideas_text: Raw text response from AI
            
        Returns:
            List of parsed idea dictionaries
        """
        ideas = []
        lines = ideas_text.strip().split('\n')
        
        current_idea = {}
        current_section = None
        current_text = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this is a new numbered idea
            if line[0].isdigit() and ('.' in line[:3] or ')' in line[:3]):
                # Save previous idea if exists
                if current_idea:
                    if current_section == 'description':
                        current_idea['description'] = ' '.join(current_text)
                    elif current_section == 'hook':
                        current_idea['hook'] = ' '.join(current_text)
                    ideas.append(current_idea)
                
                # Start new idea
                current_idea = {}
                current_text = []
                # Extract title (everything after the number)
                title = line.split('.', 1)[-1].split(')', 1)[-1].strip()
                if title:
                    current_idea['title'] = title
                current_section = 'title'
            
            # Check for section markers
            elif 'hook' in line.lower() or 'angle' in line.lower():
                if current_idea and current_text:
                    current_idea['description'] = ' '.join(current_text)
                current_text = []
                current_section = 'hook'
            
            elif current_idea:
                # Accumulate text for current section
                current_text.append(line)
                if current_section == 'title' and 'title' not in current_idea:
                    current_idea['title'] = line
                    current_section = 'description'
        
        # Save last idea
        if current_idea:
            if current_text:
                if current_section == 'hook':
                    current_idea['hook'] = ' '.join(current_text)
                elif 'description' not in current_idea:
                    current_idea['description'] = ' '.join(current_text)
            ideas.append(current_idea)
        
        # Fallback: if parsing failed, return simple structure
        if not ideas:
            # Split by numbered items and create basic structure
            parts = ideas_text.split('\n\n')
            for i, part in enumerate(parts[:7], 1):
                lines = [line.strip() for line in part.split('\n') if line.strip()]
                if lines:
                    ideas.append({
                        'title': lines[0] if lines else f"Idea {i}",
                        'description': ' '.join(lines[1:]) if len(lines) > 1 else '',
                        'hook': ''
                    })
        
        return ideas


if __name__ == "__main__":
    # Example usage
    import os
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        exit(1)
    
    generator = IdeaGenerator(api_key=api_key)
    ideas = generator.generate_ideas()
    
    print(f"\nGenerated {len(ideas)} ideas for today:\n")
    for i, idea in enumerate(ideas, 1):
        print(f"{i}. {idea.get('title', 'Untitled')}")
        if idea.get('description'):
            print(f"   {idea['description']}")
        if idea.get('hook'):
            print(f"   Hook: {idea['hook']}")
        print()

