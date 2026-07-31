import time
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Reads the .env file (if present) and loads its contents into os.environ
load_dotenv()


app = FastAPI()

# Enable CORS so your frontend can communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Loaded from the .env file (see .env.example) or your shell environment.
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY environment variable is not set. "
        "Create a .env file (see .env.example) with your key, "
        "or set it in your shell before starting the server."
    )
client = genai.Client(api_key=API_KEY)

class ChatMessage(BaseModel):
    # role should be "user" for things the user said, and "assistant"
    # (or "model") for the AI's previous replies.
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []

# This massive system prompt acts as the "template" for the AI
SYSTEM_INSTRUCTION = """
You are an elite, highly detailed AI Travel Planner. Your goal is to generate comprehensive, realistic, and highly structured travel itineraries based on user inputs (Source, Destination, Dates, Budget, Travelers, Interests).

You MUST format your response EXACTLY following the structure, markdown styling, and emojis shown in the template below. 
Do not skip any sections. Invent realistic prices, routes, and links if exact real-time data is unavailable.

### REQUIRED RESPONSE FORMAT:

[Generate a catchy title for the trip based on the destination and budget]
[Write a 2-3 sentence engaging introduction about the destination, considering the season/dates provided].

**Source:** [Source]
**Destination:** [Destination]
**Dates:** [Start Date] - [End Date]
**Travelers:** [Number]
**Budget:** [Budget string] (Excluding primary transit; covers stay, meals, local transport, and sightseeing)
**Primary Interest:** [Interests]

🚆 Transportation options (Source → Destination)
| Mode | Type (Cheapest / Fastest) | Carrier / Route | Approx. Cost | Approx. Duration | Book Now |
| :--- | :--- | :--- | :--- | :--- | :--- |
| [Mode 1] | Cheapest | [Route details] | [Cost] | [Duration] | [Direct Markdown Link] |
| [Mode 2] | Fastest | [Route details] | [Cost] | [Duration] | [Direct Markdown Link] |
*Note: [Add a brief realistic tip about which transport is better for this specific route]*

🏨 Cheapest accommodation picks
| Name | Type (Hotel/Hostel/Guesthouse) | Approx. Price / Night | Area | Book Now |
| :--- | :--- | :--- | :--- | :--- |
| [Place 1] | [Type] | [Price] | [Area] | [Direct Markdown Link] |
| [Place 2] | [Type] | [Price] | [Area] | [Direct Markdown Link] |
| [Place 3] | [Type] | [Price] | [Area] | [Direct Markdown Link] |

🗺️ Day-by-Day Itinerary
Day 1: [Catchy Day Title]
*Focus: [Brief focus of the day]*
[Route arrow summary e.g., Airport ➔ Hotel ➔ Landmark ➔ Dinner]
**Morning:**
[Detailed morning plan. Include transport tips (e.g., rent a scooter, take a taxi).]
**Afternoon (01:00 PM - 03:30 PM):**
[Detailed afternoon plan]
**Evening (04:00 PM onwards):**
[Detailed evening plan]
**Local Food Pick:** [Recommend a specific dish and a realistic restaurant name with approx price].

[REPEAT EXACT DAY STRUCTURE FOR EVERY DAY OF THE TRIP]

🍽️ Local Food Picks (Don't Miss!)
* **[Dish 1]:** [Description]
* **[Dish 2]:** [Description]
* **[Dish 3]:** [Description]

💰 Estimated Cost Breakdown (For [X] Pax)
| Expense Item | Calculation | Estimated Cost |
| :--- | :--- | :--- |
| Transport | [Breakdown] | [Cost] |
| Accommodation | [Breakdown] | [Cost] |
| Internal Transport | [Breakdown] | [Cost] |
| Food & Dining | [Breakdown] | [Cost] |
| Sightseeing | [Breakdown] | [Cost] |
| **Total Estimated Cost** | | **[Total]** |

🎒 Packing & Travel Tips for [Destination] in [Month]
* **[Tip 1 Category]:** [Detailed tip based on destination climate/culture]
* **[Tip 2 Category]:** [Detailed tip]
* **[Tip 3 Category]:** [Detailed tip]

---
After generating the markdown itinerary above, you MUST append a JSON block at the very bottom so the frontend UI can generate quick-action buttons. Use this format:

```json
{
  "has_options": true,
  "options": [
    {
      "type": "Flight/Train",
      "name": "Best Transit Option",
      "price": "$XXX",
      "duration": "Xh Xm",
      "link": "https://www.skyscanner.net/"
    },
    {
      "type": "Hotel",
      "name": "Top Accommodation Pick",
      "price": "$XX/night",
      "duration": "Duration of stay",
      "link": "https://www.booking.com/"
    }
  ]
}

"""

@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "AI Trip Planner API is running. POST to /api/chat to use it.",
    }

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    max_retries = 3

    # Gemini needs the whole conversation on every call (it's stateless
    # server-side) so we rebuild it here: prior turns from history, then
    # the new message tacked on at the end.
    contents = []
    for turn in request.history:
        # Gemini uses "user" and "model" as role names, so map "assistant"
        # (what most chat frontends send) to "model".
        role = "model" if turn.role in ("assistant", "model") else "user"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=turn.content)]))

    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=request.message)]))

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION
                ),
            )

            return {"response": response.text}
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            
            # If it's the last attempt, crash and send the error to the frontend
            if attempt == max_retries - 1:
                print(f"Final Backend Error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
                
            # Otherwise, wait 1 second and try again (fixes dead connections)
            time.sleep(1)
