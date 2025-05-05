import asyncio
from datetime import date
from pprint import pprint

from twscrape import API, Tweet, gather

from bot.db import existing_user_ids, filter_new_tweets, save_new_tweets


class XParser:
    def __init__(self):
        self.api = API()
        self.interval_sec = 10

    def set_proxy(self, proxy: str):
        self.api = API(proxy=proxy)
        self.load_accounts()

    async def load_accounts(self):
        # Option 1. Adding account with cookies (more stable)
        # Combine ct0 and auth_token into cookies string
        auth_token = "d1ba29557718984d63a28b11cc8a64d887b1d293"
        ct0 = "4ae7e4f76c4995a24dc1bac6979ac979d800237505f6b25a8aa8712c7c4b191ab2eebb27a700acffc60e07afb43d8ec08d7c5ea029a556963d79d9fc9033688a89e7bcb6218a53906ed9caf7221371ec"
        cookies = f"ct0={ct0}; auth_token={auth_token}"
        await self.api.pool.add_account(
            "toleston44282",
            "MyNDmHeTRLi&1001",
            "ho3ymjuly@gmx.com",
            "nr6hztf8Me",
            cookies=cookies,
        )
        # try:
        #     print(ACCOUNTS_FILE)
        #     with open(ACCOUNTS_FILE, "r", encoding="utf-8") as file:
        #         for line in file:
        #             # Skip empty lines
        #             if not line.strip():
        #                 continue

        #             # Split line by colon
        #             parts = line.strip().split(":")
        #             if len(parts) < 6:
        #                 print(f"Skipping invalid account line: {line.strip()}")
        #                 continue

        #             # Extract account details
        #             username = parts[0]
        #             password = parts[1]
        #             email = parts[2]
        #             email_password = parts[3]
        #             ct0 = parts[4]
        #             auth_token = parts[5]

        #             # Combine ct0 and auth_token into cookies string
        #             cookies = f"ct0={ct0}; auth_token={auth_token}"

        #             # Add account to API pool
        #             await self.api.pool.add_account(
        #                 username=username,
        #                 password=password,
        #                 email=email,
        #                 email_password=email_password,
        #                 cookies=cookies,
        #             )
        # except FileNotFoundError:
        #     print(f"Account file not found: {ACCOUNTS_FILE}")
        # except Exception as e:
        #     print(f"Error loading accounts: {str(e)}")

    async def get_user_id_by_username(self, username: str):
        user = await self.api.user_by_login(username)
        if user:
            return user.id

    async def get_tweets(self, user_id, limit: int = 2) -> list[Tweet]:
        tweets = await gather(self.api.user_tweets(user_id, limit=limit))
        # Skip older tweets
        return [tweet for tweet in tweets if tweet.date.date() >= date.today()]


class XManager:
    def __init__(self, x_parser: XParser, interval_sec: int = 10):
        self.x_parser = x_parser
        self.interval_sec = interval_sec
        self.is_active = False
        self.on_new_tweet_cb = None

    def set_proxy(self, proxy: str):
        self.stop()
        self.x_parser.set_proxy(proxy)

    async def active(self):
        self.is_active = True
        await self.x_parser.load_accounts()
        await self.work()

    async def stop(self):
        self.is_active = False

    async def work(self):
        while self.is_active:
            for user_id in existing_user_ids():
                tweets = await self.x_parser.get_tweets(user_id)
                new_tweets = filter_new_tweets(tweets)
                save_new_tweets([t.id for t in new_tweets])
                if self.on_new_tweet_cb:
                    await self.on_new_tweet_cb(new_tweets)

            await asyncio.sleep(self.interval_sec)


async def main():
    x_parser = XParser()
    await x_parser.load_accounts()
    resp = await x_parser.get_tweets("1499077769740886018", limit=2)
    pprint(resp)


if __name__ == "__main__":
    asyncio.run(main())
