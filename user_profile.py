# user_profile.py

import json
import os
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

class UserProfile:
    def __init__(self, user_id):
        self.user_id = user_id
        self.preferences = {
            'language': 'en',
            'preferred_drink_type': 'tea',
            'dietary_restrictions': [],
            'sustainability_focus': True,
            'cultural_preferences': []
        }
        self.recommendation_history = []
        self.load_profile()

    def load_profile(self):
        """Load user profile from file if it exists."""
        profile_dir = "user_profiles"
        os.makedirs(profile_dir, exist_ok=True)
        profile_path = os.path.join(profile_dir, f"{self.user_id}.json")
        
        if os.path.exists(profile_path):
            try:
                with open(profile_path, 'r') as f:
                    data = json.load(f)
                    self.preferences = data.get('preferences', self.preferences)
                    self.recommendation_history = data.get('history', [])
            except:
                print(f"Error loading profile for user {self.user_id}")

    def save_profile(self):
        """Save user profile to file."""
        profile_dir = "user_profiles"
        os.makedirs(profile_dir, exist_ok=True)
        profile_path = os.path.join(profile_dir, f"{self.user_id}.json")
        
        data = {
            'preferences': self.preferences,
            'history': self.recommendation_history
        }
        
        try:
            with open(profile_path, 'w') as f:
                json.dump(data, f, indent=2)
        except:
            print(f"Error saving profile for user {self.user_id}")

    def update_preferences(self, preferences):
        """Update user preferences."""
        self.preferences.update(preferences)
        self.save_profile()

    def add_recommendation(self, recommendation):
        """Add a recommendation to history."""
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'ailment': recommendation['ailment'],
            'drink': recommendation['drink'],
            'sustainability_score': recommendation.get('sustainability_score', 0),
            'weather_adjusted': recommendation.get('weather_adjusted', False)
        }
        self.recommendation_history.append(history_entry)
        self.save_profile()

    def get_recommendation_stats(self):
        """Get statistics about user's recommendations."""
        if not self.recommendation_history:
            return None
            
        df = pd.DataFrame(self.recommendation_history)
        
        stats = {
            'total_recommendations': len(df),
            'unique_ailments': len(df['ailment'].unique()),
            'avg_sustainability': df['sustainability_score'].mean(),
            'most_common_ailment': df['ailment'].mode().iloc[0] if not df.empty else None,
            'weather_adjusted_percent': (df['weather_adjusted'].sum() / len(df)) * 100
        }
        
        return stats

    def generate_insights_visualizations(self):
        """Generate visualization of user's recommendation history."""
        if not self.recommendation_history:
            return None
            
        df = pd.DataFrame(self.recommendation_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Ailment distribution pie chart
        ailment_dist = px.pie(
            df, 
            names='ailment',
            title='Distribution of Ailments'
        )
        
        # Sustainability score over time
        sustainability_trend = px.line(
            df, 
            x='timestamp', 
            y='sustainability_score',
            title='Sustainability Score Trend'
        )
        
        # Weather adjustment usage
        weather_usage = go.Figure(data=[
            go.Bar(
                x=['Weather-Adjusted', 'Standard'],
                y=[
                    df['weather_adjusted'].sum(),
                    len(df) - df['weather_adjusted'].sum()
                ]
            )
        ])
        weather_usage.update_layout(title='Weather Adjustment Usage')
        
        return {
            'ailment_distribution': ailment_dist,
            'sustainability_trend': sustainability_trend,
            'weather_usage': weather_usage
        }

    def get_personalized_suggestions(self):
        """Generate personalized suggestions based on user history."""
        if not self.recommendation_history:
            return []
            
        df = pd.DataFrame(self.recommendation_history)
        
        # Find most effective remedies
        effectiveness_score = df.groupby('drink').size()
        top_drinks = effectiveness_score.nlargest(3)
        
        suggestions = []
        for drink, count in top_drinks.items():
            suggestions.append({
                'drink': drink,
                'times_used': int(count),
                'message': f"You've found {drink} helpful {count} times."
            })
            
        return suggestions 
