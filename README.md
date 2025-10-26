# 🧹 Reddit NSFW Cleaner

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-GPLv3-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](#)

> A cross-platform Python tool that deletes all **NSFW saved** and/or **upvoted posts** from your Reddit account safely — with logging, progress tracking, and retry protection.

---

## 🚀 Features

- ✅ **Deletes saved and upvoted NSFW posts**
- ⚙️ **Cross-platform** — works on Windows, macOS, and Linux  
- 🧠 **Timeout system** using threads (no freezing on stuck posts)  
- 💬 **Interactive** — asks before retrying failed deletions  
- 🧾 **Error logging** to `cleanup_log.txt`  
- 📊 **Progress bars** using [`tqdm`](https://pypi.org/project/tqdm/)  
- 🎨 Optional **color output** with [`colorama`](https://pypi.org/project/colorama/)

---

## 📦 Installation

1. **Clone or download** this repository:
   ```bash
   git clone https://github.com/BashfulWizard/reddit-nsfw-cleaner.git
   cd reddit-nsfw-cleaner
   ```

2. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a Reddit App** (script type):
   - Visit: [https://www.reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
   - Click “**create another app…**”
   - Choose **script**
   - Add:
     - **name:** Reddit NSFW Cleaner  
     - **redirect uri:** `http://localhost:8080`
   - Copy your **client ID** and **client secret**

---

## ⚙️ Configuration

Open `delete_nsfw_reddit.py` and replace the placeholder values:

```python
reddit = praw.Reddit(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    user_agent="Reddit-NSFW-Cleaner by u/awowwowa",
    username="YOUR_USERNAME",
    password="YOUR_PASSWORD"
)
```

---

## ▶️ Usage

Run the script from a terminal:
```bash
python delete_nsfw_reddit.py
```

Then choose your action:
```
1. Delete saved NSFW posts
2. Remove upvotes from NSFW posts
3. Do both
```

---

## 🧾 Log File

All exceptions and timeouts are automatically saved to `cleanup_log.txt`:
```
[2025-10-25 20:31:04] prawcore.exceptions.Forbidden: received 403 HTTP response
[2025-10-25 20:32:11] Operation timed out, skipping...
```

---

## ⚖️ License

This project is licensed under the **GNU General Public License v3.0 (GPLv3)** — see the [LICENSE](LICENSE) file for details.

By using or modifying this software, you agree to:
- Keep the source code open and freely accessible.
- Distribute derivative works under the same license.
- Include attribution to the original author.

---

## 🙌 Credits

Created by **Aidan Garcia**  
A free and privacy-respecting cleanup tool for Reddit users.  

Special thanks to ChatGPT for saving a million headaches along the way

If you find this useful, consider giving the repo a ⭐ on GitHub!
