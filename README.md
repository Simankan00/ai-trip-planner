# 🌍 AI Travel Planner

A full-stack, AI-powered travel agent that instantly generates personalized, day-by-day itineraries, cost estimates, and direct booking links based on your specific budget and preferences. 

Try it live here: **https://ai-trip-planner-sandy-three.vercel.app/**

## ✨ Features
* **Personalized Itineraries:** Generates structured, day-by-day travel plans based on source, destination, dates, and interests.
* **Cost Estimator:** Automatically calculates a realistic budget breakdown for accommodation, food, and local transit.
* **Smart Recommendations:** Suggests local dishes, cultural tips, and the best modes of transportation.
* **Direct Booking Links:** Extracts dynamic JSON data to generate quick-action booking buttons for hotels and transit.
* **Responsive UI:** Clean, modern frontend that looks great on both desktop and mobile devices.

## 🛠️ Tech Stack
**Frontend:**
* HTML5, CSS3, Vanilla JavaScript
* [Marked.js](https://marked.js.org/) (for rendering Markdown responses)
* Deployed on **Vercel**

**Backend:**
* Python 3
* [FastAPI](https://fastapi.tiangolo.com/) (RESTful API framework)
* Google GenAI SDK (Powered by **Gemini 1.5 Flash-8B**)
* Deployed on **Render**

## 🚀 Running the Project Locally

If you want to run this project on your own machine, follow these steps:

### Prerequisites
* Python 3.9+ installed
* A free Google Gemini API Key

### 1. Clone the repository
```bash
git clone [https://github.com/YOUR_USERNAME/ai-trip-planner.git](https://github.com/YOUR_USERNAME/ai-trip-planner.git)
cd ai-trip-planner
