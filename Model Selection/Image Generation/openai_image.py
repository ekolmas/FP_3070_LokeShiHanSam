# Require credits in openai

from openai import OpenAI
import base64
from dotenv import load_dotenv
import os

load_dotenv()
token = os.environ.get("OPENAI_API_KEY")

# Set your API key
client = OpenAI(api_key=token)

prompt = "AI takes over the world, cinematic, dramatic lighting, ultra detailed"

result = client.images.generate(model="gpt-image-1", prompt=prompt, size="1024x1024")

# Decode base64 image
image_base64 = result.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

with open("openai_result.png", "wb") as f:
    f.write(image_bytes)

print("Image saved as openai_result.png")
