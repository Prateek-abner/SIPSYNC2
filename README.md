# SipSync: Daily Brew Matchmaker

A personalized beverage recommendation system that suggests drinks based on your ailments and preferences, with multi-language support and weather-aware recommendations.

## Features

- 🍵 Personalized drink recommendations (tea, coffee, milkshakes, light food)
- 🌍 Multi-language support (10 languages)
- 🌤️ Weather-aware recommendations
- 📊 User analytics and insights
- 🗺️ Nearby store locator
- 📱 Modern, responsive UI
- 🌱 Sustainability focus

## Setup Instructions

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - Unix/MacOS:
     ```bash
     source venv/bin/activate
     ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Set up API keys:
   - Create a `.env` file in the project root
   - Add your API keys:
     ```
     COHERE_API_KEY=your_cohere_api_key_here
     GOOGLE_CLOUD_API_KEY=your_google_cloud_api_key_here
     OPENWEATHER_API_KEY=your_openweather_api_key_here
     ```

6. Run the application:
   ```bash
   streamlit run app.py
   ```

## API Keys Setup

1. Cohere API Key:
   - Sign up at [Cohere Dashboard](https://dashboard.cohere.ai/)
   - Create a new API key

2. Google Cloud API Key:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable YouTube Data API v3 and Gemini API
   - Create API credentials

3. OpenWeather API Key:
   - Sign up at [OpenWeather](https://openweathermap.org/)
   - Get your API key

## Project Structure

- `app.py`: Main Streamlit application
- `backend.py`: Core recommendation logic
- `train.py`: Training data and recommendation rules
- `language_support.py`: Multi-language support
- `maps.py`: Location and store finding functionality
- `youtube.py`: YouTube video integration
- `user_profile.py`: User profile management

## Troubleshooting

1. If you get API key errors:
   - Check if your `.env` file is properly configured
   - Verify API keys are valid and have necessary permissions

2. If language detection fails:
   - Ensure you have internet connectivity
   - Try reinstalling the language detection packages

3. For YouTube video issues:
   - Verify your Google Cloud API key has YouTube Data API enabled
   - Check your daily quota limits

## Contributing

Feel free to submit issues and enhancement requests!