import requests
import time

API_KEY = "YOUR_PRODIA_API_KEY"

prompt = "AI takes over the world, futuristic city, cinematic, ultra realistic"

# Start image generation
start = requests.post(
    "https://api.prodia.com/v1/job",
    headers={"X-Prodia-Key": API_KEY},
    json={"prompt": prompt, "model": "sdxl", "steps": 30},
).json()

job_id = start["job"]
print("Job ID:", job_id)

# Poll until finished
while True:
    result = requests.get(
        f"https://api.prodia.com/v1/job/{job_id}", headers={"X-Prodia-Key": API_KEY}
    ).json()

    if result["status"] == "succeeded":
        print("Image URL:", result["imageUrl"])
        break
    elif result["status"] == "failed":
        print("Generation failed")
        break

    time.sleep(1)
