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
        "youtube_keywords": "peppermint tea for headache",
        "sustainability_score": 4.5,
        "eco_friendly_tips": ["Use loose leaf tea", "Compost used leaves"],
        "cultural_origin": "European Traditional Medicine",
        "scientific_evidence": "Contains menthol which aids in pain relief"
    },
    "tired": {
        "tea": "Green Tea",
        "coffee": "Espresso",
        "milkshake": "Banana Smoothie",
        "light_food": "Energy Bars or Fresh Fruits",
        "benefits": ["Boosts energy", "Improves focus", "Rich in antioxidants"],
        "ingredients": ["Green tea leaves", "Banana", "Honey"],
        "brewing_tip": "Steep green tea leaves in hot water for 3 minutes, add honey.",
        "youtube_keywords": "green tea for energy",
        "sustainability_score": 4.0,
        "eco_friendly_tips": ["Use reusable tea bags", "Choose organic tea"],
        "cultural_origin": "Traditional Chinese Medicine",
        "scientific_evidence": "Contains L-theanine for sustained energy"
    },
    "upset stomach": {
        "tea": "Ginger Tea",
        "coffee": "Avoid Coffee (Try Herbal Tea)",
        "milkshake": "Yogurt Smoothie",
        "light_food": "Plain Crackers or Toast",
        "benefits": ["Soothes stomach", "Reduces nausea", "Aids digestion"],
        "ingredients": ["Fresh ginger root", "Honey", "Lemon"],
        "brewing_tip": "Steep 1 tsp fresh ginger in hot water for 5 minutes, add honey and lemon.",
        "youtube_keywords": "ginger tea for upset stomach",
        "sustainability_score": 4.8,
        "eco_friendly_tips": ["Use local ginger", "Grow your own herbs"],
        "cultural_origin": "Traditional Asian Medicine",
        "scientific_evidence": "Contains gingerols that reduce inflammation"
    },
    "stress": {
        "tea": "Chamomile Tea",
        "coffee": "Decaf Almond Milk Latte",
        "milkshake": "Warm Vanilla Milk",
        "light_food": "Oatmeal with Almonds",
        "benefits": ["Promotes relaxation", "Reduces anxiety", "Improves sleep quality"],
        "ingredients": ["Chamomile flowers", "Honey", "Almond milk"],
        "brewing_tip": "Steep chamomile flowers in hot water for 7 minutes, add honey.",
        "youtube_keywords": "chamomile tea for stress",
        "sustainability_score": 4.2,
        "eco_friendly_tips": ["Use biodegradable tea bags", "Support local farms"],
        "cultural_origin": "European Herbal Medicine",
        "scientific_evidence": "Contains apigenin for calming effects"
    },
    "sore throat": {
        "tea": "Turmeric Ginger Tea",
        "coffee": "Avoid Coffee (Try Herbal Tea)",
        "milkshake": "Honey Lemon Smoothie",
        "light_food": "Warm Soup or Broth",
        "benefits": ["Soothes throat", "Reduces inflammation", "Boosts immunity"],
        "ingredients": ["Turmeric", "Ginger", "Honey", "Lemon"],
        "brewing_tip": "Mix 1 tsp turmeric and ginger in hot water, add honey and lemon.",
        "youtube_keywords": "turmeric tea for sore throat",
        "sustainability_score": 4.6,
        "eco_friendly_tips": ["Use fresh ingredients", "Choose organic honey"],
        "cultural_origin": "Traditional Indian Medicine (Ayurveda)",
        "scientific_evidence": "Contains curcumin with anti-inflammatory properties"
    }
}

# Enhanced Cohere API prompts
COHERE_PERSONALIZED_MESSAGE_PROMPT = """
Task: Create a personalized recommendation for someone with {ailment}.

Context:
- Recommended drink: {drink}
- Key benefits: {benefits}
- Brewing tip: {brewing_tip}
- Cultural origin: {cultural_origin}
- Scientific evidence: {scientific_evidence}
- Sustainability score: {sustainability_score}/5.0
- Eco-friendly tips: {eco_friendly_tips}

Instructions:
1. Begin with a warm, empathetic greeting acknowledging their specific ailment.
2. Explain why {drink} is particularly suitable for their condition.
3. Mention the scientific evidence and cultural background.
4. Add the brewing tip and eco-friendly suggestions.
5. End with an encouraging note about relief and sustainability.

Keep your response friendly, informative, and under 150 words. Balance traditional wisdom with scientific backing.
"""

# Weather-based recommendations
WEATHER_RECOMMENDATIONS = {
    "cold": {
        "boost": ["ginger", "cinnamon", "turmeric"],
        "avoid": ["cold drinks", "iced tea"]
    },
    "hot": {
        "boost": ["mint", "cucumber", "coconut water"],
        "avoid": ["hot drinks", "heavy ingredients"]
    },
    "rainy": {
        "boost": ["immunity herbs", "warming spices"],
        "avoid": ["cold ingredients", "raw foods"]
    }
}
