import feedparser


def get_news_rss(animal_name:str):
    """Get relevant news from RSS feeds."""

    animal_name = animal_name.replace(" ", "-")

    feeds = [
        f'https://news.google.com/rss/search?q={animal_name}+conservation',
        
    ]
    
    news_items = []
    for feed_url in feeds:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:5]:
                news_items.append({
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.published
                })
        except Exception:
            
            return "No Mentions In Recent News"

    return news_items


if __name__ == "__main__":

    print(get_news_rss("Red Panda"))