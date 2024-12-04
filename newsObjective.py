import re
import json
import os
import sys
import io
from pprint import pprint
import google.generativeai as genai

# Set UTF-8 encoding for standard output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Directory containing the JSON articles
SAVE_DIR = "./articles"
OUTPUT_DIR = "./objectified_jsons"
CONFIG_FILE = "./config.json"

# Function to read the API key from the config file
def load_api_key(config_file):
    try:
        with open(config_file, 'r', encoding='utf-8') as file:
            config = json.load(file)
            return config.get("api_key")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading config file: {e}")
        return None

# Load the API key from the config file
API_KEY = load_api_key(CONFIG_FILE)
if API_KEY is None:
    sys.exit("API key is missing. Please check your config file.")

# Configure the API with the provided key
genai.configure(api_key=API_KEY)

# Function to read JSON files from a specified directory
def read_json_files(directory):
    articles = []
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                json_data = json.load(file)
                articles.append(json_data)
    return articles

# Read articles from JSON files
articles = read_json_files(SAVE_DIR)

# Print each article in a readable format using pprint
# for i, article in enumerate(articles):
#     print(f"Article {i + 1}:")
#     pprint(article, width=80)
#     print("\n" + "-" * 80 + "\n")

# Format the articles into a single string for the prompt
article_strings = [json.dumps(article, ensure_ascii=False, indent=4) for article in articles]

# Combine the articles into one input string for summarization
articles_combined = "\n".join(article_strings)

# Create specific prompts for each part of the output
title_prompt = f"Bu haber makalelerine dayanarak, tek bir nesnel başlık oluşturun:"
short_summary_prompt = f"Bu haber makalelerine dayanarak, 140 karakterden oluşan kısa bir özet oluşturun:"
detailed_summary_prompt = f"Bu haber makalelerine dayanarak, detaylı bir özet oluşturun, sadece bilgi verin."

# Initialize the model and generate content for each part
model = genai.GenerativeModel('gemini-1.5-flash')

# Generate the title
title_response = model.generate_content(f"{title_prompt}\n{articles_combined}")
title = title_response.text.strip()

# Generate the short summary
short_summary_response = model.generate_content(f"{short_summary_prompt}\n{articles_combined}")
short_summary = short_summary_response.text.strip()

# Generate the detailed summary
detailed_summary_response = model.generate_content(f"{detailed_summary_prompt}\n{articles_combined}")
detailed_summary = detailed_summary_response.text.strip()

# Function to create the output structure
def create_output(articles, title, short_summary, detailed_summary):
    output = {
        "objectified_title": title,
        "objectified_short_summary": short_summary,
        "objectified_detailed_summary": detailed_summary,
        "sources": [article.get("source", "Unknown") for article in articles if "source" in article]
    }
    return output

# Generate the output JSON data
output_data = create_output(articles, title, short_summary, detailed_summary)

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Save the output to a JSON file
output_filepath = os.path.join(OUTPUT_DIR, "objectified_summary.json")
with open(output_filepath, 'w', encoding='utf-8') as output_file:
    json.dump(output_data, output_file, ensure_ascii=False, indent=4)

print(f"Output saved to {output_filepath}")
