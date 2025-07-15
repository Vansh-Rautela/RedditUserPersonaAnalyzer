#!/usr/bin/env python3
"""
Reddit User Persona Analyzer
A comprehensive tool to analyze Reddit user profiles and generate detailed personas with citations.
"""

import os
import re
import json
import logging
import textwrap
import math
import requests
from io import BytesIO
from datetime import datetime
from urllib.parse import urlparse
from typing import Dict, List, Tuple, Optional

import praw
from groq import Groq
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont, ImageOps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
LOGGER = logging.getLogger(__name__)

# --- Constants ---
LLM_MODEL = "llama3-70b-8192"
PERSONAS_DIR = "personas"
CARD_DIMENSIONS = (1600, 900) # Increased for higher quality
DEFAULT_AVATAR_URL = "https://www.redditstatic.com/avatars/avatar_default_02_A5A4A4.png"


# --- Monochrome Card Styling Constants ---
BG_COLOR = "#181818"
TEXT_COLOR = "#E0E0E0"
HEADER_COLOR = "#FFFFFF"
ACCENT_COLOR = "#FFFFFF" 
MUTED_COLOR = "#A0A0A0"
BAR_BG_COLOR = "#404040"


class RedditPersonaAnalyzer:
    """
    A comprehensive Reddit user persona analyzer that scrapes user activity
    and generates detailed personas with citations.
    """

    def __init__(self):
        """Initialize the analyzer with Reddit and Groq API clients."""
        load_dotenv('config.env')
        self.reddit = praw.Reddit(
            client_id=os.getenv("CLIENT_ID"),
            client_secret=os.getenv("CLIENT_SECRET"),
            user_agent=os.getenv("USER_AGENT")
        )
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self._load_fonts()
        LOGGER.info("Reddit Persona Analyzer initialized successfully")

    def _load_fonts(self):
        """Load fonts for persona card generation."""
        try:
            # Increased font sizes for better readability on a larger canvas
            self.font_username = ImageFont.truetype("arialbd.ttf", 60)
            self.font_title = ImageFont.truetype("arialbd.ttf", 28)
            self.font_regular = ImageFont.truetype("arial.ttf", 22)
            self.font_small = ImageFont.truetype("arial.ttf", 20)
            self.font_quote = ImageFont.truetype("ariali.ttf", 26)
        except IOError:
            LOGGER.warning("Arial font not found. Using default font.")
            self.font_username = ImageFont.load_default()
            self.font_title = ImageFont.load_default()
            self.font_regular = ImageFont.load_default()
            self.font_small = ImageFont.load_default()
            self.font_quote = ImageFont.load_default()

    def extract_username_from_url(self, url: str) -> str:
        """Extract username from a Reddit profile URL."""
        try:
            path = urlparse(url).path.strip("/")
            return path.split("/")[-1]
        except Exception as e:
            LOGGER.error(f"Error extracting username from URL {url}: {e}")
            raise ValueError(f"Invalid Reddit URL: {url}")

    def get_user_activity(self, username: str, post_limit: int = 30, comment_limit: int = 50) -> Dict:
        """Scrape user's posts and comments from Reddit."""
        try:
            user = self.reddit.redditor(username)
            profile_info = {
                'username': username,
                'icon_img': user.icon_img,
                'created_utc': user.created_utc,
                'comment_karma': user.comment_karma,
                'link_karma': user.link_karma,
                'is_gold': user.is_gold,
                'is_mod': user.is_mod,
                'has_verified_email': getattr(user, 'has_verified_email', False)
            }
            posts = self._get_user_posts(user, post_limit)
            comments = self._get_user_comments(user, comment_limit)
            return {'profile': profile_info, 'posts': posts, 'comments': comments}
        except Exception as e:
            LOGGER.error(f"Error fetching user activity for {username}: {e}")
            raise

    def _get_user_posts(self, user, limit: int) -> List[Dict]:
        """Fetch a user's recent posts."""
        posts = []
        try:
            for sub in user.submissions.new(limit=limit):
                posts.append({
                    'title': sub.title, 
                    'selftext': sub.selftext, 
                    'permalink': f"https://www.reddit.com{sub.permalink}"
                })
        except Exception as e:
            LOGGER.warning(f"Could not fetch posts for {user.name}: {e}")
        return posts

    def _get_user_comments(self, user, limit: int) -> List[Dict]:
        """Fetch a user's recent comments."""
        comments = []
        try:
            for c in user.comments.new(limit=limit):
                comments.append({
                    'body': c.body, 
                    'permalink': f"https://www.reddit.com{c.permalink}"
                })
        except Exception as e:
            LOGGER.warning(f"Could not fetch comments for {user.name}: {e}")
        return comments

    def analyze_user_persona(self, user_data: Dict) -> Dict:
        """Analyze user data and generate a structured persona using an LLM."""
        try:
            prompt = self._create_structured_persona_prompt(user_data)
            response = self.groq_client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are a world-class marketing and psychological analyst. Your task is to create a detailed, structured user persona from Reddit data, including citations and confidence scores for every piece of inferred information. Provide your output as a single, valid JSON object only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=4000,
                response_format={"type": "json_object"},
            )
            persona_json_string = response.choices[0].message.content
            return json.loads(persona_json_string)
        except Exception as e:
            LOGGER.error(f"Error analyzing user persona: {e}")
            return {"error": f"Failed to generate persona. Details: {str(e)}"}

    def _create_structured_persona_prompt(self, user_data: Dict) -> str:
        """Create a prompt requesting a detailed, structured JSON output with citations."""
        posts_text = "\n".join([f"Post: {p['title']} (URL: {p['permalink']})" for p in user_data['posts'][:10]])
        comments_text = "\n".join([f"Comment: {c['body'][:100]} (URL: {c['permalink']})" for c in user_data['comments'][:15]])

        return f"""
        Analyze the Reddit user 'u/{user_data['profile']['username']}' based on the provided data. Generate a comprehensive persona as a single, valid JSON object. For EVERY inferred value, you MUST provide a 'citation' URL and a 'confidence' level ('High', 'Medium', or 'Low').

        **User Activity Data:**
        {posts_text}
        {comments_text}

        **JSON Schema to follow:**
        {{
          "userProfile": {{
            "ageRange": {{"value": "e.g., '30-40'", "citation": "URL", "confidence": "High|Medium|Low"}},
            "location": {{"value": "e.g., 'India'", "citation": "URL", "confidence": "High|Medium|Low"}},
            "occupation": {{"value": "e.g., 'Financial Professional'", "citation": "URL", "confidence": "High|Medium|Low"}}
          }},
          "quote": {{"value": "A short, impactful quote that reveals personality.", "citation": "URL", "confidence": "High|Medium|Low"}},
          "behavioralTraits": [
              {{"trait": "Digital Literacy", "value": "High|Medium|Low", "evidence": "Briefly describe evidence.", "citation": "URL", "confidence": "High|Medium|Low"}},
              {{"trait": "Price Sensitivity", "value": "High|Medium|Low", "evidence": "Briefly describe evidence.", "citation": "URL", "confidence": "High|Medium|Low"}}
          ],
          "motivationsAndValues": {{
            "primaryMotivation": {{"value": "e.g., 'Financial Security'", "marketingAngle": "Marketing suggestion", "citation": "URL", "confidence": "High|Medium|Low"}},
            "secondaryMotivation": {{"value": "e.g., 'Health and Wellness'", "marketingAngle": "Marketing suggestion", "citation": "URL", "confidence": "High|Medium|Low"}},
            "valueSystem": {{"value": "A sentence describing their core values.", "citation": "URL", "confidence": "High|Medium|Low"}}
          }},
          "personalityInsights": {{
              "openness": {{"score": "Score 0-10", "marketingImpact": "Marketing suggestion", "citation": "URL", "confidence": "High|Medium|Low"}},
              "conscientiousness": {{"score": "Score 0-10", "marketingImpact": "Marketing suggestion", "citation": "URL", "confidence": "High|Medium|Low"}},
              "introvert_extrovert": {{"score": "Score from 0-100 (0=Introvert, 100=Extrovert)", "citation": "URL", "confidence": "High|Medium|Low"}},
              "sensing_intuition": {{"score": "Score from 0-100 (0=Sensing, 100=Intuition)", "citation": "URL", "confidence": "High|Medium|Low"}},
              "thinking_feeling": {{"score": "Score from 0-100 (0=Thinking, 100=Feeling)", "citation": "URL", "confidence": "High|Medium|Low"}}
          }},
          "behaviors": [{{"value": "A key observed behavior or habit.", "citation": "URL", "confidence": "High|Medium|Low"}}],
          "goals": [{{"value": "A key goal or need of the user.", "citation": "URL", "confidence": "High|Medium|Low"}}],
          "frustrations": [{{"value": "A key pain point or frustration.", "citation": "URL", "confidence": "High|Medium|Low"}}]
        }}
        """

    def generate_persona_card(self, persona_data: Dict, user_data: Dict) -> str:
        """Creates a stylized, high-quality persona card image."""
        os.makedirs(PERSONAS_DIR, exist_ok=True)
        image = Image.new("RGB", CARD_DIMENSIONS, color=BG_COLOR)
        draw = ImageDraw.Draw(image)
        
        avatar_url = user_data['profile'].get('icon_img', DEFAULT_AVATAR_URL)
        avatar_image = self._get_avatar(avatar_url)

        # --- Draw Layout ---
        self._draw_avatar_and_quote(image, draw, avatar_image, user_data['profile']['username'], persona_data)
        self._draw_motivation_bars(draw, persona_data.get('motivationsAndValues', {}), (450, 420))
        self._draw_personality_scales(draw, persona_data.get('personalityInsights', {}), (450, 620))
        
        self._draw_list_section(draw, "BEHAVIOUR & HABITS", persona_data.get('behaviors', []), (950, 100))
        self._draw_list_section(draw, "GOALS & NEEDS", persona_data.get('goals', []), (950, 400))
        self._draw_list_section(draw, "FRUSTRATIONS", persona_data.get('frustrations', []), (950, 650))


        filename = f"persona_card_{user_data['profile']['username']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        filepath = os.path.join(PERSONAS_DIR, filename)
        image.save(filepath, "JPEG", quality=100)
        LOGGER.info(f"Persona card saved to {filepath}")
        return filepath

    def _get_avatar(self, url: str) -> Image:
        """Downloads and prepares a circular avatar image."""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content)).convert("RGBA")
        except requests.exceptions.RequestException as e:
            LOGGER.warning(f"Failed to download avatar, using default. Error: {e}")
            response = requests.get(DEFAULT_AVATAR_URL, stream=True)
            img = Image.open(BytesIO(response.content)).convert("RGBA")

        size = (300, 300)
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        
        output = ImageOps.fit(img, size, centering=(0.5, 0.5))
        output.putalpha(mask)
        return output

    def _draw_avatar_and_quote(self, image, draw, avatar, username, persona_data):
        image.paste(avatar, (50, 100), avatar)
        
        draw.text((450, 100), f"u/{username}", font=self.font_username, fill=HEADER_COLOR)
        draw.line([(450, 180), (850, 180)], fill=BAR_BG_COLOR, width=2)
        
        y_pos = 200
        demographics = persona_data.get('userProfile', {})
        for key, data in demographics.items():
            draw.text((450, y_pos), key.replace("Range", " ").upper(), font=self.font_small, fill=MUTED_COLOR)
            draw.text((620, y_pos), str(data.get('value')), font=self.font_small, fill=TEXT_COLOR)
            y_pos += 40

        quote = persona_data.get('quote', {}).get('value', '')
        if quote:
            wrapped_quote = textwrap.wrap(f'"{quote}"', width=30)
            y_pos = 450
            draw.rectangle([(50, y_pos - 20), (350, y_pos + len(wrapped_quote)*35 + 20)], fill=BAR_BG_COLOR)
            for line in wrapped_quote:
                draw.text((70, y_pos), line, font=self.font_quote, fill=TEXT_COLOR)
                y_pos += 35

    def _draw_motivation_bars(self, draw, data, pos):
        x, y = pos
        draw.text((x, y), "MOTIVATIONS", font=self.font_title, fill=HEADER_COLOR)
        y += 50
        bar_width = 400
        
        motivations = [data.get('primaryMotivation', {}), data.get('secondaryMotivation', {})]
        for item in motivations:
            if not item: continue
            trait = item.get('value', 'Unknown')
            score = 75 
            draw.text((x, y), trait.upper(), font=self.font_small, fill=TEXT_COLOR)
            draw.rectangle([(x, y + 30), (x + bar_width, y + 40)], fill=BAR_BG_COLOR)
            fill_width = (bar_width * score) / 100
            draw.rectangle([(x, y + 30), (x + fill_width, y + 40)], fill=ACCENT_COLOR)
            y += 60

    def _draw_personality_scales(self, draw, data, pos):
        x, y = pos
        draw.text((x, y), "PERSONALITY", font=self.font_title, fill=HEADER_COLOR)
        y += 50
        bar_width = 400
        
        scales = [
            ("INTROVERT", "EXTROVERT", data.get("introvert_extrovert", {}).get("score", 50)),
            ("SENSING", "INTUITION", data.get("sensing_intuition", {}).get("score", 50)),
            ("THINKING", "FEELING", data.get("thinking_feeling", {}).get("score", 50))
        ]

        for left, right, score in scales:
            score = int(score)
            draw.text((x, y), left, font=self.font_small, fill=TEXT_COLOR)
            draw.text((x + bar_width - self.font_small.getbbox(right)[2], y), right, font=self.font_small, fill=TEXT_COLOR)
            draw.rectangle([(x, y + 30), (x + bar_width, y + 35)], fill=BAR_BG_COLOR)
            marker_pos = x + (bar_width * score) / 100
            draw.rectangle([(marker_pos - 3, y + 27), (marker_pos + 3, y + 38)], fill=ACCENT_COLOR)
            y += 60

    def _draw_list_section(self, draw, title, data, pos):
        x, y = pos
        draw.text((x, y), title, font=self.font_title, fill=HEADER_COLOR)
        draw.line([(x, y + 45), (x + 600, y + 45)], fill=BAR_BG_COLOR, width=2)
        y += 70
        for item in data:
            point = item.get('value')
            if point:
                for line in textwrap.wrap(f"• {point}", width=60):
                    draw.text((x, y), line, font=self.font_regular, fill=TEXT_COLOR)
                    y += 30
                y += 20

    def generate_detailed_report(self, persona_data: Dict, user_data: Dict) -> str:
        """Generates a detailed text report from the persona data."""
        profile = user_data['profile']
        username = profile['username']
        
        created_date = datetime.fromtimestamp(profile['created_utc'])
        age_delta = datetime.now() - created_date
        years = age_delta.days // 365
        months = (age_delta.days % 365) // 30
        age_str = f"{years} years, {months} months"

        report = f"""
================================================================================
🎯 REDDIT USER PERSONA ANALYSIS
================================================================================
📌 Username:             u/{username}
📌 Analysis Date:        {datetime.now().isoformat()}
📌 Posts Analyzed:       {len(user_data['posts'])}
📌 Comments Analyzed:    {len(user_data['comments'])}

----------------------------------------
👤 Core Demographics & Profile
----------------------------------------
"""
        user_profile = persona_data.get('userProfile', {})
        for key, data in user_profile.items():
            report += f"  * **{key.title()}**: {data.get('value')} [{data.get('confidence', 'N/A')[0]}] [Evidence]({data.get('citation')})\n"

        report += "\n## **Account Statistics**\n"
        report += f"  * **Member Since**: {created_date.strftime('%Y-%m-%d')} ({age_str})\n"
        report += f"  * **Comment Karma**: {profile.get('comment_karma', 0):,}\n"
        report += f"  * **Post Karma**: {profile.get('link_karma', 0):,}\n"
        report += f"  * **Premium Status**: {'Premium Member' if profile.get('is_gold') else 'Standard User'}\n"
        report += f"  * **Moderator**: {'Yes' if profile.get('is_mod') else 'No'}\n"
        report += f"  * **Email Status**: {'Verified' if profile.get('has_verified_email') else 'Unverified'}\n"

        report += "\n----------------------------------------\n"
        report += "🧠 Psychographics & Behavior\n"
        report += "----------------------------------------\n"
        
        behavioral_traits = persona_data.get('behavioralTraits', [])
        for item in behavioral_traits:
            report += f"  * **{item.get('trait')}**: {item.get('value')} [{item.get('confidence', 'N/A')[0]}] (Evidence: {item.get('evidence')}) [Source]({item.get('citation')})\n"
        
        motivations = persona_data.get('motivationsAndValues', {})
        if motivations:
            report += "\n## **Key Motivations & Values**\n"
            primary = motivations.get('primaryMotivation', {})
            secondary = motivations.get('secondaryMotivation', {})
            value_system = motivations.get('valueSystem', {})

            if primary:
                report += f"  * **Primary Motivation**: {primary.get('value')} [{primary.get('confidence', 'N/A')[0]}] [Source]({primary.get('citation')})\n"
                report += f"    + **Marketing Angle**: {primary.get('marketingAngle')}\n"
            if secondary:
                report += f"  * **Secondary Motivation**: {secondary.get('value')} [{secondary.get('confidence', 'N/A')[0]}] [Source]({secondary.get('citation')})\n"
                report += f"    + **Marketing Angle**: {secondary.get('marketingAngle')}\n"
            if value_system:
                report += f"  * **Value System**: {value_system.get('value')} [{value_system.get('confidence', 'N/A')[0]}] [Source]({value_system.get('citation')})\n"

        personality = persona_data.get('personalityInsights', {})
        if personality:
            report += "\n## **Personality Insights**\n"
            for key, data in personality.items():
                if 'score' in data:
                    report += f"  * **{key.title()}**: {data.get('score')}/10 [{data.get('confidence', 'N/A')[0]}] [Source]({data.get('citation')})\n"
                    if 'marketingImpact' in data:
                        report += f"    + **Marketing Impact**: {data.get('marketingImpact')}\n"

        for section_name, section_key, item_key in [("Behavior & Habits", "behaviors", "value"), ("Goals & Needs", "goals", "value"), ("Frustrations", "frustrations", "value")]:
            data_list = persona_data.get(section_key, [])
            if data_list:
                report += f"\n## **{section_name}**\n"
                for item in data_list:
                    report += f"  * {item.get(item_key)} [{item.get('confidence', 'N/A')[0]}] [Source]({item.get('citation')})\n"
        
        report += "\n================================================================================\n"
        report += "Generated by Reddit Persona Analyzer v3.0\n"
        report += "Note: All insights are based on public Reddit activity analysis\n"
            
        return report


def main():
    """Main function to run the analyzer from the command line."""
    import sys
    if len(sys.argv) != 2:
        print("Usage: python reddit_persona_analyzer.py <reddit_profile_url>")
        sys.exit(1)

    profile_url = sys.argv[1]
    try:
        analyzer = RedditPersonaAnalyzer()
        username = analyzer.extract_username_from_url(profile_url)
        user_data = analyzer.get_user_activity(username, post_limit=30, comment_limit=50)
        persona_data = analyzer.analyze_user_persona(user_data)
        
        if "error" in persona_data:
            print(f"❌ Error generating persona: {persona_data['error']}")
            sys.exit(1)

        card_path = analyzer.generate_persona_card(persona_data, user_data)
        print(f"\n✅ Analysis complete for {username}!")
        print(f"Persona card saved to: {card_path}")

    except Exception as e:
        print(f"❌ An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
