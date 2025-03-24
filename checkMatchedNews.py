from sentence_transformers import SentenceTransformer, util
import os
import json

# Load model
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

def load_articles_from_dir(dir_path):
    articles = []
    for file in os.listdir(dir_path):
        if file.endswith(".json"):
            with open(os.path.join(dir_path, file), "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    content = data.get("content", "").strip()
                    title = data.get("title", "").strip()
                    if content:
                        # Combine title + content for better semantic info
                        articles.append(f"{title}\n{content}")
                except json.JSONDecodeError:
                    print(f"❌ Could not parse JSON file: {file}")
    return articles

def check_similarity(folder_path):
    articles = load_articles_from_dir(folder_path)
    print(f"📁 Checking: {folder_path} | {len(articles)} articles")
    
    if len(articles) < 2:
        return None  # Can't compare
    
    embeddings = model.encode(articles, convert_to_tensor=True)
    
    # Compute cosine similarities between all pairs
    scores = []
    for i in range(len(embeddings)):
        for j in range(i+1, len(embeddings)):
            sim = util.cos_sim(embeddings[i], embeddings[j]).item()
            scores.append(sim)
    
    avg_similarity = sum(scores) / len(scores)
    return avg_similarity

# Base directory containing all MatchedNewsData folders
base_dir = r"C:\Users\zeyne\Desktop\bitirme\VeritasNews\News-Objectify\articles"

all_scores = {}
for folder in os.listdir(base_dir):
    full_path = os.path.join(base_dir, folder)
    if os.path.isdir(full_path):
        sim_score = check_similarity(full_path)
        if sim_score is not None:
            all_scores[folder] = sim_score

# Print or save results
print("\n🧾 Similarity Results (higher = more topically matched):")
for k, v in sorted(all_scores.items(), key=lambda x: x[1], reverse=True):
    print(f"{k}: avg similarity = {v:.4f}")
