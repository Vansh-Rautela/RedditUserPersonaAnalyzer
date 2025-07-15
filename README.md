🤖 Reddit User Persona Analyzer

A sophisticated tool that leverages AI to analyze public Reddit user profiles and generate detailed, professional-grade personas. This application provides deep insights into user behaviors, motivations, and personality traits, complete with a visually rich persona card and a comprehensive detailed report.
✨ Features

    AI-Powered Persona Generation: Utilizes AI to perform in-depth analysis of Reddit user activity.

    Interactive Web Interface: A Streamlit application for easy navigation and analysis of Reddit user personas.

    User Activity Analysis: Analyzes user posts and comments to generate insights about their interests and behaviors.

    Persona Visualization: Creates a visual representation of the user's persona based on their Reddit activity.

    Customizable Analysis: Configure the depth of analysis by adjusting the number of posts and comments to review.

📋 Prerequisites

Before you begin, ensure you have the following installed:

    Python 3.8+

    pip (Python package installer)

    git (for cloning the repository)

🛠️ Installation & Setup

Follow these steps to get the Reddit Persona Analyzer up and running on your local machine.
1. Clone the Repository

First, clone the project repository from GitHub to your local machine using the following command:

git clone https://github.com/yourusername/reddit-persona-analyzer.git
cd reddit-persona-analyzer
2. Install Dependencies

Install all the required Python packages using the requirements.txt file. It is recommended to do this within a virtual environment.

# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install the packages
pip install -r requirements.txt

3. Configure Environment Variables

Create a `.env` file in the project root and add your API keys and configuration:

```
# .env
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=your_user_agent
```

4. Run the Application

The application requires API keys from both Reddit and Groq to function.

Create a new file named config.env in the root directory of the project. Copy and paste the following content into the file and replace the placeholder text with your actual API credentials.

# Reddit API Credentials
CLIENT_ID=your_reddit_client_id
CLIENT_SECRET=your_reddit_client_secret
USER_AGENT=your_app_name/1.0

# Groq API Key
GROQ_API_KEY=your_groq_api_key

How to get API keys:

    Reddit:

        Go to Reddit's App Preferences.

        Scroll to the bottom and click "create another app...".

        Fill out the form:

            name: Give your application a name.

            Select "script" as the app type.

            redirect uri: http://localhost:8501

        Click "create app". Your client_id will be listed under the app name, and the client_secret will be next to it.

    Groq:

        Go to the Groq Console.

        Sign up or log in to your account.

        Create a new API key and copy it.

🚀 Running the Application

Once the installation and configuration are complete, you can run the application using the Streamlit web interface.

streamlit run app.py

This command will start the web server and open the application in your default web browser. The URL will typically be http://localhost:8501.
📁 Project Structure

The project directory is organized as follows:

/
├── app.py                      # The main Streamlit web application
├── reddit_persona_analyzer.py  # Core logic for analysis and card generation
├── requirements.txt            # List of Python dependencies
├── style.css                   # CSS for styling the web interface
├── config.env                  # Your secret API keys (you must create this)
├── personas/                   # Directory where generated cards are saved
└── README.md                   # This file

⚖️ Disclaimer

This tool is intended for educational and analytical purposes only. It analyzes publicly available data from Reddit. Please use the tool responsibly and ethically, respecting user privacy and adhering to Reddit's Terms of Service.