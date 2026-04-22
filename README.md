# CalTrack — AI-Powered Fitness & Nutrition Tracker

A modern, full-stack web application that uses **Google Gemini AI** to make calorie and exercise tracking effortless. Instead of manually searching food databases or calculating macros, users simply type what they ate or what workout they did in natural language — and the AI handles everything else.

---

## 🚀 Live Demo

🔗 **[caltrack-bice.vercel.app](https://caltrack-bice.vercel.app)**

---

## 📸 Screenshots

<img width="1121" height="852" alt="Screenshot 2026-03-02 230800" src="https://github.com/user-attachments/assets/0e223745-4082-4ee9-a914-434094846f3d" />

<img width="1732" height="801" alt="Screenshot 2026-03-02 230733" src="https://github.com/user-attachments/assets/1d14c2e2-682b-4975-919b-01e42cfa4e6c" />



---

## 💡 The Problem It Solves

Traditional calorie trackers are tedious — you search a database, guess portion sizes, and repeat for every meal. CalTrack removes all of that friction. Just type *"I had a bowl of rice and chicken curry for lunch"* and Gemini AI extracts the calories, macros, and nutritional info automatically.

---

## ✨ Features

- 🤖 **Natural Language Food Logging** — Describe meals in plain English; AI parses calories and macros
- 🏋️ **Exercise Tracking** — Log workouts the same way; AI estimates calories burned
- 📊 **Daily Dashboard** — Visual summary of calorie intake vs. goal
- 🔐 **User Authentication** — Secure register/login with JWT tokens
- 📅 **History & Trends** — View past logs to track progress over time
- 📱 **Responsive UI** — Clean, mobile-friendly design with Bootstrap 5

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Angular, TypeScript, HTML5, CSS3, Bootstrap 5 |
| Backend | Python, Django, Django REST Framework (DRF) |
| AI | Google Generative AI (Gemini) |
| Database | SQLite *(development)* → PostgreSQL *(production-ready)* |
| Deployment | Vercel (frontend) |
| Auth | JWT (JSON Web Tokens) |

---

## 📁 Project Structure

```
caltrack/
├── backend/                  # Django project
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/               # Settings, URLs, WSGI
│   └── apps/
│       ├── users/            # Auth, user profiles
│       ├── nutrition/        # Food log, AI parsing
│       └── exercise/         # Workout log, calorie burn
├── frontend/                 # Angular project
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/   # Dashboard, log form, history
│   │   │   ├── services/     # API calls, auth
│   │   │   └── models/       # TypeScript interfaces
│   └── angular.json
└── README.md
```

---

## ⚙️ Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- Angular CLI (`npm install -g @angular/cli`)
- A Google Gemini API key — get one free at [Google AI Studio](https://aistudio.google.com/)

---

### 🔧 Backend Setup

```bash
# 1. Navigate to backend
cd backend

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your Gemini API key
# Create a .env file in /backend and add:
# GEMINI_API_KEY=your_api_key_here

# 5. Apply migrations
python manage.py migrate

# 6. Start the development server
python manage.py runserver
```

Backend will run at: `http://localhost:8000`

---

### 🎨 Frontend Setup

```bash
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Start the Angular dev server
ng serve
```

Frontend will run at: `http://localhost:4200`

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register/` | Register a new user |
| POST | `/api/auth/login/` | Login and receive JWT token |
| POST | `/api/nutrition/log/` | Log a meal (AI parses it) |
| GET | `/api/nutrition/history/` | Get past food logs |
| POST | `/api/exercise/log/` | Log a workout (AI parses it) |
| GET | `/api/exercise/history/` | Get past exercise logs |
| GET | `/api/dashboard/` | Get daily summary and totals |

---

## 🤖 How the AI Integration Works

1. User types a free-text description (e.g. *"2 idlis with sambar and coconut chutney"*)
2. The Django backend sends this to the **Google Gemini API** with a structured prompt
3. Gemini returns estimated calories, protein, carbs, and fat in JSON format
4. The data is saved to the database and shown instantly on the user's dashboard

No manual database lookup. No portion size guessing. Just type and go.

---

## 🗃️ Database

Uses **SQLite** for local development (zero configuration needed). For production, switch to **PostgreSQL** by updating the `DATABASES` setting in `config/settings.py`.

---

## 🔮 Planned Improvements

- [ ] Add macro breakdown charts (Chart.js / Recharts)
- [ ] Weekly and monthly progress reports
- [ ] Meal photo upload with AI visual recognition
- [ ] Switch to PostgreSQL for production
- [ ] Write unit tests for AI parsing logic
- [ ] PWA support for mobile home screen install

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

---

## 👨‍💻 Author

**Sudev A**
Passionate Python developer and designer.
🔗 [GitHub](https://github.com/sudev-sep) | 🌐 [Live App](https://caltrack-bice.vercel.app)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
