import yt_dlp
from datetime import datetime

# 🔹 FUNCTIONS
def calculate_score(product):
    views = product["views"] / 10000
    likes = product["likes"] / 1000
    return (views * 0.4) + (likes * 0.3)


def clean_link(url):
    return url.split("?")[0]


def get_tiktok_data(url):
    with yt_dlp.YoutubeDL() as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "views": info.get("view_count", 0),
            "likes": info.get("like_count", 0),
            "description": info.get("description", "")
        }


#  SEASON DETECTION
def get_season():
    month = datetime.now().month

    if month in [12, 1, 2]:
        return "winter"
    elif month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    else:
        return "autumn"


#  SEASONAL SCORE
def seasonal_score(text):
    season = get_season()
    t = text.lower()

    keywords = {
        "summer": ["fan", "cooler", "ice", "water", "bottle", "outdoor"],
        "winter": ["heater", "warm", "blanket", "coat"],
        "spring": ["clean", "organize", "fresh", "garden"],
        "autumn": ["school", "desk", "office", "study"]
    }

    score = 0

    if season in keywords:
        for word in keywords[season]:
            if word in t:
                score += 25

    return score


# 🔹 PERFORMANCE SIGNAL
def product_signal_score(product):
    score = 0
    if product["views"] > 500_000:
        score += 20
    if product["views"] > 1_000_000:
        score += 20
    if product["likes"] > 50_000:
        score += 20
    return score


# 🔹 PRODUCT TYPE BOOST
def product_type_boost(text):
    keywords = [
        "sealer", "cleaner", "charger", "organizer",
        "kitchen", "pet", "baby", "car", "beauty",
        "tool", "device", "gadget", "bottle", "mixer"
    ]

    score = 0
    for word in keywords:
        if word in text.lower():
            score += 20

    return score


def non_product_penalty(text):
    bad = ["watch", "oddly", "cant stop", "can't stop", "won't stop"]
    return -40 if any(word in text.lower() for word in bad) else 0


def buying_intent_score(text):
    keywords = ["link in bio", "buy now", "shop now", "get yours"]

    score = 0
    for word in keywords:
        if word in text.lower():
            score += 40

    return score


def classify_product(text):
    t = text.lower()

    if any(word in t for word in ["link in bio", "buy now", "shop now"]):
        return "strong"

    if any(word in t for word in ["gadget", "tool", "device", "kitchen", "mixer"]):
        return "weak"

    return "none"


def engagement_score(product):
    if product["views"] == 0:
        return 0

    ratio = product["likes"] / product["views"]

    if ratio > 0.08:
        return 40
    elif ratio > 0.05:
        return 25
    elif ratio > 0.03:
        return 10
    return -20


def viral_boost(product):
    v = product["views"]

    if v > 2_000_000:
        return 50
    elif v > 1_000_000:
        return 30
    elif v > 500_000:
        return 15
    return 0


def problem_intensity(text):
    score = 0

    for w in ["fix", "solve", "problem"]:
        if w in text.lower():
            score += 20

    for w in ["easy", "better", "clean"]:
        if w in text.lower():
            score += 10

    return score


def aesthetic_score(text):
    keywords = ["satisfying", "cool", "aesthetic", "nice"]
    return sum(10 for word in keywords if word in text.lower())


#  MONEY MODE
def estimate_profit(product):
    if product["views"] > 1_000_000:
        return "HIGH"
    elif product["views"] > 300_000:
        return "MEDIUM"
    return "LOW"


def estimate_competition(product):
    if product["views"] > 1_000_000:
        return "HIGH"
    elif product["views"] > 300_000:
        return "MEDIUM"
    return "LOW"


def final_verdict(score):
    if score > 120:
        return "SELL THIS"
    elif score > 40:
        return "TEST"
    return "SKIP"


def confidence_score(score):
    if score > 150:
        return 95
    elif score > 120:
        return 90
    elif score > 80:
        return 75
    elif score > 40:
        return 60
    else:
        return 30


# 🔹 LOAD LINKS
def load_links():
    with open("links.txt", "r") as file:
        links = [clean_link(line.strip()) for line in file if line.strip()]
    return list(set(links))


# 🔹 MAIN SYSTEM
links = load_links()
results = []

for link in links:
    try:
        data = get_tiktok_data(link)

        product = {
            "name": data["description"][:40],
            "views": data["views"],
            "likes": data["likes"],
            "text": data["description"]
        }

        category = classify_product(product["text"])

        if category == "none":
            score = 0

        elif category == "weak":
            score = (
                calculate_score(product)
                + product_signal_score(product)
                + problem_intensity(product["text"])
                + engagement_score(product)
                + viral_boost(product)
                + aesthetic_score(product["text"])
                + product_type_boost(product["text"])
                + seasonal_score(product["text"])   #  NEW
                + non_product_penalty(product["text"])
            ) * 0.5

        else:
            score = (
                calculate_score(product)
                + product_signal_score(product)
                + problem_intensity(product["text"])
                + engagement_score(product)
                + viral_boost(product)
                + aesthetic_score(product["text"])
                + product_type_boost(product["text"])
                + seasonal_score(product["text"])   #  NEW
                + non_product_penalty(product["text"])
                + buying_intent_score(product["text"])
            )

        profit = estimate_profit(product)
        competition = estimate_competition(product)
        verdict = final_verdict(score)
        confidence = confidence_score(score)

        results.append({
            "name": product["name"],
            "score": round(score, 2),
            "profit": profit,
            "competition": competition,
            "verdict": verdict,
            "confidence": confidence
        })

    except:
        continue


# SORT
results = sorted(results, key=lambda x: x["score"], reverse=True)

import pandas as pd

df = pd.DataFrame(results)
df.to_csv("results.csv", index=False)


# 🟢 WINNERS
print("\n========== WINNERS ==========\n")
for r in results:
    if r["verdict"] == "SELL THIS":
        print(f"{r['name']}")
        print(f"Score: {r['score']} | Confidence: {r['confidence']}%")
        print(f"Profit: {r['profit']} | Competition: {r['competition']}")
        print("-" * 40)


# 🟡 TEST
print("\n========== TEST ==========\n")
for r in results:
    if r["verdict"] == "TEST":
        print(f"{r['name']}")
        print(f"Score: {r['score']} | Confidence: {r['confidence']}%")
        print(f"Profit: {r['profit']} | Competition: {r['competition']}")
        print("-" * 40)


# 🔴 SKIP
print("\n========== SKIP ==========\n")
for r in results:
    if r["verdict"] == "SKIP":
        print(f"{r['name']} (Score: {r['score']})")