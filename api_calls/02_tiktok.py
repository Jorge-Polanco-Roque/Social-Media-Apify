### EXTRACCIÓN DE MÉTRICAS DE TIKTOK USANDO APIFY ###

import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from apify_client import ApifyClient

# Load environment variables
load_dotenv()

# Initialize the ApifyClient with your API token
client = ApifyClient(os.getenv("APIFY_API_TOKEN"))

# Run the Actor task and wait for it to finish
run = client.task("ZEQZd8JPgNx5e5KB1").call()

# Fetch and save Actor task results to CSV
data = []
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    data.append(item)
    print(f"Processed item: {item.get('id', 'N/A')}")

# Create DataFrame and save to CSV
if data:
    df = pd.DataFrame(data)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"tiktok_task_comments_{timestamp}.csv"
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f"\nData saved to {filename}")
    print(f"Total items: {len(data)}")
else:
    print("No data found")