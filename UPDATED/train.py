# train.py

# Hardcoded rules for ailments and recommendations
RECOMMENDATIONS = {
    "headache": {
        "tea": "Peppermint Tea",
        "coffee": "Cold Brew Coffee",
        "milkshake": "Mint Chocolate Shake",
        "light_food": "Dark Chocolate or Nuts",
        "benefits": ["Relieves tension", "Reduces stress", "Improves focus"],
        "ingredients": ["Peppermint leaves", "Honey", "Dark chocolate"],
        "brewing_tip": "Steep peppermint leaves in hot water for 5 minutes, add honey.",
        "youtube_keywords": "peppermint tea for headache"
    },
    "tired": {
        "tea": "Green Tea",
        "coffee": "Espresso",
        "milkshake": "Banana Smoothie",
        "light_food": "Energy Bars or Fresh Fruits",
        "benefits": ["Boosts energy", "Improves focus", "Rich in antioxidants"],
        "ingredients": ["Green tea leaves", "Banana", "Honey"],
        "brewing_tip": "Steep green tea leaves in hot water for 3 minutes, add honey.",
        "youtube_keywords": "green tea for energy"
    },
    "upset stomach": {
        "tea": "Ginger Tea",
        "coffee": "Avoid Coffee (Try Herbal Tea)",
        "milkshake": "Yogurt Smoothie",
        "light_food": "Plain Crackers or Toast",
        "benefits": ["Soothes stomach", "Reduces nausea", "Aids digestion"],
        "ingredients": ["Fresh ginger root", "Honey", "Lemon"],
        "brewing_tip": "Steep 1 tsp fresh ginger in hot water for 5 minutes, add honey and lemon.",
        "youtube_keywords": "ginger tea for upset stomach"
    },
    "stress": {
        "tea": "Chamomile Tea",
        "coffee": "Decaf Almond Milk Latte",
        "milkshake": "Warm Vanilla Milk",
        "light_food": "Oatmeal with Almonds",
        "benefits": ["Promotes relaxation", "Reduces anxiety", "Improves sleep quality"],
        "ingredients": ["Chamomile flowers", "Honey", "Almond milk"],
        "brewing_tip": "Steep chamomile flowers in hot water for 7 minutes, add honey.",
        "youtube_keywords": "chamomile tea for stress"
    }
}

# Cohere API prompts
COHERE_PERSONALIZED_MESSAGE_PROMPT = """
Task: Create a personalized recommendation for someone with {ailment}.

Details:
- Recommended drink: {drink}
- Key benefits: {benefits}
- Brewing tip: {brewing_tip}

Instructions:
1. Begin with a warm, empathetic greeting acknowledging their specific ailment.
2. Explain why {drink} is particularly suitable for their condition.
3. Mention 1-2 specific active compounds or properties that make this drink effective.
4. Add a relevant brewing tip to your recommendation.
5. End with an encouraging note about relief or wellbeing.

Keep your response friendly, informative, and under 100 words. Avoid medical claims that sound too definitive.
"""
