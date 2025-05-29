drug_keywords = {
    "2c-b": "psychedelics", "420": "marijuana", "420plug": "marijuana", "8 ball": "cocaine", "M30": "opioids",
    "acapulco gold": "marijuana", "acid": "lsd", "acid drops": "lsd", "acid hits": "lsd", "acid pop": "lsd"
}
coded_slang = {
    "broccoli": {"category": "marijuana", "weight": 0.8}, "blunt": {"category": "marijuana", "weight": 0.8},
    "salad": {"category": "marijuana", "weight": 0.8}, "alfalfa": {"category": "marijuana", "weight": 0.8},
    "lettuce": {"category": "marijuana", "weight": 0.8}, "2c-b": {"category": "psychedelics", "weight": 0.8}
}
drug_hashtags = {
    "420": {"category": "marijuana", "weight": 0.4}, "420blazeit": {"category": "marijuana", "weight": 0.5},
    "420blessed": {"category": "marijuana", "weight": 0.3}, "420cartel": {"category": "marijuana", "weight": 0.7},
    "420connect": {"category": "marijuana", "weight": 0.6}, "#2cb": {"category": "psychedelics", "weight": 0.7}
}
suspicious_phrases = [
    "need some stuff", "got anything good?", "looking for a plug", "where’s the connect?", "know anyone selling?"
]
transaction_phrases = [
    "hit me up", "on sale", "ready for pick-up", "just arrived", "prices just went up"
]
drug_emoji_map = {
    "opioids": [
        {"emoji": "💊", "weight": 0.4, "context": "xanax"},
        {"emoji": "💉", "weight": 0.4, "context": "smack"}
    ],
    "benzodiazepines": [
        {"emoji": "💊", "weight": 0.4, "context": "bars"}
    ],
    "marijuana": [
        {"emoji": "🌿", "weight": 0.4, "context": "weed"}
    ]
}
ambiguous_keywords = {
    "coke": [{"category": "cocaine", "weight": 0.5}, {"category": "soda", "weight": 0.0}],
    "weed": [{"category": "marijuana", "weight": 0.5}, {"category": "garden", "weight": 0.0}]
}
safe_context_words = {
    "420": ["April 20th", "calendar", "celebration"],
    "acid": ["battery", "chemical", "chemistry"]
}