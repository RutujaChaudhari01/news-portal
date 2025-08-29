from flask import Flask, render_template, request, redirect, url_for, session
import requests
from textblob import TextBlob
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)
app.secret_key = "supersecretkey"

API_KEY = "1c2e9d99d0144969ad957d5e9ea792ea"

COUNTRIES = {
    "global": "Global",
    "us": "United States",
    "gb": "United Kingdom",
    "in": "India",
    "ca": "Canada",
    "au": "Australia",
    "fr": "France",
    "de": "Germany",
    "jp": "Japan",
    "br": "Brazil",
    "za": "South Africa"
}

CATEGORY_MAP = {
    "general": "News",
    "business": "Business",
    "technology": "Technology",
    "sports": "Sports",
    "entertainment": "Entertainment",
    "health": "Health",
    "science": "Science"
}

# ------------------ DB FUNCTIONS ------------------
def init_db():
    conn = sqlite3.connect("news.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            source TEXT,
            country TEXT,
            category TEXT,
            publishedAt TEXT,
            positive INT,
            neutral INT,
            negative INT
        )
    """)
    conn.commit()
    conn.close()

def save_articles(news_articles, country, category):
    conn = sqlite3.connect("news.db")
    c = conn.cursor()
    for a in news_articles:
        c.execute("""
            INSERT INTO articles (title, description, source, country, category, publishedAt, positive, neutral, negative)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            a["title"], a["description"], a["source"], country, category, a["publishedAt"],
            a["sentiments"]["positive"], a["sentiments"]["neutral"], a["sentiments"]["negative"]
        ))
    conn.commit()
    conn.close()

# ------------------ SENTIMENT ------------------
def analyze_sentiment(text: str):
    if not text:
        return {"positive": 0, "neutral": 100, "negative": 0}
    try:
        polarity = TextBlob(text).sentiment.polarity
    except Exception:
        polarity = 0.0
    pos = max(0.0, polarity) * 100.0
    neg = max(0.0, -polarity) * 100.0
    neu = 100.0 - (pos + neg)
    pos_i, neg_i, neu_i = int(round(pos)), int(round(neg)), int(round(neu))
    total = pos_i + neg_i + neu_i
    if total != 100:
        neu_i += (100 - total)
    return {"positive": pos_i, "neutral": neu_i, "negative": neg_i}

# ------------------ ROUTES ------------------
@app.route("/")
def root():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == "admin" and password == "admin":
            session["user"] = username
            return redirect(url_for("home"))
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/home", methods=["GET", "POST"])
def home():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        country = request.form.get("country", "us")
        category = request.form.get("category", "general")
        keyword = request.form.get("keyword", "").strip()
    else:
        country = request.args.get("country", "us")
        category = request.args.get("category", "general")
        keyword = request.args.get("keyword", "").strip()

    news_articles, error_msg = [], None

    try:
        # Build query for everything endpoint
        query_parts = [CATEGORY_MAP.get(category, "News")]
        if keyword:
            query_parts.append(keyword)
        if country != "global":
            query_parts.append(COUNTRIES.get(country, ""))
        query = " ".join(query_parts).strip()

        url = f"https://newsapi.org/v2/everything?q={requests.utils.requote_uri(query)}&language=en&sortBy=publishedAt&apiKey={API_KEY}"

        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") != "ok":
            error_msg = f"NewsAPI error: {data.get('message', 'unknown error')}"
        else:
            raw_articles = data.get("articles", [])[:15]
            for a in raw_articles:
                title = a.get("title") or ""
                desc = a.get("description") or ""
                text = f"{title} {desc}".strip()
                sentiments = analyze_sentiment(text)
                article = {
                    "title": title,
                    "description": desc,
                    "url": a.get("url"),
                    "urlToImage": a.get("urlToImage"),
                    "source": a.get("source", {}).get("name", "Unknown"),
                    "publishedAt": a.get("publishedAt", "")[:10],
                    "sentiments": sentiments
                }
                news_articles.append(article)

            if news_articles:
                save_articles(news_articles, country, category)

    except requests.exceptions.RequestException as e:
        error_msg = f"Could not fetch news: {e}"

    if not news_articles and not error_msg:
        error_msg = "No articles found for the selected filters."

    return render_template(
        "index.html",
        news=news_articles,
        country=country,
        category=category,
        countries=COUNTRIES,
        category_map=CATEGORY_MAP,  # ✅ important
        error=error_msg,
        user=session["user"]
    )

# ------------------ Analytics ------------------
@app.route("/analytics")
def analytics():
    conn = sqlite3.connect("news.db")
    df = pd.read_sql_query("SELECT * FROM articles", conn)
    conn.close()
    if df.empty:
        return "<h3>No data available yet. Please fetch some news first.</h3>"

    charts = {}
    sentiment_counts = df[["positive","neutral","negative"]].mean()
    fig1, ax1 = plt.subplots()
    ax1.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%')
    buf1 = BytesIO()
    plt.savefig(buf1, format="png")
    buf1.seek(0)
    charts["sentiment"] = base64.b64encode(buf1.read()).decode("utf-8")
    plt.close(fig1)

    category_counts = df["category"].value_counts()
    fig2, ax2 = plt.subplots()
    category_counts.plot(kind="bar", ax=ax2)
    buf2 = BytesIO()
    plt.savefig(buf2, format="png")
    buf2.seek(0)
    charts["category"] = base64.b64encode(buf2.read()).decode("utf-8")
    plt.close(fig2)

    source_counts = df["source"].value_counts().head(10)
    fig3, ax3 = plt.subplots()
    source_counts.plot(kind="bar", ax=ax3)
    buf3 = BytesIO()
    plt.savefig(buf3, format="png")
    buf3.seek(0)
    charts["source"] = base64.b64encode(buf3.read()).decode("utf-8")
    plt.close(fig3)

    return render_template("analytics.html", charts=charts)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
