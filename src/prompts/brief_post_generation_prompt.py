brief_post_generation_prompt = """You are helping a freelance ML engineer create LinkedIn content. Generate 5 brief versions of a LinkedIn post based on the selected idea. 

SELECTED IDEA:
Title: {idea_title}

CONTENT PILLAR:
Topic: {pillar_name}
Description: {pillar_description}

TASK:
Generate exactly 5 BRIEF versions of this LinkedIn post. Each version should be:
- Short and concise (approximately 3-5 sentences or 100-200 words)
- Different in approach, angle, or style from the others

Note, do not generate the full post, just short snippets/summaries of the post. 
These are PREVIEW versions - they should give a sense of what the full post would be like, but be brief enough to quickly compare different approaches.

Format your response as a numbered list (1-5), with each brief post clearly separated by blank lines.
"""

