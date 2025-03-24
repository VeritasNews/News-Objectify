import os
import json
import requests

# ✅ Configure paths
JSON_DIR = r"C:\Users\zeyne\Desktop\bitirme\VeritasNews\News-Objectify\objectified_jsons"
INSERT_URL = "http://127.0.0.1:8000/api/insert_articles/"
HEADERS = {"Content-Type": "application/json"}

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

# ✅ Main execution
if __name__ == "__main__":
    print("🚀 Starting JSON upload process...")

    # Step 1: Send new JSON files **without deleting them unless uploaded successfully**
    send_json_files()

    print("✅ Process completed successfully!")
