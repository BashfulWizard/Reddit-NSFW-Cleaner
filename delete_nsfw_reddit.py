"""
Reddit NSFW Full Cleaner v1.3
------------------------
Deletes all NSFW saved and upvoted posts/comments from your Reddit account.
Automatically repeats until nothing NSFW remains.

Author: Aidan Garcia
License: GNU GPLv3
"""

import praw
import traceback
import threading
import time
import sys
from tqdm import tqdm

# Replacing unicode symbols for Windows compatibility
OK = "[OK]"
WARN = "[WARN]"
SKIP = "[SKIP]"
DONE = "[DONE]"
ERR = "[ERR]"
ARROW = "->"

# Optional colors
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    class Fore:
        RED = ""
        GREEN = ""
        CYAN = ""
        YELLOW = ""
        MAGENTA = ""
    class Style:
        RESET_ALL = ""

# ------------------------------------------------------------
TIMEOUT_SECONDS = 20
LOG_FILE = "cleanup_log.txt"

# ------------------------------------------------------------
def log_error(message):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

def run_with_timeout(func, timeout, *args, **kwargs):
    """Run a function with timeout; skip if it takes too long."""
    result = [None]
    exception = [None]

    def target():
        try:
            result[0] = func(*args, **kwargs)
        except Exception as e:
            exception[0] = e

    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        tqdm.write(Fore.YELLOW + "{WARN} Operation timed out, skipping..." + Style.RESET_ALL)
        return False
    if exception[0]:
        raise exception[0]
    return True
    
def is_unmodifiable(item):
    """Return True if the Reddit post/comment can't be changed (e.g., archived)."""
    if isinstance(item, praw.models.Submission) and getattr(item, "archived", False):
        return True
    return False

def is_unfixable_error(e):
    """Return True if the error means the post can't be modified."""
    msg = str(e).lower()
    return (
        "400" in msg
        or "bad request" in msg
        or "archived" in msg
        or "not found" in msg
        or "forbidden" in msg
    )

# ------------------------------------------------------------
def connect_to_reddit():
    print(Fore.CYAN + "Connecting to Reddit API..." + Style.RESET_ALL)
    try:
        reddit = praw.Reddit(
            client_id="YOUR_CLIENT_ID",
            client_secret="YOUR_CLIENT_SECRET",
            user_agent="Reddit NSFW Cleaner v1.3 by u/awowwowa",
            username="YOUR_USERNAME",
            password="YOUR_PASSWORD"
        )
        print(Fore.GREEN + f"{OK} Connected as: {reddit.user.me()}" + Style.RESET_ALL)
        return reddit
    except Exception as e:
        print(Fore.RED + f"{ERR} Connection failed: {e}" + Style.RESET_ALL)
        log_error(traceback.format_exc())
        retry = input(Fore.YELLOW + "Retry connection? (y/n): ").strip().lower()
        if retry == "y":
            return connect_to_reddit()
        else:
            sys.exit(1)

# ------------------------------------------------------------
def cleanup_saved(reddit):
    total_deleted = 0
    while True:
        saved = list(reddit.user.me().saved(limit=None))
        nsfw_items = [p for p in saved if getattr(p, "over_18", False)]

        if not nsfw_items:
            break

        skipped_posts = []

        for item in tqdm(nsfw_items, desc="Saved NSFW posts", unit="post"):
            try:
                if is_unmodifiable(item):
                    tqdm.write(Fore.YELLOW + f"{SKIP} Skipping archived post: {getattr(item, 'title', '[no title]')}" + Style.RESET_ALL)
                    continue

                
                if isinstance(item, (praw.models.Submission, praw.models.Comment)):
                    success = run_with_timeout(item.unsave, TIMEOUT_SECONDS)
                    if success:
                        total_deleted += 1
                else:
                    skipped_posts.append(item)
                            
                            
            except Exception as e:
                if is_unfixable_error(e):
                    tqdm.write(Fore.YELLOW + f"{WARN} Skipping unmodifiable post: {getattr(item, 'title', '[no title]')}" + Style.RESET_ALL)
                    log_error(f"Unmodifiable: {getattr(item, 'title', '[no title]')} -> {e}")
                    continue
                else:
                    tqdm.write(Fore.RED + f"Error deleting saved: {e}" + Style.RESET_ALL)
                    log_error(traceback.format_exc())
                    skipped_posts.append(item)

        if not skipped_posts:
            break
            
            
            tqdm.write(Fore.YELLOW + f"Retrying {len(skipped_posts)} skipped saved posts..." + Style.RESET_ALL)
            

    print(Fore.GREEN + f"\n{OK} Deleted {total_deleted} NSFW saved posts/comments.\n" + Style.RESET_ALL)

# ------------------------------------------------------------
def cleanup_upvoted(reddit):
    total_deleted = 0
    while True:
        upvoted = list(reddit.user.me().upvoted(limit=None))
        nsfw_items = [p for p in upvoted if getattr(p, "over_18", False)]

        if not nsfw_items:
            break

        skipped_posts = []

        for item in tqdm(nsfw_items, desc="Upvoted NSFW posts", unit="post"):
            try:
                if is_unmodifiable(item):
                    tqdm.write(Fore.YELLOW + f"{SKIP} Skipping archived post: {getattr(item,'title', '[no title]')}" + Style.RESET_ALL)
                    continue

                if isinstance(item, (praw.models.Submission, praw.models.Comment)):
                    success = run_with_timeout(item.clear_vote, TIMEOUT_SECONDS)
                    if success:
                        total_deleted += 1
                    else:
                        skipped_posts.append(item)
                        
            except Exception as e:
                if is_unfixable_error(e):
                    tqdm.write(Fore.YELLOW + f"{WARN} Skipping unmodifiable post: {getattr(item, 'title', '[no title]')}" + Style.RESET_ALL)
                    log_error(f"Unmodifiable: {getattr(item, 'title', '[no title]')} -> {e}")
                    continue
                else:
                    tqdm.write(Fore.RED + f"Error clearing upvote: {e}" + Style.RESET_ALL)
                    log_error(traceback.format_exc())
                    skipped_posts.append(item)

        if not skipped_posts:
            break
            
            
            tqdm.write(Fore.YELLOW + f"Retrying {len(skipped_posts)} skipped upvoted posts..." + Style.RESET_ALL)

    print(Fore.GREEN + f"\n{OK} Cleared upvotes from {total_deleted} NSFW posts/comments.\n" + Style.RESET_ALL)

# ------------------------------------------------------------
def cleanup_downvoted(reddit):
    total_deleted = 0

    while True:
        downvoted = list(reddit.user.me().downvoted(limit=None))
        nsfw_items = [p for p in downvoted if getattr(p, "over_18", False)]

        if not nsfw_items:
            break

        skipped_posts = []

        for item in tqdm(nsfw_items, desc="Downvoted NSFW posts", unit="post"):
            try:
                if is_unmodifiable(item):
                    tqdm.write(Fore.YELLOW + f"{SKIP} Skipping archived post: {getattr(item, 'title', '[no title]')}" + Style.RESET_ALL)
                    continue

                
                if isinstance(item, (praw.models.Submission, praw.models.Comment)):
                    success = run_with_timeout(item.clear_vote, TIMEOUT_SECONDS)
                    if success:
                        total_deleted += 1
                    else:
                        skipped_posts.append(item)
            
            except Exception as e:
                if is_unfixable_error(e):
                    tqdm.write(Fore.YELLOW + f"{WARN} Skipping unmodifiable post: {getattr(item, 'title', '[no title]')}" + Style.RESET_ALL)
                    log_error(f"Unmodifiable: {getattr(item, 'title', '[no title]')} -> {e}")
                    continue  
                else:
                    tqdm.write(Fore.RED + f"Error clearing downvote: {e}" + Style.RESET_ALL)
                    log_error(traceback.format_exc())
                    skipped_posts.append(item)

        if not skipped_posts:
            break
            
            
        tqdm.write(Fore.YELLOW + f"Retrying {len(skipped_posts)} skipped downvoted posts..." + Style.RESET_ALL)
            

    print(Fore.GREEN + f"\n{OK} Cleared downvotes from {total_deleted} NSFW posts/comments.\n" + Style.RESET_ALL)
    
# ------------------------------------------------------------
if __name__ == "__main__":
    VERSION = "v1.3"
    print(Fore.MAGENTA + f"=== Reddit NSFW Full Cleaner {VERSION} ===\n" + Style.RESET_ALL)
    reddit = connect_to_reddit()

    choice = input(
    Fore.CYAN +
    "Select action:\n"
    "1. Delete saved NSFW posts/comments\n"
    "2. Remove upvotes from NSFW posts/comments\n"
    "3. Remove downvotes from NSFW posts/comments\n"
    "4. Do all three\n"
    "Choice: " + Style.RESET_ALL
).strip()

if choice in ["1", "4"]:
    cleanup_saved(reddit)
if choice in ["2", "4"]:
    cleanup_upvoted(reddit)
if choice in ["3", "4"]:
    cleanup_downvoted(reddit)

    print(Fore.MAGENTA + "\n[DONE] All done! Check cleanup_log.txt for errors if any.\n" + Style.RESET_ALL)
    input("Press Enter to exit...")
