from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime
import pandas as pd
from database import DatabaseManager
from financial_advisor import FinancialAdvisor

app = FastAPI(title="Personal Finance Tracker API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="../frontend"), name="static")



# Initialize services
db = DatabaseManager()
advisor = FinancialAdvisor()

# Pydantic models
class TransactionCreate(BaseModel):
    date: date
    category: str
    amount: float
    type: str  # "Income" or "Expense"
    description: Optional[str] = ""

class TransactionResponse(BaseModel):
    id: int
    date: str
    category: str
    amount: float
    type: str
    description: str
    created_at: str

class FinancialSummary(BaseModel):
    total_income: float
    total_expenses: float
    net_balance: float
    savings_rate: float
    avg_expense: float
    transaction_count: int

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

# Routes
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page"""
    with open("../frontend/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.post("/api/transactions", response_model=dict)
async def create_transaction(transaction: TransactionCreate):
    """Add a new transaction"""
    try:
        success = db.add_transaction(
            date=transaction.date,
            category=transaction.category,
            amount=transaction.amount,
            transaction_type=transaction.type,
            description=transaction.description
        )
        if success:
            return {"message": "Transaction added successfully", "success": True}
        else:
            raise HTTPException(status_code=400, detail="Failed to add transaction")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/transactions", response_model=List[dict])
async def get_transactions():
    """Get all transactions"""
    try:
        df = db.get_all_transactions()
        if df.empty:
            return []
        
        # Convert DataFrame to list of dictionaries
        transactions = []
        for _, row in df.iterrows():
            transactions.append({
                "id": int(row['id']),
                "date": str(row['date']),
                "category": row['category'],
                "amount": float(row['amount']),
                "type": row['type'],
                "description": row['description'] or "",
                "created_at": str(row['created_at'])
            })
        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/transactions/{transaction_id}")
async def delete_transaction(transaction_id: int):
    """Delete a transaction"""
    try:
        success = db.delete_transaction(transaction_id)
        if success:
            return {"message": "Transaction deleted successfully", "success": True}
        else:
            raise HTTPException(status_code=404, detail="Transaction not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard")
async def get_dashboard_data(month: Optional[int] = None, year: Optional[int] = None):
    """Get dashboard summary and chart data with optional month/year filtering"""
    try:
        df = db.get_all_transactions()
        
        if df.empty:
            return {
                "summary": {
                    "total_income": 0,
                    "total_expenses": 0,
                    "net_balance": 0,
                    "savings_rate": 0,
                    "avg_expense": 0,
                    "transaction_count": 0
                },
                "category_chart": [],
                "monthly_chart": [],
                "recent_transactions": [],
                "available_months": [],
                "available_years": []
            }
        
        # Convert date column to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Get available months and years for filters
        available_years = sorted(df['date'].dt.year.unique().tolist(), reverse=True)
        available_months = []
        
        # If year is specified, get months for that year
        if year:
            year_df = df[df['date'].dt.year == year]
            available_months = sorted(year_df['date'].dt.month.unique().tolist())
        else:
            # Get all unique months across all years
            available_months = sorted(df['date'].dt.month.unique().tolist())
        
        # Apply date filtering
        filtered_df = df.copy()
        
        # Default to current month if no filters specified
        if month is None and year is None:
            from datetime import datetime
            current_date = datetime.now()
            month = current_date.month
            year = current_date.year
        
        if year:
            filtered_df = filtered_df[filtered_df['date'].dt.year == year]
        if month:
            filtered_df = filtered_df[filtered_df['date'].dt.month == month]
        
        # Calculate summary for filtered data
        total_income = float(filtered_df[filtered_df['type'] == 'Income']['amount'].sum())
        total_expenses = float(filtered_df[filtered_df['type'] == 'Expense']['amount'].sum())
        net_balance = total_income - total_expenses
        savings_rate = (net_balance / total_income * 100) if total_income > 0 else 0
        avg_expense = float(filtered_df[filtered_df['type'] == 'Expense']['amount'].mean()) if not filtered_df[filtered_df['type'] == 'Expense'].empty else 0
        
        summary = {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_balance": net_balance,
            "savings_rate": savings_rate,
            "avg_expense": avg_expense,
            "transaction_count": len(filtered_df),
            "current_month": month,
            "current_year": year
        }
        
        # Category chart data (filtered)
        expense_df = filtered_df[filtered_df['type'] == 'Expense']
        category_data = []
        if not expense_df.empty:
            category_sum = expense_df.groupby('category')['amount'].sum()
            for category, amount in category_sum.items():
                category_data.append({
                    "category": category,
                    "amount": float(amount)
                })
        
        # Monthly chart data (always show full year or last 12 months)
        monthly_data = []
        if not df.empty:
            if year:
                # Show all months for the selected year
                year_df = df[df['date'].dt.year == year]
                monthly_expenses = year_df[year_df['type'] == 'Expense'].groupby(year_df['date'].dt.month)['amount'].sum()
                month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                for month_num in range(1, 13):
                    amount = monthly_expenses.get(month_num, 0)
                    monthly_data.append({
                        "month": month_names[month_num - 1],
                        "amount": float(amount)
                    })
            else:
                # Show last 12 months
                monthly_expenses = df[df['type'] == 'Expense'].groupby(df['date'].dt.to_period('M'))['amount'].sum()
                for period, amount in monthly_expenses.tail(12).items():
                    monthly_data.append({
                        "month": str(period),
                        "amount": float(amount)
                    })
        
        # Recent transactions (filtered)
        recent_transactions = []
        for _, row in filtered_df.head(5).iterrows():
            recent_transactions.append({
                "id": int(row['id']),
                "date": str(row['date'])[:10],
                "category": row['category'],
                "amount": float(row['amount']),
                "type": row['type']
            })
        
        return {
            "summary": summary,
            "category_chart": category_data,
            "monthly_chart": monthly_data,
            "recent_transactions": recent_transactions,
            "available_months": available_months,
            "available_years": available_years
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_advisor(message: ChatMessage):
    """Chat with AI financial advisor"""
    try:
        df = db.get_all_transactions()
        
        if df.empty:
            return ChatResponse(response="Please add some transactions first to get personalized financial advice!")
        
        response = advisor.get_financial_advice(df, message.message)
        return ChatResponse(response=response)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.get("/api/analysis/spending")
async def get_spending_analysis():
    """Get detailed spending analysis"""
    try:
        df = db.get_all_transactions()
        
        if df.empty:
            return {"analysis": "No transaction data available for analysis."}
        
        analysis = advisor.analyze_spending_pattern(df)
        return {"analysis": analysis}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analysis/budget")
async def get_budget_suggestions():
    """Get budget suggestions"""
    try:
        df = db.get_all_transactions()
        
        if df.empty:
            return {"suggestions": "Add some transactions to get budget suggestions!"}
        
        suggestions = advisor.get_budget_suggestions(df)
        return {"suggestions": suggestions}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analysis/savings")
async def get_savings_tips():
    """Get savings tips"""
    try:
        df = db.get_all_transactions()
        
        if df.empty:
            return {"tips": "Add transactions to get personalized savings tips!"}
        
        tips = advisor.get_savings_tips(df)
        return {"tips": tips}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/comparison")
async def get_comparison_data():
    """Get month-wise and year-wise spending comparison data"""
    try:
        df = db.get_all_transactions()
        
        if df.empty:
            return {
                "monthly_comparison": [],
                "yearly_comparison": [],
                "category_trends": []
            }
        
        df['date'] = pd.to_datetime(df['date'])
        expense_df = df[df['type'] == 'Expense']
        
        # Monthly comparison (last 12 months)
        monthly_comparison = []
        if not expense_df.empty:
            monthly_expenses = expense_df.groupby(expense_df['date'].dt.to_period('M'))['amount'].sum()
            for period, amount in monthly_expenses.tail(12).items():
                monthly_comparison.append({
                    "period": str(period),
                    "amount": float(amount),
                    "month": period.month,
                    "year": period.year
                })
        
        # Yearly comparison
        yearly_comparison = []
        if not expense_df.empty:
            yearly_expenses = expense_df.groupby(expense_df['date'].dt.year)['amount'].sum()
            for year, amount in yearly_expenses.items():
                yearly_comparison.append({
                    "year": int(year),
                    "amount": float(amount)
                })
        
        # Category trends (top 5 categories over time)
        category_trends = []
        if not expense_df.empty:
            top_categories = expense_df.groupby('category')['amount'].sum().nlargest(5).index
            
            for category in top_categories:
                category_data = expense_df[expense_df['category'] == category]
                monthly_trend = category_data.groupby(category_data['date'].dt.to_period('M'))['amount'].sum()
                
                trend_data = []
                for period, amount in monthly_trend.tail(6).items():  # Last 6 months
                    trend_data.append({
                        "period": str(period),
                        "amount": float(amount)
                    })
                
                category_trends.append({
                    "category": category,
                    "data": trend_data,
                    "total": float(expense_df[expense_df['category'] == category]['amount'].sum())
                })
        
        return {
            "monthly_comparison": monthly_comparison,
            "yearly_comparison": yearly_comparison,
            "category_trends": category_trends
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/yearly")
async def get_yearly_dashboard_data(year: int):
    """Get yearly dashboard data for comparison"""
    try:
        df = db.get_all_transactions()
        
        if df.empty:
            return {
                "summary": {
                    "total_income": 0,
                    "total_expenses": 0,
                    "net_balance": 0,
                    "savings_rate": 0,
                    "avg_expense": 0,
                    "transaction_count": 0
                },
                "category_chart": []
            }
        
        # Convert date column to datetime and filter by year
        df['date'] = pd.to_datetime(df['date'])
        yearly_df = df[df['date'].dt.year == year]
        
        if yearly_df.empty:
            return {
                "summary": {
                    "total_income": 0,
                    "total_expenses": 0,
                    "net_balance": 0,
                    "savings_rate": 0,
                    "avg_expense": 0,
                    "transaction_count": 0
                },
                "category_chart": []
            }
        
        # Calculate summary for the year
        total_income = float(yearly_df[yearly_df['type'] == 'Income']['amount'].sum())
        total_expenses = float(yearly_df[yearly_df['type'] == 'Expense']['amount'].sum())
        net_balance = total_income - total_expenses
        savings_rate = (net_balance / total_income * 100) if total_income > 0 else 0
        avg_expense = float(yearly_df[yearly_df['type'] == 'Expense']['amount'].mean()) if not yearly_df[yearly_df['type'] == 'Expense'].empty else 0
        
        summary = {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_balance": net_balance,
            "savings_rate": savings_rate,
            "avg_expense": avg_expense,
            "transaction_count": len(yearly_df),
            "year": year
        }
        
        # Category chart data for the year
        expense_df = yearly_df[yearly_df['type'] == 'Expense']
        category_data = []
        if not expense_df.empty:
            category_sum = expense_df.groupby('category')['amount'].sum()
            for category, amount in category_sum.items():
                category_data.append({
                    "category": category,
                    "amount": float(amount)
                })
        
        return {
            "summary": summary,
            "category_chart": category_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)