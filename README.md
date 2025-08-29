📰 News Portal

A Flask-based web application that fetches and displays news articles from various regions and categories using the News API. It also provides sentiment analysis and analytics visualization to help users understand the tone of news content.


📖 Table of Contents

Overview
Features
Tech Stack
Project Structure
Setup Instructions
Usage
Screenshots
Future Enhancements

📌 Overview

The News Portal project is designed to provide users with up-to-date news articles filtered by region, category, or keyword. It includes user authentication (login/logout), sentiment analysis of articles (positive, negative, neutral), and an analytics dashboard to visualize trends.


✨ Features

User Login/Logout Authentication
Fetch latest news from NewsAPI
Filter news by Region, Category, or Keyword
Sentiment Analysis of news articles
Analytics Dashboard with visual charts
Responsive UI with clean design


🛠 Tech Stack

Backend: Flask (Python)
Frontend: HTML
Database: SQLite (for user authentication)
Visualization: Chart.js / Matplotlib
Other Tools:
Requests (for API calls)
TextBlob (for sentiment analysis)
Git & GitHub (for version control)


Project Structure
news_portal/
│
├── app.py                # Main Flask application
|
├── requirements.txt      # Python dependencies
|
├── README.md             # Project documentation
|
├── templates/            # HTML templates
|   |
│   ├── index.html        # Homepage
|   |
│   ├── login.html        # Login page
|   |
│   ├── analytics.html    # Analytics dashboard
│
└── instance/             # Database and config (auto-created)
    |
    └── users.db


Setup Instructions

1.Clone the repository
git clone https://github.com/YourUsername/news-portal.git
cd news-portal

2.Create a virtual environment
python -m venv venv
source venv/bin/activate     # for Mac/Linux  
venv\Scripts\activate        # for Windows

3.Install dependencies
pip install -r requirements.txt

4.Run the Flask app
python app.py

5.Open in browser
http://127.0.0.1:5000


▶️ Usage

Login with your credentials.
Select Region / Category / Keyword to fetch news.
View news with sentiment bars.
Open Analytics Page to see trends and sentiment distribution.


🚀 Future Enhancements

Add multi-language support for news
Improve UI/UX with Bootstrap/Tailwind
More advanced analytics (trending topics, keyword clouds)
User notifications for breaking news
Save favorite articles for later


👩‍💻 Author

Rutuja Chaudhari




