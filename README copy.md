# 🔍 Reddit User Persona Analyzer

A comprehensive tool for analyzing Reddit user profiles and generating detailed personas with citations from their posts and comments. This project uses advanced LLM technology to create insightful user personas that include demographics, psychology, online behavior, expertise, and social dynamics.

## 🚀 Features

- **Comprehensive Analysis**: Analyzes user posts, comments, and profile data
- **AI-Powered Personas**: Uses Groq LLM to generate detailed user personas
- **Citation System**: Every characteristic includes citations from actual posts/comments
- **Multiple Output Formats**: Command-line tool and web interface
- **Visual Analytics**: Charts and statistics for user activity
- **Export Capabilities**: Save detailed reports as text files

## 📋 Requirements

- Python 3.8+
- Reddit API credentials
- Groq API key
- Internet connection

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd Ashiwn-reddit
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

Create a `config.env` file in the project root with your API credentials:

```env
CLIENT_ID=your_reddit_client_id
CLIENT_SECRET=your_reddit_client_secret
USER_AGENT=your_app_name/1.0
GROQ_API_KEY=your_groq_api_key
```

#### Getting Reddit API Credentials:

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Select "script" as the app type
4. Fill in the required information
5. Copy the client ID and client secret

#### Getting Groq API Key:

1. Visit https://console.groq.com/
2. Sign up for an account
3. Generate an API key
4. Copy the API key to your config file

## 🎯 Usage

### Command Line Interface

Analyze a Reddit user profile:

```bash
python reddit_persona_analyzer.py https://www.reddit.com/user/username/
```

Example:
```bash
python reddit_persona_analyzer.py https://www.reddit.com/user/kojied/
```

### Web Interface

Launch the Streamlit web interface:

```bash
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

## 📊 Output Format

The tool generates comprehensive persona reports including:

### 1. Demographics
- Age range estimation
- Geographic location
- Occupation/profession
- Education level

### 2. Psychology
- Personality traits
- Communication style
- Values and beliefs
- Stress management patterns

### 3. Online Behavior
- Reddit usage patterns
- Community engagement level
- Posting frequency and timing
- Interaction style

### 4. Expertise & Knowledge
- Areas of expertise
- Knowledge depth
- Specialized interests
- Professional background hints

### 5. Social Dynamics
- Community relationships
- Influence level
- Conflict resolution style
- Supportiveness

Each characteristic includes:
- **Trait**: The specific observation
- **Citation**: Direct reference to posts/comments
- **Confidence**: High/Medium/Low confidence level

## 📁 Project Structure

```
Ashiwn-reddit/
├── reddit_persona_analyzer.py    # Main analysis script
├── app.py                        # Streamlit web interface
├── requirements.txt              # Python dependencies
├── config.env                   # API configuration
├── README.md                    # This file
├── sample_persona_kojied.txt    # Sample output
└── sample_persona_Hungry-Move-6603.txt  # Sample output
```

## 🔧 Configuration Options

### Analysis Parameters

You can customize the analysis by modifying these parameters in the code:

- `post_limit`: Number of posts to analyze (default: 30)
- `comment_limit`: Number of comments to analyze (default: 50)
- `temperature`: LLM creativity level (default: 0.7)
- `max_tokens`: Maximum response length (default: 4000)

### LLM Model

The tool uses Groq's `llama3-70b-8192` model by default. You can change this in the `analyze_user_persona` method.

## 📈 Sample Outputs

The repository includes sample persona reports for demonstration:

- `sample_persona_kojied.txt`: Professional software developer persona
- `sample_persona_Hungry-Move-6603.txt`: Student persona

## 🚨 Error Handling

The tool includes comprehensive error handling for:

- Invalid Reddit URLs
- API rate limits
- Network connectivity issues
- Missing or invalid API credentials
- User profile privacy settings

## 🔒 Privacy & Ethics

### Important Considerations:

1. **Respect Privacy**: Only analyze public Reddit profiles
2. **Rate Limiting**: The tool respects Reddit's API rate limits
3. **Data Usage**: Generated personas are for analysis purposes only
4. **User Consent**: Ensure compliance with Reddit's terms of service

### Best Practices:

- Use the tool responsibly and ethically
- Don't share personal information from analyses
- Respect user privacy and Reddit's community guidelines
- Consider the impact of your analysis on individuals

## 🐛 Troubleshooting

### Common Issues:

1. **API Connection Errors**
   - Verify your API credentials in `config.env`
   - Check your internet connection
   - Ensure Reddit API is accessible

2. **Rate Limiting**
   - Wait a few minutes between analyses
   - Reduce the number of posts/comments analyzed

3. **User Not Found**
   - Verify the Reddit username exists
   - Check if the profile is public
   - Ensure the URL format is correct

4. **LLM Response Issues**
   - Check your Groq API key
   - Verify your Groq account has sufficient credits
   - Try reducing the analysis scope

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for:

- Bug fixes
- Feature enhancements
- Documentation improvements
- Performance optimizations

## 📄 License

This project is for educational and assessment purposes. Please ensure compliance with:

- Reddit's API terms of service
- Groq's usage policies
- Applicable privacy laws and regulations

## 🙏 Acknowledgments

- Reddit API for providing access to user data
- Groq for LLM capabilities
- Streamlit for the web interface framework
- The Reddit community for inspiration

## 📞 Support

For issues or questions:

1. Check the troubleshooting section above
2. Review the error messages for specific guidance
3. Ensure all dependencies are properly installed
4. Verify your API credentials are correct

---

**Note**: This tool is designed for educational and assessment purposes. Always use responsibly and in compliance with Reddit's terms of service and applicable privacy regulations. 