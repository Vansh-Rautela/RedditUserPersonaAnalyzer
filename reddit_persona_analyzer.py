#!/usr/bin/env python3
"""
Reddit User Persona Analyzer
A comprehensive tool to analyze Reddit user profiles and generate detailed personas with citations.
"""

import os
import json
import re
from datetime import datetime
from urllib.parse import urlparse
from typing import Dict, List, Tuple, Optional
import praw
from groq import Groq
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RedditPersonaAnalyzer:
    """
    A comprehensive Reddit user persona analyzer that scrapes user activity
    and generates detailed personas with citations.
    """

    def __init__(self):
        """Initialize the analyzer with Reddit and Groq API clients."""
        load_dotenv('config.env')

        # Initialize Reddit API
        self.reddit = praw.Reddit(
            client_id=os.getenv("CLIENT_ID"),
            client_secret=os.getenv("CLIENT_SECRET"),
            user_agent=os.getenv("USER_AGENT")
        )

        # Initialize Groq LLM client
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        logger.info("Reddit Persona Analyzer initialized successfully")

    def extract_username_from_url(self, url: str) -> str:
        """
        Extract username from Reddit profile URL.

        Args:
            url (str): Reddit profile URL

        Returns:
            str: Extracted username
        """
        try:
            path = urlparse(url).path.strip("/")
            username = path.split("/")[-1]
            return username
        except Exception as e:
            logger.error(f"Error extracting username from URL {url}: {e}")
            raise ValueError(f"Invalid Reddit URL: {url}")

    def get_user_activity(
            self,
            username: str,
            post_limit: int = 30,
            comment_limit: int = 50) -> Dict:
        """
        Scrape user's posts and comments from Reddit.

        Args:
            username (str): Reddit username
            post_limit (int): Maximum number of posts to fetch
            comment_limit (int): Maximum number of comments to fetch

        Returns:
            Dict: User activity data including posts, comments, and profile info
        """
        try:
            user = self.reddit.redditor(username)

            # Get user profile information
            profile_info = {
                'username': username,
                'created_utc': user.created_utc,
                'comment_karma': user.comment_karma,
                'link_karma': user.link_karma,
                'is_gold': user.is_gold,
                'is_mod': user.is_mod,
                'has_verified_email': user.has_verified_email
            }

            # Get user's posts
            posts = []
            try:
                for submission in user.submissions.new(limit=post_limit):
                    post_data = {
                        'title': submission.title,
                        'selftext': submission.selftext,
                        'subreddit': submission.subreddit.display_name,
                        'score': submission.score,
                        'created_utc': submission.created_utc,
                        'url': submission.url,
                        'permalink': submission.permalink,
                        'num_comments': submission.num_comments,
                        'upvote_ratio': submission.upvote_ratio
                    }
                    posts.append(post_data)
            except Exception as e:
                logger.warning(f"Error fetching posts for {username}: {e}")

            # Get user's comments
            comments = []
            try:
                for comment in user.comments.new(limit=comment_limit):
                    comment_data = {
                        'body': comment.body,
                        'subreddit': comment.subreddit.display_name,
                        'score': comment.score,
                        'created_utc': comment.created_utc,
                        'permalink': comment.permalink,
                        'parent_id': comment.parent_id
                    }
                    comments.append(comment_data)
            except Exception as e:
                logger.warning(f"Error fetching comments for {username}: {e}")

            return {
                'profile': profile_info,
                'posts': posts,
                'comments': comments
            }

        except Exception as e:
            logger.error(f"Error fetching user activity for {username}: {e}")
            raise

    def analyze_user_persona(self, user_data: Dict) -> Dict:
        """
        Analyze user data and generate a comprehensive persona using Groq LLM.

        Args:
            user_data (Dict): User activity data

        Returns:
            Dict: Generated persona with characteristics and citations
        """
        try:
            # Prepare data for LLM analysis
            analysis_data = {
                'profile': user_data['profile'],
                # Further limit for token efficiency
                'posts': user_data['posts'][:5],
                # Further limit for token efficiency
                'comments': user_data['comments'][:10]
            }

            # Create prompt for persona generation
            prompt = self._create_persona_prompt(analysis_data)

            # Generate persona using Groq
            response = self.groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert user persona analyst. Analyze Reddit user data and create detailed personas with specific citations from their posts and comments."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=4000
            )

            # Parse the response
            persona_text = response.choices[0].message.content

            # Extract structured persona data
            persona_data = self._parse_persona_response(
                persona_text, user_data)

            return persona_data

        except Exception as e:
            logger.error(f"Error analyzing user persona: {e}")
            raise

    def _create_persona_prompt(self, user_data: Dict) -> str:
        """
        Create a comprehensive prompt for persona generation.

        Args:
            user_data (Dict): User activity data

        Returns:
            str: Formatted prompt for LLM
        """
        profile = user_data['profile']
        posts = user_data['posts']
        comments = user_data['comments']

        # Calculate account age in years and months
        created_date = datetime.fromtimestamp(profile['created_utc'])
        now = datetime.now()
        age_delta = now - created_date
        years = age_delta.days // 365
        months = (age_delta.days % 365) // 30

        age_str = f"{years} year{'s' if years != 1 else ''}"
        if months > 0:
            age_str += f" {months} month{'s' if months != 1 else ''}"

        # Build compact summaries to reduce token count
        posts_trim = posts[:5]
        posts_summary = "\n".join([
            f"- {p['title'][:90]} ([link](https://www.reddit.com{p['permalink']}))" 
            for p in posts_trim
        ])
        comments_trim = comments[:10]
        comments_summary = "\n".join([
            f"- {c['body'][:90].replace('\n', ' ')} ([link](https://www.reddit.com{c['permalink']}))" 
            for c in comments_trim
        ])

        prompt = f"""
        You are an expert marketing analyst. Using the Reddit data provided, create a concise persona profile in Markdown.

        Guidelines:
        • Only include a field if you have high confidence backed by MULTIPLE citations.
        • Limit each section to a MAX of 3 bullet points.
        • Cite evidence inline as Markdown links: [text](full_reddit_url).
# 📊 User Persona: u/{profile['username']}

## 👤 User Profile
| Category | Details | Confidence | Evidence |
|----------|---------|------------|-----------|
| Age Range | (inferred) | H/M/L | [cite posts/comments] |
| Location | (inferred) | H/M/L | [cite posts/comments] |
| Occupation | (inferred) | H/M/L | [cite posts/comments] |
| Education | (inferred) | H/M/L | [cite posts/comments] |
| Life Stage | (inferred) | H/M/L | [cite posts/comments] |

## 📈 Account Statistics
- 🗓️ Member Since: {created_date.strftime('%Y-%m-%d')} ({age_str})
- 💬 Comment Karma: {profile['comment_karma']:,}
- 📝 Post Karma: {profile['link_karma']:,}
- ⭐ Premium Status: {'Premium Member' if profile['is_gold'] else 'Standard User'}
- 🛡️ Moderator: {'Yes' if profile['is_mod'] else 'No'}
- ✉️ Email Status: {'Verified' if profile['has_verified_email'] else 'Unverified'}

## 🧠 Behavioral Traits
| Trait | Level | Evidence | Marketing Implications |
|-------|-------|----------|---------------------|
| Digital Literacy | 🟢🟡⚪ | [cite] | How to reach them |
| Brand Loyalty | 🟢🟡⚪ | [cite] | Retention strategy |
| Price Sensitivity | 🟢🟡⚪ | [cite] | Pricing approach |
| Early Adoption | 🟢🟡⚪ | [cite] | Product launches |
| Social Influence | 🟢🟡⚪ | [cite] | Advocacy potential |

## 🎯 Key Motivations & Values
Each motivation includes specific evidence and marketing implications:

1. Primary Motivations (with evidence):
   - 🥇 [Primary motivation] [H/M/L]
     * Evidence: [cite posts/comments]
     * Marketing Angle: [specific approach]

2. Secondary Motivations:
   - 🥈 [Secondary motivation] [H/M/L]
     * Evidence: [cite posts/comments]
     * Marketing Angle: [specific approach]

3. Value System:
   - 💎 Core Values: [list with evidence]
   - 🚫 Pain Points: [list with evidence]
   - 🌟 Aspirations: [list with evidence]

## 🎭 Personality Insights
### Big Five Analysis (with evidence)
1. 📊 Openness: [0-10] [H/M/L]
   * Evidence: [cite specific examples]
   * Marketing Impact: [specific strategies]

2. 📈 Conscientiousness: [0-10] [H/M/L]
   * Evidence: [cite specific examples]
   * Marketing Impact: [specific strategies]

3. 🤝 Extraversion: [0-10] [H/M/L]
   * Evidence: [cite specific examples]
   * Marketing Impact: [specific strategies]

4. 🤲 Agreeableness: [0-10] [H/M/L]
   * Evidence: [cite specific examples]
   * Marketing Impact: [specific strategies]

5. 🎯 Neuroticism: [0-10] [H/M/L]
   * Evidence: [cite specific examples]
   * Marketing Impact: [specific strategies]

## Behaviour & Habits
- Bullet points with evidence and [Reddit post/comment](https://reddit.com/...) hyperlinks for each.

## Frustrations
- Bullet points with evidence and [Reddit post/comment](https://reddit.com/...) hyperlinks for each.

## Goals & Needs
- Bullet points with evidence and [Reddit post/comment](https://reddit.com/...) hyperlinks for each.

---

USER POSTS (summary):
{posts_summary}

USER COMMENTS (summary):
{comments_summary}

---
**For every claim, provide a direct citation as a Markdown hyperlink to the relevant Reddit post or comment. Use clear, concise language and organize the persona visually as above. If you cannot infer a section, leave it blank but keep the heading.**
"""

        return prompt

    def _parse_persona_response(
            self,
            response_text: str,
            user_data: Dict) -> Dict:
        """
        Parse the LLM response and structure the persona data.

        Args:
            response_text (str): Raw LLM response
            user_data (Dict): Original user data for reference

        Returns:
            Dict: Structured persona data with raw text and metadata
        """
        try:
            # Store the raw response text
            persona_data = {
                'raw_analysis': response_text,
                'metadata': {
                    'analysis_date': datetime.now().isoformat(),
                    'username': user_data['profile']['username'],
                    'posts_analyzed': len(user_data['posts']),
                    'comments_analyzed': len(user_data['comments'])
                }
            }

            return persona_data

        except Exception as e:
            logger.error(f"Error parsing persona response: {e}")
            # Return a basic structure if parsing fails
            return {
                'error': 'Failed to parse persona response',
                'raw_response': response_text,
                'metadata': {
                    'analysis_date': datetime.now().isoformat(),
                    'username': user_data['profile']['username']
                }
            }

    def _extract_persona_from_text(self, text: str) -> Dict:
        """
        Extract persona information from unstructured text response.

        Args:
            text (str): Raw text response

        Returns:
            Dict: Structured persona data
        """
        # This is a fallback method to extract information from text
        # In a production environment, you might want to use more sophisticated
        # parsing

        sections = {
            'demographics': [],
            'psychology': [],
            'online_behavior': [],
            'expertise': [],
            'social_dynamics': []
        }

        # Simple keyword-based extraction
        lines = text.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()
            if 'demographic' in line.lower():
                current_section = 'demographics'
            elif 'psycholog' in line.lower():
                current_section = 'psychology'
            elif 'online' in line.lower() or 'behavior' in line.lower():
                current_section = 'online_behavior'
            elif 'expertise' in line.lower() or 'knowledge' in line.lower():
                current_section = 'expertise'
            elif 'social' in line.lower():
                current_section = 'social_dynamics'
            elif line and current_section:
                # Extract trait information
                if ':' in line or '-' in line:
                    sections[current_section].append({
                        'trait': line.split(':')[0].strip() if ':' in line else line.split('-')[0].strip(),
                        'value': line.split(':')[1].strip() if ':' in line else line.split('-')[1].strip() if '-' in line else line,
                        'citation': 'Extracted from text analysis',
                        'confidence': 'Medium'
                    })

        return sections

    def generate_persona_report(
            self,
            persona_data: Dict,
            username: str) -> str:
        """
        Generate a formatted text report from persona data with enhanced readability.

        Args:
            persona_data (Dict): Structured persona data
            username (str): Reddit username

        Returns:
            str: Formatted persona report with improved visual structure
        """
        def create_section_header(title: str) -> str:
            """Create a visually distinct section header."""
            return f"\n{'=' * 80}\n{title}\n{'=' * 80}\n"

        def create_subsection(title: str) -> str:
            """Create a visually distinct subsection header."""
            return f"\n{'-' * 40}\n{title}\n{'-' * 40}\n"

        def format_key_value(key: str, value: str) -> str:
            """Format key-value pairs consistently."""
            return f"📌 {key:<25} {value}"

        def format_list_item(item: str) -> str:
            """Format list items consistently."""
            return f"• {item}"

        def format_confidence(level: str) -> str:
            """Format confidence levels with visual indicators."""
            indicators = {
                'High': '🟢',
                'Medium': '🟡',
                'Low': '🔴'
            }
            return f"{indicators.get(level, '⚪')} {level} Confidence"

        # Build the report
        sections = []

        # Header Section
        header = create_section_header("🎯 REDDIT USER PERSONA ANALYSIS")
        meta_info = [
            format_key_value(
                "Username", f"u/{username}"), format_key_value(
                "Analysis Date", persona_data.get(
                    'metadata', {}).get(
                    'analysis_date', 'Unknown')), format_key_value(
                        "Posts Analyzed", str(
                            persona_data.get(
                                'metadata', {}).get(
                                    'posts_analyzed', 'Unknown'))), format_key_value(
                                        "Comments Analyzed", str(
                                            persona_data.get(
                                                'metadata', {}).get(
                                                    'comments_analyzed', 'Unknown')))]
        sections.append(header + "\n".join(meta_info))

        # Executive Summary
        if 'raw_analysis' in persona_data:
            analysis_text = persona_data['raw_analysis']

            # Core Demographics
            sections.append(create_subsection("👤 Core Demographics"))
            demographics = self._extract_section(analysis_text, "Demographics")
            sections.append(self._format_section_content(demographics))

            # Psychographic Profile
            sections.append(create_subsection("🧠 Psychographic Profile"))
            psychographics = self._extract_section(
                analysis_text, "Psychographic")
            sections.append(self._format_section_content(psychographics))

            # Behavior Patterns
            sections.append(create_subsection("🔄 Behavior Patterns"))
            behavior = self._extract_section(analysis_text, "Behavior")
            sections.append(self._format_section_content(behavior))

            # Key Insights (Check if already included in previous sections)
            if not any("Key Insights" in section for section in sections):
                sections.append(create_subsection("💡 Key Insights"))
                insights = self._extract_section(analysis_text, "Insights")
                sections.append(self._format_section_content(insights))

        elif 'error' in persona_data:
            sections.append(create_subsection("⚠️ Analysis Error"))
            sections.append(f"Error: {persona_data['error']}")
            if 'raw_response' in persona_data:
                sections.append("\nRaw Response:")
                sections.append(persona_data['raw_response'])

        # Footer
        footer = "\n" + "=" * 80 + "\n"
        footer += "Generated by Reddit Persona Analyzer v2.0\n"
        footer += "Note: All insights are based on public Reddit activity analysis\n"
        sections.append(footer)

        return "\n".join(sections)

    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract a specific section from the analysis text."""
        pattern = rf"(?i).*{section_name}.*?(?=\n=|\n-|\Z)"
        match = re.search(pattern, text, re.DOTALL)
        return match.group(0) if match else ""

    def _format_section_content(self, content: str) -> str:
        """Format section content with proper indentation and styling."""
        lines = content.split('\n')
        formatted_lines = []
        for line in lines:
            line = line.strip()
            if line:
                if line.startswith(('•', '-', '*')):
                    formatted_lines.append(f"  {line}")
                elif ':' in line:
                    key, value = line.split(':', 1)
                    formatted_lines.append(f"📌 {key.strip()}: {value.strip()}")
                else:
                    formatted_lines.append(line)
        return "\n".join(formatted_lines)

    def save_persona_report(self, report: str, username: str) -> str:
        """
        Save the persona report to a text file in the personas folder.

        Args:
            report (str): Formatted persona report
            username (str): Reddit username

        Returns:
            str: Path to saved file
        """
        # Create personas folder if it doesn't exist
        personas_dir = "personas"
        if not os.path.exists(personas_dir):
            os.makedirs(personas_dir)

        filename = f"persona_{username}_{
            datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(personas_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)

        logger.info(f"Persona report saved to {filepath}")
        return filepath

    def generate_persona_card(self, persona_data: Dict, username: str) -> str:
        """
        Create a stylised persona card PNG similar to attached example (dark theme, multi-column layout).

        Args:
            persona_data (Dict): Persona information generated by the LLM.
            username (str): Reddit username.

        Returns:
            str: Path to the generated JPG image.
        """
        try:
            # Import locally to avoid mandatory dependency if the feature isn't
            # used elsewhere
            from PIL import Image, ImageDraw, ImageFont

            personas_dir = "personas"
            if not os.path.exists(personas_dir):
                os.makedirs(personas_dir)

            img_width, img_height = 1200, 1600
            bg_color = (255, 255, 255)
            image = Image.new("RGB", (img_width, img_height), color=bg_color)
            draw = ImageDraw.Draw(image)
            font = ImageFont.load_default()

            # Limit text length to fit into the image
            text = persona_data.get("raw_analysis", "")[:3500]

            margin, offset = 40, 40
            max_width = img_width - 2 * margin

            for paragraph in text.split("\n"):
                words = paragraph.split()
                current_line = ""
                for word in words:
                    test_line = f"{current_line} {word}".strip()
                    try:
                        bbox = draw.textbbox((0, 0), test_line, font=font)
                        w = bbox[2] - bbox[0]
                        h = bbox[3] - bbox[1]
                    except AttributeError:
                        # Fallback for older Pillow
                        w, h = font.getsize(test_line)
                    if w <= max_width:
                        current_line = test_line
                    else:
                        draw.text(
                            (margin, offset), current_line, fill=(
                                0, 0, 0), font=font)
                        offset += h + 4
                        current_line = word
                if current_line:
                    draw.text(
                        (margin, offset), current_line, fill=(
                            0, 0, 0), font=font)
                    offset += h + 4
                if offset > img_height - margin:
                    break  # Stop drawing if we exceed image height

            filename = f"persona_{username}_{
                datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            jpg_path = os.path.join(personas_dir, filename)
            image.save(jpg_path, "PNG")
            logger.info(f"Persona card saved to {jpg_path}")
            return jpg_path
        except Exception as e:
            logger.error(f"Error generating persona image: {e}")
            raise

    def analyze_user_from_url(self, profile_url: str) -> Tuple[str, str, str]:
        """
        Complete analysis pipeline from Reddit profile URL.

        Args:
            profile_url (str): Reddit profile URL

        Returns:
            Tuple[str, str, str]: (username, markdown_report_path, jpg_image_path)
        """
        try:
            # Extract username
            username = self.extract_username_from_url(profile_url)
            logger.info(f"Analyzing user: {username}")

            # Get user activity
            user_data = self.get_user_activity(username)
            logger.info(
                f"Retrieved {len(user_data['posts'])} posts and {len(user_data['comments'])} comments")

            # Generate persona
            persona_data = self.analyze_user_persona(user_data)
            logger.info("Persona analysis completed")

            # Generate report
            markdown_report = self.generate_persona_report(
                persona_data, username)
            md_path = self.save_persona_report(markdown_report, username)

            # Generate visual image of persona
            card_path = self.generate_persona_card(persona_data, username)

            return username, md_path, card_path

        except Exception as e:
            logger.error(f"Error in analysis pipeline: {e}")
            raise


def main():
    """Main function to run the Reddit persona analyzer."""
    import sys

    if len(sys.argv) != 2:
        print("Usage: python reddit_persona_analyzer.py <reddit_profile_url>")
        print(
            "Example: python reddit_persona_analyzer.py https://www.reddit.com/user/kojied/")
        sys.exit(1)

    profile_url = sys.argv[1]

    try:
        analyzer = RedditPersonaAnalyzer()
        username, output_file = analyzer.analyze_user_from_url(profile_url)

        print(f"\n✅ Analysis completed successfully!")
        print(f"Username: {username}")
        print(f"Output file: {output_file}")
        print(f"\nReport preview:")
        print("=" * 50)

        # Show first 20 lines of the report
        with open(output_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:20]
            print(''.join(lines))
            if len(f.readlines()) > 20:
                print("... (truncated)")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
