import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
from getpass import getpass

# Function to connect to the MySQL database
def connect_to_database():
    """
    Establishes a connection to the MySQL database using user-provided credentials.

    This function creates a sidebar in the Streamlit app for database connection,
    prompts the user for MySQL username and password, and attempts to connect
    to the 'analyze_personal_expenses' database on localhost.

    Returns:
    mysql.connector.connection.MySQLConnection or None: A connection object if
    the connection is successful, or None if there's an error or missing credentials.

    Side effects:
    - Displays a title, input fields, and status messages in the Streamlit sidebar.
    - May raise mysql.connector.Error if there's a problem with the database connection.
    """
    st.sidebar.title("Database Connection")
    username = st.sidebar.text_input("Enter MySQL username")
    password = st.sidebar.text_input("Enter MySQL password", type="password")

    if username and password:
        try:
            database = mysql.connector.connect(
                host="localhost",
                user=username,
                password=password,
                database="analyze_personal_expenses"
            )
            st.sidebar.success("Connected to the database!")
            return database
        except mysql.connector.Error as err:
            st.sidebar.error(f"Error: {err}")
            return None
    else:
        st.sidebar.warning("Please enter your MySQL username and password.")
        return None



# Function to execute a query and return a DataFrame
def run_query(database, query):
    """
    Execute a SQL query on the given database and return the results as a pandas DataFrame.

    This function creates a cursor, executes the provided query, fetches all results,
    extracts column names, and constructs a DataFrame from the results.
    Parameters:
    database (mysql.connector.connection.MySQLConnection): A connected MySQL database object.
    query (str): The SQL query to execute.

    Returns:
    pandas.DataFrame: A DataFrame containing the query results, with columns named
                      according to the SQL query's result set.
    """
    cursor = database.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    cursor.close()
    return pd.DataFrame(result, columns=columns)

# Main Streamlit app
def main():
    st.title("Personal Expense Tracker")
    st.markdown("### Analyze your spending habits with interactive visualizations.")

    # Connect to the database
    database = connect_to_database()
    if not database:
        return

    # List of queries
    queries = {
    "Total Transactions": "SELECT COUNT(*) FROM PERSONAL_EXPENSES",
    "Total Amount Spent": "SELECT SUM(`Amount Paid`) FROM PERSONAL_EXPENSES",
    "Spending by Category": "SELECT Category, SUM(`Amount Paid`) AS total_spent FROM PERSONAL_EXPENSES GROUP BY Category",
    "Payment Mode Distribution": "SELECT `Payment Mode`, COUNT(*) FROM PERSONAL_EXPENSES GROUP BY `Payment Mode`",
    "Top 10 Descriptions by Amount": "SELECT Description, SUM(`Amount Paid`) FROM PERSONAL_EXPENSES GROUP BY Description ORDER BY SUM(`Amount Paid`) DESC LIMIT 10",
    "Transactions Above 40,000": "SELECT * FROM PERSONAL_EXPENSES WHERE `Amount Paid` > 40000",
    "Daily Spending Trend": "SELECT Date, SUM(`Amount Paid`) FROM PERSONAL_EXPENSES GROUP BY Date ORDER BY Date",
    "Average Spending per Category": "SELECT Category, AVG(`Amount Paid`) FROM PERSONAL_EXPENSES GROUP BY Category",
    "Categories with More Than 50 Transactions": "SELECT Category, COUNT(*) FROM PERSONAL_EXPENSES GROUP BY Category HAVING COUNT(*) > 50",
    "Max Amount Spent in Each Category": "SELECT Category, MAX(`Amount Paid`) FROM PERSONAL_EXPENSES GROUP BY Category",
    "Most Frequent Descriptions": "SELECT Description, COUNT(*) FROM PERSONAL_EXPENSES GROUP BY Description ORDER BY COUNT(*) DESC LIMIT 30",
    "Transactions with Cashback > 500": "SELECT * FROM PERSONAL_EXPENSES WHERE Cashback > 500",
    "Daily Cashback Trend": "SELECT Date, SUM(Cashback) FROM PERSONAL_EXPENSES GROUP BY Date ORDER BY Date",
    "Total Cashback Received": "SELECT SUM(Cashback) AS Total_Cashback FROM PERSONAL_EXPENSES",
    "Top 5 Most Expensive Categories": "SELECT Category, SUM(`Amount Paid`) AS Total_Spent FROM PERSONAL_EXPENSES GROUP BY Category ORDER BY Total_Spent DESC LIMIT 5",
    "Transportation Spending by Payment Mode": "SELECT `Payment Mode`, SUM(`Amount Paid`) AS Total_Spent FROM PERSONAL_EXPENSES WHERE Category = 'Transportation' GROUP BY `Payment Mode`",
    "Transactions with Cashback": "SELECT * FROM PERSONAL_EXPENSES WHERE Cashback > 0",
    "Monthly Spending": "SELECT DATE_FORMAT(Date, '%Y-%m') AS Month, SUM(`Amount Paid`) AS Total_Spent FROM PERSONAL_EXPENSES GROUP BY Month",
    "Highest Spending Months for Travel, Entertainment, Gifts": "SELECT DATE_FORMAT(Date, '%Y-%m') AS Month, Category, SUM(`Amount Paid`) AS Total_Spent FROM PERSONAL_EXPENSES WHERE Category IN ('Travel', 'Entertainment', 'Gifts') GROUP BY Month, Category ORDER BY Total_Spent DESC",
    "Recurring Expenses by Month": "SELECT DATE_FORMAT(Date, '%Y-%m') AS Month, Category, SUM(`Amount Paid`) AS Total_Spent FROM PERSONAL_EXPENSES WHERE Category IN ('Insurance', 'Property Taxes') GROUP BY Month, Category",
    "Monthly Cashback": "SELECT DATE_FORMAT(Date, '%Y-%m') AS Month, SUM(Cashback) AS Total_Cashback FROM PERSONAL_EXPENSES GROUP BY Month",
    "Overall Spending Trend": "SELECT DATE_FORMAT(Date, '%Y-%m') AS Month, SUM(`Amount Paid`) AS Total_Spent FROM PERSONAL_EXPENSES GROUP BY Month ORDER BY Month",
    "Travel Costs by Type": "SELECT Description, SUM(`Amount Paid`) AS Total_Spent FROM PERSONAL_EXPENSES WHERE Category = 'Travel' GROUP BY Description",
    "Grocery Spending Patterns": "SELECT DAYOFWEEK(Date) AS DayOfWeek, SUM(`Amount Paid`) AS Total_Spent FROM PERSONAL_EXPENSES WHERE Category = 'Groceries' GROUP BY DayOfWeek",
    "High and Low Priority Categories": "SELECT Category, SUM(`Amount Paid`) AS Total_Spent FROM PERSONAL_EXPENSES GROUP BY Category ORDER BY Total_Spent DESC",
    "Category Contribution to Total Spending": "SELECT Category, SUM(`Amount Paid`) * 100.0 / (SELECT SUM(`Amount Paid`) FROM PERSONAL_EXPENSES) AS Percentage FROM PERSONAL_EXPENSES GROUP BY Category ORDER BY Percentage DESC",
}

    # Dropdown to select a query,
    
    query_option = st.selectbox("Select a Query to Analyze", list(queries.keys()))

    # Execute the selected query
    query = queries[query_option]
    result_df = run_query(database, query)

    # Display the query results
    st.write(f"### {query_option}")
    st.write(result_df)

    # Visualizations based on the selected query
    if query_option == "Spending by Category":
        fig = px.bar(result_df, x="Category", y="total_spent", color="Category", title="Total Spending by Category", text="total_spent")
        st.plotly_chart(fig)

    elif query_option == "Payment Mode Distribution":
        fig = px.pie(result_df, values="COUNT(*)", names="Payment Mode", title="Distribution of Payment Modes", color="Payment Mode")
        st.plotly_chart(fig)

    elif query_option == "Top 10 Descriptions by Amount":
        fig = px.bar(result_df, x="Description", y="SUM(`Amount Paid`)", title="Top 10 Descriptions by Total Amount Paid", color="SUM(`Amount Paid`)")
        st.plotly_chart(fig)

    elif query_option == "Transactions Above 40,000":
        fig = px.bar(result_df, x="Category", y="Amount Paid", title="Transactions Above 40,000 by Category", color="Amount Paid")
        st.plotly_chart(fig)

    elif query_option == "Daily Spending Trend":
        fig = px.line(result_df, x="Date", y="SUM(`Amount Paid`)", title="Daily Spending Trend", markers=True)
        st.plotly_chart(fig)

    elif query_option == "Average Spending per Category":
        fig = px.bar(result_df, x="Category", y="AVG(`Amount Paid`)", title="Average Spending per Category", color="AVG(`Amount Paid`)")
        st.plotly_chart(fig)

    elif query_option == "Categories with More Than 50 Transactions":
        fig = px.bar(result_df, x="Category", y="COUNT(*)", title="Categories with More Than 50 Transactions", color="Category")
        st.plotly_chart(fig)

    elif query_option == "Max Amount Spent in Each Category":
        fig = px.bar(result_df, x="Category", y="MAX(`Amount Paid`)", title="Max Amount Spent in Each Category", color="Category")
        st.plotly_chart(fig)

    elif query_option == "Most Frequent Descriptions":
        fig = px.bar(result_df, x="Description", y="COUNT(*)", title="Most Frequent Descriptions", color="COUNT(*)")
        st.plotly_chart(fig)

    elif query_option == "Transactions with Cashback > 500":
        fig = px.bar(result_df, x="Description", y="Cashback", title="Transactions with Cashback > 500", color="Cashback")
        st.plotly_chart(fig)

    elif query_option == "Daily Cashback Trend":
        fig = px.line(result_df, x="Date", y="SUM(Cashback)", title="Daily Cashback Trend", markers=True)
        st.plotly_chart(fig)


    elif query_option == "Total Cashback Received":
        st.write(f"Total Cashback Received: {result_df.iloc[0, 0]}")

    elif query_option == "Top 5 Most Expensive Categories":
        fig = px.bar(result_df, x="Category", y="Total_Spent", title="Top 5 Most Expensive Categories", color="Category")
        st.plotly_chart(fig)

    elif query_option == "Transportation Spending by Payment Mode":
        fig = px.bar(result_df, x="Payment Mode", y="Total_Spent", title="Transportation Spending by Payment Mode", color="Payment Mode")
        st.plotly_chart(fig)

    elif query_option == "Transactions with Cashback":
        fig = px.bar(result_df, x="Category", y="Cashback", title="Transactions with Cashback", color="Cashback")
        st.plotly_chart(fig)

    elif query_option == "Monthly Spending":
        fig = px.line(result_df, x="Month", y="Total_Spent", title="Monthly Spending Trend", markers=True)
        st.plotly_chart(fig)

    elif query_option == "Highest Spending Months for Travel, Entertainment, Gifts":
        fig = px.bar(result_df, x="Month", y="Total_Spent", color="Category", title="Highest Spending Months for Travel, Entertainment, Gifts")
        st.plotly_chart(fig)

    elif query_option == "Recurring Expenses by Month":
        fig = px.bar(result_df, x="Month", y="Total_Spent", color="Category", title="Recurring Expenses by Month")
        st.plotly_chart(fig)

    elif query_option == "Monthly Cashback":
        fig = px.line(result_df, x="Month", y="Total_Cashback", title="Monthly Cashback Trend", markers=True)
        st.plotly_chart(fig)

    elif query_option == "Overall Spending Trend":
        fig = px.line(result_df, x="Month", y="Total_Spent", title="Overall Spending Trend", markers=True)
        st.plotly_chart(fig)

    elif query_option == "Travel Costs by Type":
        fig = px.bar(result_df, x="Description", y="Total_Spent", title="Travel Costs by Type", color="Description")
        st.plotly_chart(fig)

    elif query_option == "Grocery Spending Patterns":
        fig = px.bar(result_df, x="DayOfWeek", y="Total_Spent", title="Grocery Spending Patterns by Day of Week", color="DayOfWeek")
        st.plotly_chart(fig)

    elif query_option == "High and Low Priority Categories":
        fig = px.bar(result_df, x="Category", y="Total_Spent", title="High and Low Priority Categories", color="Category")
        st.plotly_chart(fig)

    elif query_option == "Category Contribution to Total Spending":
        fig = px.pie(result_df, values="Percentage", names="Category", title="Category Contribution to Total Spending")
        st.plotly_chart(fig)

    # Close the database connection
    database.close()

# Run the app
if __name__ == "__main__":
    main()