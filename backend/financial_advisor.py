import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

class FinancialAdvisor:
    def __init__(self):
        self.llm = ChatGroq(
            temperature=0.3,
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.3-70b-versatile"
        )
    
    def analyze_spending_pattern(self, df):
        """Analyze spending patterns and provide comprehensive insights"""
        if df.empty:
            return "No transaction data available for analysis."
        
        # Calculate key metrics
        total_income = df[df['type'] == 'Income']['amount'].sum()
        total_expenses = df[df['type'] == 'Expense']['amount'].sum()
        net_savings = total_income - total_expenses
        savings_rate = (net_savings/total_income*100) if total_income > 0 else 0
        
        # Category analysis
        expense_by_category = df[df['type'] == 'Expense'].groupby('category')['amount'].sum().sort_values(ascending=False)
        top_category = expense_by_category.index[0] if not expense_by_category.empty else "N/A"
        top_category_amount = expense_by_category.iloc[0] if not expense_by_category.empty else 0
        top_category_pct = (top_category_amount/total_expenses*100) if total_expenses > 0 else 0
        
        # Financial health assessment
        if savings_rate >= 20:
            health_status = "🟢 Excellent"
            health_advice = "Keep up the great work!"
        elif savings_rate >= 10:
            health_status = "🟡 Good"
            health_advice = "Try to increase savings to 20%"
        elif savings_rate >= 0:
            health_status = "🟠 Fair"
            health_advice = "Focus on reducing expenses"
        else:
            health_status = "🔴 Poor"
            health_advice = "Urgent: Expenses exceed income!"
        
        # Spending efficiency analysis
        df['date'] = pd.to_datetime(df['date'])
        days_span = (df['date'].max() - df['date'].min()).days + 1
        avg_daily_expense = total_expenses / days_span if days_span > 0 else 0
        
        analysis = f"""
        📊 **Comprehensive Spending Analysis:**
        
        💰 **Financial Health: {health_status}**
        - Total Income: ₹{total_income:,.2f}
        - Total Expenses: ₹{total_expenses:,.2f}
        - Net Savings: ₹{net_savings:,.2f}
        - Savings Rate: {savings_rate:.1f}% | {health_advice}
        
        🎯 **Spending Breakdown:**
        - Top Category: {top_category} (₹{top_category_amount:,.2f} - {top_category_pct:.1f}%)
        - Daily Average: ₹{avg_daily_expense:.2f}
        - Categories Used: {len(expense_by_category)}
        - Transactions: {len(df)} total
        
        💡 **Quick Insights:**
        - {"✅ Healthy diversification" if len(expense_by_category) >= 5 else "⚠️ Consider diversifying spending categories"}
        - {"✅ Controlled top category" if top_category_pct < 40 else "⚠️ Top category dominates spending"}
        - {"✅ Regular transaction pattern" if len(df) > 10 else "📝 Add more transactions for better insights"}
        """
        
        return analysis
    
    def get_budget_suggestions(self, df):
        """Generate intelligent budget suggestions based on spending patterns"""
        if df.empty:
            return "Add some transactions to get personalized budget suggestions!"
        
        total_income = df[df['type'] == 'Income']['amount'].sum()
        total_expenses = df[df['type'] == 'Expense']['amount'].sum()
        expense_by_category = df[df['type'] == 'Expense'].groupby('category')['amount'].sum()
        
        if total_income <= 0:
            return "⚠️ Add income transactions to get budget recommendations!"
        
        # Calculate current allocation
        current_savings_rate = ((total_income - total_expenses) / total_income) * 100
        
        # 50/30/20 Rule recommendations
        needs_budget = total_income * 0.5
        wants_budget = total_income * 0.3
        savings_budget = total_income * 0.2
        
        # Analyze current vs recommended
        needs_categories = ["🏠 Housing", "💡 Utilities", "🚗 Transportation", "🏥 Healthcare"]
        wants_categories = ["🍔 Food & Dining", "🎬 Entertainment", "🛒 Shopping", "🎁 Gifts"]
        
        current_needs = sum([expense_by_category.get(cat, 0) for cat in needs_categories])
        current_wants = sum([expense_by_category.get(cat, 0) for cat in wants_categories])
        
        suggestions = f"""
        💡 **Personalized Budget Recommendations:**
        
        📊 **Current vs Recommended Allocation:**
        
        🏠 **Needs (Recommended: 50% = ₹{needs_budget:,.2f})**
        - Current: ₹{current_needs:,.2f} ({(current_needs/total_income*100):.1f}%)
        - {"✅ Within range" if current_needs <= needs_budget else "⚠️ Reduce by ₹" + f"{current_needs - needs_budget:,.2f}"}
        
        🎬 **Wants (Recommended: 30% = ₹{wants_budget:,.2f})**
        - Current: ₹{current_wants:,.2f} ({(current_wants/total_income*100):.1f}%)
        - {"✅ Within range" if current_wants <= wants_budget else "⚠️ Reduce by ₹" + f"{current_wants - wants_budget:,.2f}"}
        
        💰 **Savings (Recommended: 20% = ₹{savings_budget:,.2f})**
        - Current: {current_savings_rate:.1f}%
        - {"✅ Excellent!" if current_savings_rate >= 20 else "📈 Increase by " + f"{20 - current_savings_rate:.1f}%"}
        
        🎯 **Action Items:**
        """
        
        # Add specific recommendations based on their data
        if not expense_by_category.empty:
            top_category = expense_by_category.idxmax()
            top_amount = expense_by_category.max()
            top_percentage = (top_amount / total_expenses) * 100
            
            if top_percentage > 40:
                suggestions += f"\n- 🔥 Priority: Reduce {top_category} spending (currently {top_percentage:.1f}% of expenses)"
            
            if current_savings_rate < 10:
                suggestions += f"\n- 🚨 Critical: Increase savings rate from {current_savings_rate:.1f}% to at least 10%"
            
            # Category-specific advice
            food_spending = expense_by_category.get("🍔 Food & Dining", 0)
            if food_spending > total_income * 0.15:
                suggestions += f"\n- 🍽️ Food spending high: Try meal planning (current: ₹{food_spending:,.2f})"
        
        return suggestions
    
    def get_savings_tips(self, df):
        """Provide personalized savings tips"""
        if df.empty:
            return "Add transactions to get personalized savings tips!"
        
        expense_by_category = df[df['type'] == 'Expense'].groupby('category')['amount'].sum().sort_values(ascending=False)
        
        tips = """
        🎯 **Personalized Savings Tips:**
        
        """
        
        if not expense_by_category.empty:
            top_category = expense_by_category.index[0]
            
            category_tips = {
                "🍔 Food & Dining": "Consider meal planning and cooking at home more often. Try the 80/20 rule - cook 80% of meals at home.",
                "🛒 Shopping": "Create a shopping list and stick to it. Wait 24 hours before making non-essential purchases.",
                "🎬 Entertainment": "Look for free or low-cost entertainment options. Consider streaming services instead of movie theaters.",
                "🚗 Transportation": "Use public transport, carpool, or bike when possible. Regular vehicle maintenance can save fuel costs.",
                "💡 Utilities": "Switch to energy-efficient appliances and be mindful of electricity usage.",
            }
            
            if top_category in category_tips:
                tips += f"🔥 **Focus Area - {top_category}:**\n{category_tips[top_category]}\n\n"
        
        tips += """
        💡 **General Tips:**
        - Set up automatic transfers to savings account
        - Use the envelope method for discretionary spending
        - Review and cancel unused subscriptions
        - Compare prices before making purchases
        - Set specific financial goals and track progress
        """
        
        return tips
    
    def get_financial_advice(self, df, user_question):
        """Get AI-powered financial advice based on user data and question"""
        
        # Prepare comprehensive financial context
        financial_summary = self._prepare_financial_summary(df)
        financial_insights = self._get_financial_insights(df)
        financial_knowledge = self._get_financial_knowledge_base()
        
        prompt_template = """
        You are an expert financial advisor with deep knowledge of personal finance, budgeting, and investment strategies.
        
        ### FINANCIAL KNOWLEDGE BASE:
        {financial_knowledge}
        
        ### USER'S FINANCIAL DATA:
        {financial_summary}
        
        ### FINANCIAL INSIGHTS:
        {financial_insights}
        
        ### USER'S QUESTION:
        {user_question}
        
        ### INSTRUCTIONS:
        - Provide personalized advice based on their actual spending data
        - Reference relevant financial principles from the knowledge base
        - Give specific, actionable recommendations with numbers
        - Be concise but comprehensive (3-4 sentences max)
        - Include relevant percentages, ratios, or benchmarks
        - Use 1-2 emojis for engagement
        - If asked for detailed explanations, provide structured advice
        
        ### FINANCIAL ADVICE:
        """
        
        prompt = PromptTemplate.from_template(prompt_template)
        chain = prompt | self.llm
        
        try:
            response = chain.invoke({
                "financial_summary": financial_summary,
                "financial_insights": financial_insights,
                "financial_knowledge": financial_knowledge,
                "user_question": user_question
            })
            return response.content
        except Exception as e:
            return f"Sorry, I couldn't process your question right now. Please try again. Error: {str(e)}"
    
    def _prepare_financial_summary(self, df):
        """Prepare a summary of financial data for the AI"""
        if df.empty:
            return "No financial data available."
        
        # Basic metrics
        total_income = df[df['type'] == 'Income']['amount'].sum()
        total_expenses = df[df['type'] == 'Expense']['amount'].sum()
        net_savings = total_income - total_expenses
        
        # Category breakdown
        expense_by_category = df[df['type'] == 'Expense'].groupby('category')['amount'].sum().sort_values(ascending=False)
        
        # Time period
        df['date'] = pd.to_datetime(df['date'])
        date_range = f"{df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}"
        
        summary = f"""
        Financial Period: {date_range}
        Total Income: ₹{total_income:,.2f}
        Total Expenses: ₹{total_expenses:,.2f}
        Net Savings: ₹{net_savings:,.2f}
        Savings Rate: {(net_savings/total_income*100) if total_income > 0 else 0:.1f}%
        
        Top Expense Categories:
        """
        
        for i, (category, amount) in enumerate(expense_by_category.head(5).items()):
            percentage = (amount/total_expenses*100) if total_expenses > 0 else 0
            summary += f"{i+1}. {category}: ₹{amount:,.2f} ({percentage:.1f}%)\n"
        
        return summary
    
    def _get_financial_insights(self, df):
        """Generate advanced financial insights and patterns"""
        if df.empty:
            return "No transaction data available for insights."
        
        insights = []
        
        # Calculate key financial ratios
        total_income = df[df['type'] == 'Income']['amount'].sum()
        total_expenses = df[df['type'] == 'Expense']['amount'].sum()
        
        if total_income > 0:
            savings_rate = ((total_income - total_expenses) / total_income) * 100
            expense_ratio = (total_expenses / total_income) * 100
            
            # Savings rate analysis
            if savings_rate >= 20:
                insights.append(f"✅ Excellent savings rate: {savings_rate:.1f}% (Recommended: 20%+)")
            elif savings_rate >= 10:
                insights.append(f"⚠️ Moderate savings rate: {savings_rate:.1f}% (Try to reach 20%)")
            else:
                insights.append(f"🚨 Low savings rate: {savings_rate:.1f}% (Critical: Increase to 10%+)")
        
        # Spending pattern analysis
        expense_by_category = df[df['type'] == 'Expense'].groupby('category')['amount'].sum()
        if not expense_by_category.empty:
            top_category = expense_by_category.idxmax()
            top_percentage = (expense_by_category.max() / total_expenses) * 100
            insights.append(f"📊 Top spending: {top_category} ({top_percentage:.1f}% of expenses)")
        
        # Transaction frequency analysis
        df['date'] = pd.to_datetime(df['date'])
        days_span = (df['date'].max() - df['date'].min()).days + 1
        avg_daily_expense = total_expenses / days_span if days_span > 0 else 0
        insights.append(f"💸 Average daily spending: ₹{avg_daily_expense:.2f}")
        
        # Monthly trend analysis
        if len(df) > 1:
            monthly_expenses = df[df['type'] == 'Expense'].groupby(df['date'].dt.to_period('M'))['amount'].sum()
            if len(monthly_expenses) > 1:
                trend = "increasing" if monthly_expenses.iloc[-1] > monthly_expenses.iloc[0] else "decreasing"
                insights.append(f"📈 Spending trend: {trend} over time")
        
        return "\n".join(insights)
    
    def _get_financial_knowledge_base(self):
        """Comprehensive financial knowledge base for better advice"""
        return """
        ### FINANCIAL PRINCIPLES & BENCHMARKS:
        
        **Budgeting Rules:**
        - 50/30/20 Rule: 50% needs, 30% wants, 20% savings
        - 80/20 Rule: 80% expenses, 20% savings (minimum)
        - Emergency Fund: 3-6 months of expenses
        
        **Spending Guidelines (% of income):**
        - Housing: 25-30% (rent, utilities, maintenance)
        - Food: 10-15% (groceries + dining out)
        - Transportation: 10-15% (fuel, maintenance, public transport)
        - Entertainment: 5-10% (movies, hobbies, subscriptions)
        - Healthcare: 5-10% (insurance, medical expenses)
        - Savings: 20%+ (investments, emergency fund)
        
        **Savings Strategies:**
        - Pay yourself first (automate savings)
        - Track every expense for awareness
        - Use envelope method for discretionary spending
        - Review and optimize subscriptions monthly
        - Set specific financial goals with deadlines
        
        **Investment Basics:**
        - Start early (compound interest advantage)
        - Diversify investments (don't put all eggs in one basket)
        - Low-cost index funds for beginners
        - SIP (Systematic Investment Plan) for regular investing
        - Risk tolerance decreases with age
        
        **Debt Management:**
        - Pay high-interest debt first (credit cards)
        - Debt-to-income ratio should be <36%
        - Avoid lifestyle inflation
        - Consider debt consolidation for multiple debts
        
        **Financial Red Flags:**
        - Savings rate below 10%
        - Living paycheck to paycheck
        - Increasing credit card debt
        - No emergency fund
        - Spending more than 30% on housing
        
        **Money-Saving Tips:**
        - Cook at home (can save 60% on food costs)
        - Use public transport or bike
        - Buy generic brands for basics
        - Cancel unused subscriptions
        - Shop with a list and stick to it
        - Use cashback and reward programs
        - Compare prices before major purchases
        
        **Age-Based Financial Milestones:**
        - 20s: Build emergency fund, start investing
        - 30s: 1x annual salary saved, buy insurance
        - 40s: 3x annual salary saved, peak earning years
        - 50s: 5x annual salary saved, retirement planning
        - 60s: 8-10x annual salary saved, pre-retirement
        """