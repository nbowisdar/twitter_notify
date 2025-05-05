import re


async def get_command_args(message):
    command_args = message.text.split(maxsplit=1)
    if len(command_args) < 2:
        return await message.answer(
            "Please provide a proxy (e.g., /add_proxy dawdf:aawoa8ju8213)."
        )
    return command_args[1].strip()


def extract_username(url: str) -> str:
    """
    Extract the username from an X profile URL.

    Args:
        url (str): The X profile URL (e.g., https://x.com/elonmusk?lang=uk)

    Returns:
        str: The username (e.g., elonmusk), or empty string if not found
    """
    pattern = r"https?://(?:www\.)?x\.com/([a-zA-Z0-9_]+)"
    match = re.match(pattern, url)
    return match.group(1) if match else ""


# async def check_if_user_exists(db, username):
#     command_args = message.text.split(maxsplit=1)
#     if len(command_args) < 2:
#         return await message.answer(
#             "Please provide a proxy (e.g., /add_proxy dawdf:aawoa8ju8213)."
#         )
#     return command_args[1].strip()

# Example usage
if __name__ == "__main__":
    url = "https://x.com/elonmusk?lang=uk"
    username = extract_username(url)
    print(f"Username: {username}")  # Output: Username: elonmusk
