import re
import json
import os
import sys
import io
import uuid
import time
import requests
from pprint import pprint
import google.generativeai as genai
from datetime import datetime

# ✅ Set UTF-8 encoding for standard output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# ✅ Configure paths
INSERT_URL = "http://127.0.0.1:8000/api/insert_articles/"
HEADERS = {"Content-Type": "application/json"}

# ✅ Base directories
CONFIG_FILE = "./config.json"
DJANGO_API_URL = "http://127.0.0.1:8000/api/insert_articles/"

# ✅ Load API key
def load_api_key(config_file):
    try:
        with open(config_file, 'r', encoding='utf-8') as file:
            config = json.load(file)
            return config.get("api_key")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Error reading config file: {e}")
        return None

API_KEY = load_api_key(CONFIG_FILE)
if API_KEY is None:
    sys.exit("❌ API key is missing. Please check your config file.")

# ✅ Configure AI API
genai.configure(api_key=API_KEY)

# ✅ Find `MatchedNewsData-*` directories
def find_matched_news_dirs(base_dir):
    return [
        os.path.join(base_dir, d)
        for d in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, d)) and d.startswith("MatchedNewsData")
    ]

# ✅ Read JSON files
def read_json_files(directory):
    articles = []
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                json_data = json.load(file)
                articles.append(json_data)
    return articles

# ✅ AI Article Processing with Categorization
def process_articles_with_ai(articles):
    article_strings = [json.dumps(article, ensure_ascii=False, indent=4) for article in articles]
    articles_combined = "\n".join(article_strings)

    # ✅ AI Prompts for Summarization & Categorization
    title_prompt = "Bu haber makalelerine dayanarak, 3-4 kelimelik nesnel bir başlık oluşturun:"
    short_summary_prompt = "Bu haber makalelerine dayanarak, 10-50 karakter arasında kısa, betimleme içermeyen, salt bilgi içeren bir özet oluşturun:"
    detailed_summary_prompt = "Bu haber makalelerine dayanarak, detaylı ve salt bilgi içeren bir özet oluşturun:"
    category_prompt = """
    Bu haber makalesini aşağıdaki kategorilerden birine atayın:
    Siyaset
    Eğlence
    Spor
    Teknoloji
    Sağlık
    Çevre
    Bilim
    Eğitim
    Ekonomi
    Seyahat
    Moda
    Kültür
    Suç
    Yemek
    Yaşam Tarzı
    İş Dünyası
    Dünya Haberleri
    Oyun
    Otomotiv
    Sanat
    Tarih
    Uzay
    İlişkiler
    Din
    Ruh Sağlığı
    Magazin

    Eğer uygun bir kategori bulamazsan, 'Genel' olarak belirle. Bu kategorilerden başka hiçbir şey yazma.
    """

    # ✅ Initialize AI model
    model = genai.GenerativeModel('gemini-1.5-flash')

    time.sleep(5)  
    try:
        title_response = model.generate_content(f"{title_prompt}\n{articles_combined}")
        title = title_response.text.strip()
    except Exception as e:
        print(f"❌ Error generating title: {e}")
        title = "Title generation failed"

    time.sleep(5)
    try:
        short_summary_response = model.generate_content(f"{short_summary_prompt}\n{articles_combined}")
        short_summary = short_summary_response.text.strip()
    except Exception as e:
        print(f"❌ Error generating short summary: {e}")
        short_summary = "Short summary failed"

    time.sleep(5)
    try:
        detailed_summary_response = model.generate_content(f"{detailed_summary_prompt}\n{articles_combined}")
        detailed_summary = detailed_summary_response.text.strip()
    except Exception as e:
        print(f"❌ Error generating detailed summary: {e}")
        detailed_summary = "Detailed summary failed"

    time.sleep(5)
    try:
        category_response = model.generate_content(f"{category_prompt}\n{articles_combined}")
        category = category_response.text.strip()
    except Exception as e:
        print(f"❌ Error generating category: {e}")
        category = "Genel"  # Default to "General"

    # ✅ Generate Unique ID for the article
    article_id = str(uuid.uuid4())

    # ✅ Extract sources as a list
    sources = list(set([article.get("source", "Unknown") for article in articles if "source" in article]))

    # ✅ Create structured output with Category
    output = {
        "id": None,
        "articleId": article_id,
        "title": title,
        "content": "",
        "summary": short_summary,
        "longerSummary": detailed_summary,
        "category": category,  # ✅ Assign AI-generated category
        "tags": [],
        "source": sources,
        "location": None,
        "popularityScore": 0,
        "createdAt": None,
        "image": None,
        "priority": None
    }
    return output


# ✅ Save JSON output
def save_json_output(data):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"objectified_summary_{timestamp}.json"
    output_filepath = os.path.join(OUTPUT_DIR, output_filename)

    with open(output_filepath, 'w', encoding='utf-8') as output_file:
        json.dump(data, output_file, ensure_ascii=False, indent=4)

    print(f"✅ Output saved locally at {output_filepath}")
    return output_filepath

# ✅ Function to send JSON files one by one
def send_json_files():
    if not os.path.exists(JSON_DIR):
        print(f"❌ Directory not found: {JSON_DIR}")
        return
    
    json_files = [f for f in os.listdir(JSON_DIR) if f.endswith(".json")]
    
    if not json_files:
        print("❌ No JSON files found in objectified_jsons directory!")
        return

    print(f"🔍 Found {len(json_files)} objectified JSON files. Sending them to the backend...")

    for json_file in json_files:
        json_path = os.path.join(JSON_DIR, json_file)

        try:
            # ✅ Load JSON data
            with open(json_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            # ✅ Debugging - Print data before sending
            print(f"\n🔹 Sending file: {json_file} to backend...")
            print("📜 JSON Data (First 300 characters):", json.dumps(data, indent=2)[:300])

            # ✅ Send POST request
            response = requests.post(INSERT_URL, json=data, headers=HEADERS)
            response_json = response.json()

            # ✅ Debugging - Print server response
            print(f"📜 Backend Response (Status {response.status_code}): {response_json}")

            if response.status_code == 201:
                print(f"✅ Successfully sent {json_file}!")
            else:
                print(f"❌ Failed to send {json_file} (Server Response): {response.text}")

        except json.JSONDecodeError:
            print(f"❌ Error: Invalid JSON format in {json_file}. Skipping but NOT deleting it.")
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error while sending {json_file}: {str(e)}")
            print("⚠️ Keeping the JSON file for retry.")
        except Exception as e:
            print(f"❌ Unexpected error processing {json_file}: {str(e)}")

    print("✅ All objectified JSONs have been processed.")


# ✅ Main Function
def main():
    news_dirs = find_matched_news_dirs(BASE_DIR)

    if not news_dirs:
        print("❌ No `MatchedNewsData-*` directories found!")
        return

    print(f"🔍 Found {len(news_dirs)} directories to process.")

    # ✅ Delete old articles before inserting new ones
    print("🗑 Deleting old articles before inserting new ones...")
    try:
        requests.get("http://127.0.0.1:8000/api/delete_articles/")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error deleting old articles: {e}")

    for news_dir in news_dirs:
        print(f"📂 Processing: {news_dir}")
        articles = read_json_files(news_dir)

        if not articles:
            print(f"⚠️ No articles found in {news_dir}, skipping...")
            continue

        # ✅ Ensure no duplicate processing
        unique_titles = set()
        filtered_articles = []

        for article in articles:
            title = article.get("title", "").strip()
            if title and title not in unique_titles:
                unique_titles.add(title)
                filtered_articles.append(article)

        if not filtered_articles:
            print(f"⚠️ No new unique articles found in {news_dir}, skipping...")
            continue

        # ✅ AI Processing (COMMENT THIS IF NOT NEEDED)
        processed_data = process_articles_with_ai(filtered_articles)

        # ✅ Save locally
        save_json_output(processed_data)

        # Step 1: Send new JSON files **without deleting them unless uploaded successfully**
        send_json_files()

        print("✅ Process completed successfully!")

    print("✅ All directories processed successfully!")

# ✅ Run the script
if __name__ == "__main__":
    main()
