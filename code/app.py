import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Custom CSS to improve the look and feel
st.markdown("""
<style>
    .main {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stApp {
        background-image: linear-gradient(to right top, #d16ba5, #c777b9, #ba83ca, #aa8fd8, #9a9ae1, #8aa7ec, #79b3f4, #69bff8, #52cffe, #41dfff, #46eefa, #5ffbf1);
        background-attachment: fixed;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    .stButton>button {
        background-color: #3498db;
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #2980b9;
    }
    .stTextInput>div>div>input {
        background-color: #f8fafc;
        border: 1px solid #cbd5e0;
        border-radius: 5px;
    }
    .stSelectbox>div>div>select {
        background-color: #f8fafc;
        border: 1px solid #cbd5e0;
        border-radius: 5px;
    }
    .sidebar .sidebar-content {
        background-color: #2c3e50;
        color: #ecf0f1;
    }
    .sidebar .sidebar-content .stRadio > label {
        color: #ecf0f1;
        font-weight: bold;
    }
    .sidebar .sidebar-content .stRadio > div {
        background-color: #34495e;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .sidebar .sidebar-content [data-testid="stVerticalBlock"] {
        gap: 0.5rem;
    }
    .sidebar .sidebar-content [data-testid="stMarkdownContainer"] p {
        font-size: 1.2em;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize empty DataFrames to store expenses
if 'personal_expenses' not in st.session_state:
    st.session_state.personal_expenses = pd.DataFrame(columns=["Date", "Category", "Amount"])

if 'group_expenses' not in st.session_state:
    st.session_state.group_expenses = pd.DataFrame(columns=["Description", "Total", "Participants", "Paid", "Owes"])

# Helper function to download dataframe as CSV
def download_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# Home Page
def home_page():
    st.title("💰 Expense Tracker & Splitter")
    st.write("Welcome to your personal finance management hub!")

    # Animated welcome message
    st.markdown(
        """
        <div style="background-color: #f0f8ff; padding: 20px; border-radius: 10px; text-align: center;">
            <h2 style="color: #1e3a8a;">Track, Split, and Visualize Your Expenses</h2>
            <p style="font-size: 18px;">Take control of your finances with our easy-to-use tools!</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Display summary statistics
    if not st.session_state.personal_expenses.empty:
        total_expenses = st.session_state.personal_expenses['Amount'].sum()
        avg_expense = st.session_state.personal_expenses['Amount'].mean()
        
        st.subheader("📊 Quick Stats")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Expenses", f"₹{total_expenses:.2f}")
        col2.metric("Average Expense", f"₹{avg_expense:.2f}")
        col3.metric("Number of Expenses", len(st.session_state.personal_expenses))

    # Quick add expense widget
    st.subheader("🚀 Quick Add Expense")
    with st.form("quick_add_expense"):
        col1, col2, col3 = st.columns(3)
        quick_date = col1.date_input("Date", value=datetime.now())
        quick_category = col2.selectbox("Category", ["Food", "Rent", "Entertainment", "Transport", "Other"])
        quick_amount = col3.number_input("Amount", min_value=0.0, step=0.01)
        submitted = st.form_submit_button("Add Expense")
        if submitted:
            new_expense = pd.DataFrame({"Date": [quick_date], "Category": [quick_category], "Amount": [quick_amount]})
            st.session_state.personal_expenses = pd.concat([st.session_state.personal_expenses, new_expense], ignore_index=True)
            st.success("Expense added successfully!")

    # Recent expenses widget
    if not st.session_state.personal_expenses.empty:
        st.subheader("🕒 Recent Expenses")
        recent_expenses = st.session_state.personal_expenses.sort_values("Date", ascending=False).head(5)
        st.table(recent_expenses)

# Personal Expense Tracker Pages
def add_personal_expense():
    st.header("📝 Add Personal Expense")
    with st.form("add_expense_form"):
        col1, col2 = st.columns(2)
        date = col1.date_input("Date")
        category = col2.selectbox("Category", ["Food", "Rent", "Entertainment", "Transport", "Other"])
        amount = st.number_input("Amount", min_value=0.0, step=0.01)
        note = st.text_area("Note (optional)")
        submitted = st.form_submit_button("Add Expense")
        if submitted:
            new_expense = pd.DataFrame({"Date": [date], "Category": [category], "Amount": [amount], "Note": [note]})
            st.session_state.personal_expenses = pd.concat([st.session_state.personal_expenses, new_expense], ignore_index=True)
            st.success("Expense added successfully!")

def view_personal_expenses():
    st.header("📅 Expense History")
    
    col1, col2 = st.columns(2)
    start_date = col1.date_input("Start Date", value=pd.to_datetime("2024-01-01"))
    end_date = col2.date_input("End Date", value=pd.to_datetime("2024-12-31"))

    filtered_expenses = st.session_state.personal_expenses[
        (pd.to_datetime(st.session_state.personal_expenses['Date']) >= pd.to_datetime(start_date)) &
        (pd.to_datetime(st.session_state.personal_expenses['Date']) <= pd.to_datetime(end_date))
    ]
    
    st.dataframe(filtered_expenses, use_container_width=True)

    if not filtered_expenses.empty:
        st.download_button(
            label="📥 Download Expense Data",
            data=download_csv(filtered_expenses),
            file_name="personal_expenses.csv",
            mime="text/csv"
        )

def visualize_personal_expenses():
    st.header("Spending Visualization")
    
    # Add category filter for visualizing specific expenses
    selected_category = st.multiselect("Select Categories to Visualize", 
                                       st.session_state.personal_expenses['Category'].unique())
    
    # Filter data based on selected categories
    if selected_category:
        filtered_data = st.session_state.personal_expenses[st.session_state.personal_expenses['Category'].isin(selected_category)]
    else:
        filtered_data = st.session_state.personal_expenses
    
    if not filtered_data.empty:
        # Pie chart for expense distribution
        expense_by_category = filtered_data.groupby("Category")["Amount"].sum()
        fig = px.pie(expense_by_category, values=expense_by_category.values, names=expense_by_category.index, title="Expense Distribution by Category")
        st.plotly_chart(fig)

        # Bar chart for monthly expenses
        filtered_data['Date'] = pd.to_datetime(filtered_data['Date'])
        monthly_expenses = filtered_data.groupby([filtered_data['Date'].dt.to_period('M').astype(str), 'Category'])['Amount'].sum().unstack()
        fig = px.bar(monthly_expenses.reset_index(), x='Date', y=monthly_expenses.columns, title="Monthly Expenses by Category")
        st.plotly_chart(fig)

        # Line chart for cumulative expenses over time
        cumulative_expenses = filtered_data.sort_values('Date').groupby('Date')['Amount'].sum().cumsum().reset_index()
        fig = px.line(cumulative_expenses, x='Date', y='Amount', title="Cumulative Expenses Over Time")
        st.plotly_chart(fig)

    else:
        st.write("No expenses to visualize.")

# Group Expense Splitter Pages
def add_group_expense():
    st.header("👥 Add Group Expense")
    with st.form("add_group_expense_form"):
        description = st.text_input("Description of Expense")
        total_amount = st.number_input("Total Amount", min_value=0.0, step=0.01)
        participants = st.text_input("Participants (comma-separated)").split(",")
        
        st.write("Enter the amount paid by each participant:")
        paid_by = []
        for participant in participants:
            if participant.strip():
                col1, col2 = st.columns([3, 1])
                with col1:
                    paid_amount = st.slider(f"Amount paid by {participant.strip()}", 
                                            min_value=0, 
                                            max_value=int(total_amount), 
                                            step=1, 
                                            value=0)
                with col2:
                    paid_amount = st.number_input(f"or enter amount for {participant.strip()}", 
                                                  min_value=0, 
                                                  max_value=int(total_amount), 
                                                  step=1, 
                                                  value=paid_amount)
                paid_by.append(paid_amount)
        
        submitted = st.form_submit_button("Split Expense")
        if submitted:
            total_paid = sum(paid_by)
            if total_paid != total_amount:
                st.error(f"Total paid (₹{total_paid:.2f}) does not match the total amount (₹{total_amount:.2f}).")
            else:
                per_person = total_amount / len(participants)
                owes = [per_person - paid for paid in paid_by]
                
                new_group_expense = pd.DataFrame({
                    "Description": [description], "Total": [total_amount], 
                    "Participants": [participants], "Paid": [paid_by], "Owes": [owes]
                })
                st.session_state.group_expenses = pd.concat([st.session_state.group_expenses, new_group_expense], ignore_index=True)
                st.success("Group expense added successfully!")

def view_group_balances():
    st.header("💸 View Balances")
    
    if not st.session_state.group_expenses.empty:
        exploded_expenses = st.session_state.group_expenses.explode(["Participants", "Paid", "Owes"])
        st.dataframe(exploded_expenses, use_container_width=True)
        
        balances = exploded_expenses.groupby("Participants")["Owes"].sum()
        st.subheader("Total Balances")
        st.dataframe(balances, use_container_width=True)

        st.download_button(
            label="📥 Download Group Expense Data",
            data=download_csv(exploded_expenses),
            file_name="group_expenses.csv",
            mime="text/csv"
        )
    else:
        st.info("No group expenses added yet. Add some expenses to see the balances!")

def visualize_split_expenses():
    st.header("📊 Split Expense Visualization")
    
    if not st.session_state.group_expenses.empty:
        exploded_expenses = st.session_state.group_expenses.explode(["Participants", "Paid", "Owes"])
        total_paid = exploded_expenses.groupby("Participants")["Paid"].sum()
        fig = px.bar(total_paid, x=total_paid.index, y=total_paid.values, title="Total Expenses Paid by Participant")
        st.plotly_chart(fig, use_container_width=True)

        balances = exploded_expenses.groupby("Participants")["Owes"].sum()
        balance_matrix = pd.DataFrame(index=balances.index, columns=balances.index)
        for payer in balances.index:
            for receiver in balances.index:
                if payer != receiver:
                    balance = balances[payer] - balances[receiver]
                    balance_matrix.loc[payer, receiver] = max(0, balance)
        
        fig = px.imshow(balance_matrix, title="Who Owes Whom", labels=dict(color="Amount Owed"))
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("No group expenses to visualize. Add some group expenses to see the charts!")

# Streamlit App Layout
st.sidebar.markdown("# 📊 Finance Tracker")
st.sidebar.markdown("---")
page = st.sidebar.radio("📍 Navigation", ["🏠 Home", "💰 Personal Expense Tracker", "👥 Expense Splitter"])

if page == "🏠 Home":
    home_page()
elif page == "💰 Personal Expense Tracker":
    st.sidebar.markdown("### Personal Expense Options")
    option = st.sidebar.radio("Choose option", ["📝 Add Expense", "📅 View Expenses", "📊 Visualize Expenses"])
    if option == "📝 Add Expense":
        add_personal_expense()
    elif option == "📅 View Expenses":
        view_personal_expenses()
    elif option == "📊 Visualize Expenses":
        visualize_personal_expenses()
elif page == "👥 Expense Splitter":
    st.sidebar.markdown("### Group Expense Options")
    option = st.sidebar.radio("Choose option", ["📝 Add Group Expense", "💸 View Balances", "📊 Visualize Split Expenses"])
    if option == "📝 Add Group Expense":
        add_group_expense()
    elif option == "💸 View Balances":
        view_group_balances()
    elif option == "📊 Visualize Split Expenses":
        visualize_split_expenses()