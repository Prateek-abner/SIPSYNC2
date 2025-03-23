# SipSync: AI-Powered Wellness Drink Recommender 🍵

SipSync is an intelligent wellness companion that provides personalized drink recommendations based on your current state of health, and sustainability preferences. Using advanced AI technology, it combines traditional wisdom with modern science to suggest the perfect brew for your needs.

## 🌟 Features

### 1. Personalized Recommendations
- AI-powered drink suggestions based on your ailments
- Weather-aware recommendations that adapt to your local conditions
- Multiple drink types: Tea, Coffee, Milkshakes, and Light Foods
- Scientific evidence and cultural context for each recommendation

### 2. Multi-language Support
- Automatic language detection
- Real-time translation in 10 languages:
  - English (en)
  - French (fr)
  - Spanish (es)
  - Chinese (zh)
  - Hindi (hi)
  - Arabic (ar)
  - Bengali (bn)
  - Portuguese (pt)
  - Russian (ru)
  - Japanese (ja)

### 3. Sustainability Focus
- Eco-friendly tips for each recommendation
- Sustainability scoring system
- Local ingredient sourcing suggestions
- Environmental impact considerations

### 4. Interactive Features
- Interactive map for finding nearby stores
- Educational YouTube videos
- User profile with recommendation history
- Analytics and insights visualization

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **AI/ML**: 
  - Cohere AI for personalized messages
  - Google Gemini for intelligent recommendations
- **APIs**:
  - Google Maps API for location services
  - YouTube Data API for educational content
- **Data Visualization**: Plotly, Folium
- **Language Processing**: LangDetect, Googletrans

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Prateek-abner/SIPSYNC2.git
cd SIPSYNC2
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the project root with your API keys:
COHERE_API_KEY=your_cohere_api_key_here
GOOGLE_CLOUD_API_KEY=your_google_cloud_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here


5. Run the application:
```bash
cd UPDATED
streamlit run app.py
```

## 📝 Usage

1. Select your preferred drink type (Tea, Coffee, Milkshake, or Light Food)
2. Enter your current ailment or how you're feeling
3. (Optional) Enter your location for weather-aware recommendations
4. Click "Find My Brew" to get personalized recommendations
5. Explore the detailed information, including:
   - Benefits and ingredients
   - Brewing instructions
   - Sustainability tips
   - Nearby stores
   - Educational videos

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Cohere AI for natural language processing capabilities
- Google Cloud for Gemini AI and Maps integration
- OpenWeather for weather data
- All contributors and supporters

## 🔮 Future Enhancements

- Mobile app version
- Social sharing features
- Community recommendations
- Enhanced AI personalization
- More language support
- Advanced analytics
- Integration with smart home devices
