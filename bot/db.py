import orjson
from twscrape import Tweet

from bot.loader import DB_FILE


def get_db() -> dict:
    with open(DB_FILE, "rb") as f:
        return orjson.loads(f.read())


def save_db(data: dict):
    with open(DB_FILE, "wb") as f:
        f.write(orjson.dumps(data))


def existing_user_ids() -> list[str]:
    users = get_db().get("users", [])
    return [user_id for username, user_id in users.items()]


def existing_tweets() -> list[str]:
    return get_db().get("tweets", [])


def save_new_tweets(tweets_ids: list[str]) -> list[str]:
    data = get_db()
    data["tweets"] += tweets_ids
    save_db(data)


def filter_new_tweets(tweets: list[Tweet]) -> list[Tweet]:
    old_tweets = get_db().get("tweets", [])
    return [t for t in tweets if t.id not in old_tweets]
