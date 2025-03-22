# train.py

# Cohere API prompts
COHERE_TEA_RECOMMENDATION_PROMPT = """
Task: Based on the user's described ailment '{ailment}', recommend the most scientifically appropriate herbal tea.

Available herbal teas to choose from: {tea_options}

Consider these factors:
1. The specific symptoms described
2. Known medicinal properties of each tea
3. Scientific research supporting each tea's efficacy

Respond with ONLY the name of the single most appropriate tea from the list above.
Example output: "Chamomile Tea" or "Ginger Tea"
"""

COHERE_PERSONALIZED_MESSAGE_PROMPT = """
Task: Create a personalized herbal tea recommendation for someone with {ailment}.

Details:
- Recommended tea: {tea}
- Key benefits: {benefits}
- Time of day: {time_context}
- Current season: {season}

Instructions:
1. Begin with a warm, empathetic greeting acknowledging their specific ailment
2. Explain why {tea} is particularly suitable for their condition
3. Mention 1-2 specific active compounds or properties that make this tea effective
4. Add a relevant seasonal or time-of-day context to your recommendation
5. End with an encouraging note about relief or wellbeing

Keep your response friendly, informative, and under 100 words. Avoid medical claims that sound too definitive.
"""

COHERE_BREWING_TIP_PROMPT = """
Task: Provide one specific brewing tip for {tea} that will maximize its effectiveness for {ailment}.

Your tip should:
1. Be based on scientific principles about extracting beneficial compounds
2. Be specific (exact temperature, timing, or technique)
3. Explain briefly why this method is particularly effective

Keep your response under 50 words and start with "Pro tip:"
"""

COHERE_DAILY_TEA_DESCRIPTION_PROMPT = """
Task: Create a brief, enticing description for our "Tea of the Day" feature highlighting {tea}.

Include:
1. What makes this tea special
2. Its primary health benefits
3. An intriguing fact about its origin or history

Keep it concise (under 75 words) and engaging.
"""

# YouTube API configuration
YOUTUBE_API_CONFIG = {
    "max_results": 3,
    "order": "relevance"
}
