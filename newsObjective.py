import json
from transformers import T5Tokenizer, T5ForConditionalGeneration

# Load a pre-trained T5 model and tokenizer for summarization
model_name = "google/t5-small"  # You can use "t5-small", "t5-base", or larger models for better accuracy
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

# Function to read JSON articles and extract content
def load_articles_from_json(json_files):
    articles = []
    for file_path in json_files:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            articles.append(data["content"])  # Extract the "content" field
    return articles

# Function to generate an objective summary
def generate_summary(articles, max_length=150):
    input_text = " ".join([f"Article {i+1}: {article}" for i, article in enumerate(articles)])
    input_ids = tokenizer.encode(f"summarize: {input_text}", return_tensors="pt", truncation=True, max_length=1024)
    summary_ids = model.generate(
        input_ids,
        max_length=max_length,
        num_beams=4,
        early_stopping=True
    )
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

# List of JSON article file paths
json_files = [
    "C:/Users/zeyne/Veritas/Veritas/saved_articles/cnn.json",
    "C:/Users/zeyne/Veritas/Veritas/saved_articles/cumhuriyet.json",
    "C:/Users/zeyne/Veritas/Veritas/saved_articles/euronews.json",
    "C:/Users/zeyne/Veritas/Veritas/saved_articles/haberturk.json",
    "C:/Users/zeyne/Veritas/Veritas/saved_articles/ntv.json"
]

# Load articles and generate summary
articles = load_articles_from_json(json_files)
objective_summary = generate_summary(articles)

print("Objective Summary:")
print(objective_summary)
