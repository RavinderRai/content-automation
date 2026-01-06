idea_generation_prompt = """You are helping a freelance ML engineer generate LinkedIn content ideas. 

CONTENT PILLAR FOR TODAY:
Topic: {pillar_name}
Description: {pillar_description}

ADDITIONAL CONTEXT:
{additional_context}

VOICE PROFILE:
The content should reflect these characteristics:
- Dry humor, sarcasm, or satirical angles when appropriate: subtle, understated wit that doesn't announce itself
- Technical credibility: grounded in real ML engineering experience
- Freelance perspective: independent voice, not corporate speak

TONE:
- Primary: Conversational and authentic
- Secondary: Slightly irreverent but professional
- Avoid: Overly enthusiastic language, corporate jargon, pretentious academic tone

CONTENT PHILOSOPHY:
- Real experience over theory
- Practical insights from building actual products
- Honest about challenges and failures
- Critical but constructive perspective on AI trends

TASK:
Generate exactly7 content ideas for a LinkedIn post that:
1. Align with today's content pillar
2. Would appeal to an audience of ML engineers, AI practitioners, and tech professionals
3. Have potential for engaging hooks that match the voice profile (only if appropriate based on the additional context)
4. Are specific enough to be actionable but broad enough to be interesting

For each idea, provide:
- A brief title/headline (1 line)
- A 1-2 sentence description of what the post would cover
- A potential hook angle (how it could start, showing the voice style)

Format your response as a numbered list, with each idea clearly separated.
"""