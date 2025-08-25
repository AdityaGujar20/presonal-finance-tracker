# 💰 Personal Finance Tracker

A clean, simple personal finance tracking web application with AI-powered insights.

## ✨ Features

### 📊 **Dashboard & Analytics**
- Real-time financial metrics (Income, Expenses, Balance, Savings Rate)
- Interactive charts (Pie charts for categories, Bar charts for monthly trends)
- Month/Year filtering with default current month view
- Responsive design for all devices

### 💳 **Transaction Management**
- Add income and expense transactions
- Unlimited amount entry with decimal precision
- Categorized transactions with emoji icons
- Search and filter transaction history
- Delete transactions with confirmation

### 📈 **Comparison Analysis**
- **Monthly Comparison**: Compare specific months across years
- **Yearly Comparison**: Compare entire years
- Side-by-side pie charts with independent filtering
- Smart insights with percentage changes and analysis
- Visual spending pattern identification

### 🤖 **AI Financial Advisor**
- Personalized spending analysis
- Budget optimization suggestions
- Savings recommendations
- Interactive chat for financial questions
- Context-aware advice based on your data

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation & Running

1. **Navigate to the project directory**
   ```bash
   cd personal-finance-tracker
   ```

2. **Install dependencies**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Run the application**
   ```bash
   # Option 1: Use the run script (recommended)
   python run.py
   
   # Option 2: Use the shell script (Linux/Mac)
   ./start.sh
   
   # Option 3: Manual start
   cd backend
   uvicorn main:app --reload --host 0.0.0.0
   ```

4. **Open in browser**
   - The app will automatically open at `http://localhost:8000`
   - Or manually navigate to `http://localhost:8000`

## 💾 Data Storage

### **Local & Private**
- All data stored locally in SQLite database (`finance_tracker.db`)
- No cloud storage - complete privacy
- Works 100% offline after initial load
- No accounts or sign-ups required

### **Backup Your Data**
```bash
python backup-restore.py
```

This utility provides:
- Complete database backup
- CSV export for spreadsheets
- JSON export for data portability
- Easy restore functionality

## 📁 Project Structure

```
personal-finance-tracker/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── database.py          # SQLite database operations
│   ├── financial_advisor.py # AI advisor logic
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── index.html          # Main HTML file
│   ├── styles.css          # CSS styling
│   └── script.js           # JavaScript functionality
├── run.py                  # Easy run script
├── start.sh               # Shell script for Linux/Mac
├── backup-restore.py      # Data backup utility
└── README.md              # This file
```

## 🔧 Configuration

### **Environment Variables**
Create `backend/.env` file for AI features:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### **Database**
- SQLite database created automatically
- Location: `backend/finance_tracker.db`
- No setup required

## 🌟 Usage Tips

### **Dashboard**
- Use month/year filters to focus on specific periods
- Default view shows current month for immediate relevance
- Hover over charts for detailed information

### **Transactions**
- Add transactions with unlimited amounts
- Use descriptive names for better categorization
- Filter by category, type, or date range

### **Comparison**
- Switch between Monthly and Yearly comparison modes
- Compare same months across different years
- Use insights section for spending analysis

### **AI Advisor**
- Ask specific questions about your spending
- Get personalized budget recommendations
- Use quick analysis buttons for instant insights

## 🔒 Privacy & Security

- **100% Local Storage**: Data never leaves your device
- **No Tracking**: No analytics or data collection
- **No Accounts**: No personal information required
- **Offline Capable**: Works without internet connection
- **Open Source**: Full transparency of code

## 🛠️ Troubleshooting

### **Common Issues**

**Port already in use:**
```bash
# The run.py script automatically finds available ports
python run.py
```

**Missing dependencies:**
```bash
pip install -r backend/requirements.txt
```

**Permission errors:**
```bash
pip install --user -r backend/requirements.txt
```
