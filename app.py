import streamlit as st
from main import FamilyExpenseTracker
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu
from pathlib import Path

# Streamlit configuration
st.set_page_config(page_title="Family Expense Tracker", page_icon="💰")
st.title("")  # Clear the default title

# Path Settings
current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
css_file = current_dir / "styles" / "main.css"

if css_file.exists():
    with open(css_file, encoding="utf-8") as f:
        st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)

# Create a session state object
session_state = st.session_state
file_name = "family_expenses.csv"

# Check if the 'expense_tracker' object exists in the session state
if "expense_tracker" not in session_state:
    session_state.expense_tracker = FamilyExpenseTracker()
    
    # 🔄 CSV फ़ाइल से पुराना सारा डेटा उठाकर ओरिजिनल ट्रैकर में लोड करना
    if os.path.exists(file_name) and os.path.getsize(file_name) > 10:
        try:
            old_df = pd.read_csv(file_name)
            for _, row in old_df.iterrows():
                if row["Type"] in ["Income", "Non-Earning"]:
                    name_part = str(row["Description"]).replace("Member: ", "").strip()
                    is_earning = True if row["Type"] == "Income" else False
                    existing = [m for m in session_state.expense_tracker.members if m.name == name_part]
                    if not existing:
                        session_state.expense_tracker.add_family_member(name_part, is_earning, int(row["Amount"]))
                elif row["Type"] == "Expense":
                    dt_obj = datetime.strptime(str(row["Date"]), "%Y-%m-%d").date()
                    session_state.expense_tracker.merge_similar_category(
                        int(row["Amount"]), row["Category"], row["Description"], dt_obj
                    )
        except Exception as e:
            pass

# Center-align the heading using HTML
st.markdown(
    '<h1 style="text-align: center;">Family Expense Tracker</h1>',
    unsafe_allow_html=True,
)

# Navigation Menu
selected = option_menu(
    menu_title=None,
    options=["Data Entry", "Data Overview", "Data Visualization"],
    icons=[
        "pencil-fill",
        "clipboard2-data",
        "bar-chart-fill",
    ],
    orientation="horizontal",
)

expense_tracker = session_state.expense_tracker

# --- DATA ENTRY TAB ---
if selected == "Data Entry":
    st.header("Add Family Member")
    with st.expander("Add Family Member", expanded=True):
        member_name = st.text_input("Name").title()
        earning_status = st.checkbox("Earning Status")
        if earning_status:
            earnings = st.number_input("Earnings", value=1, min_value=1)
        else:
            earnings = 0

        if st.button("Add Member"):
            if member_name:
                try:
                    existing_members = [m for m in expense_tracker.members if m.name == member_name]
                    if not existing_members:
                        expense_tracker.add_family_member(member_name, earning_status, earnings)
                    else:
                        expense_tracker.update_family_member(existing_members[0], earning_status, earnings)
                    
                    current_month = datetime.now().strftime("%B %Y")
                    current_date = datetime.now().strftime("%Y-%m-%d")
                    
                    new_data = pd.DataFrame([{
                        "Date": current_date,
                        "Month": current_month,
                        "Category": "Initial/Income",
                        "Description": f"Member: {member_name}",
                        "Amount": earnings,
                        "Type": "Income" if earning_status else "Non-Earning"
                    }])
                    
                    if not os.path.exists(file_name) or os.path.getsize(file_name) <= 10:
                        new_data.to_csv(file_name, index=False)
                    else:
                        new_data.to_csv(file_name, mode='a', header=False, index=False)
                        
                    st.success(f"Successfully Added: Member '{member_name}' with ₹{earnings} earnings!")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Please enter a valid member name.")

    st.header("Add Expenses")
    with st.expander("Add Expenses", expanded=True):
        expense_category = st.selectbox(
            "Category",
            ("Housing", "Food", "Transportation", "Entertainment", "Child-Related", "Medical", "Investment", "Miscellaneous"),
        )
        expense_description = st.text_input("Description (optional)").title()
        expense_value = st.number_input("Value", min_value=0)
        expense_date = st.date_input("Date", value=datetime.today())

        if st.button("Add Expense"):
            if expense_value > 0:
                try:
                    expense_tracker.merge_similar_category(
                        expense_value, expense_category, expense_description, expense_date
                    )
                    
                    formatted_date = expense_date.strftime("%Y-%m-%d")
                    expense_month = expense_date.strftime("%B %Y")
                    
                    new_expense = pd.DataFrame([{
                        "Date": formatted_date,
                        "Month": expense_month,
                        "Category": expense_category,
                        "Description": expense_description if expense_description else "No description",
                        "Amount": expense_value,
                        "Type": "Expense"
                    }])
                    
                    if not os.path.exists(file_name) or os.path.getsize(file_name) <= 10:
                        new_expense.to_csv(file_name, index=False)
                    else:
                        new_expense.to_csv(file_name, mode='a', header=False, index=False)
                        
                    st.success(f"Successfully Added: ₹{expense_value} for '{expense_category}'!")
                except ValueError as e:
                    st.error(str(e))
            else:
                st.warning("Expense value must be greater than 0.")

# --- DATA OVERVIEW TAB ---
elif selected == "Data Overview":
    if not expense_tracker.members:
        st.info("Start by adding family members to track your expenses together! Get started by clicking the 'Add Member' from the Data Entry Tab.")
    else:
        st.header("Family Members")
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.write("**Name**")
        col_m2.write("**Earning status**")
        col_m3.write("**Earnings**")
        col_m4.write("**Action**")

        for member in expense_tracker.members:
            col_m1.write(member.name)
            col_m2.write("Earning" if member.earning_status else "Not Earning")
            col_m3.write(f"₹{member.earnings}")
            if col_m4.button(f"Delete {member.name}", key=f"del_mem_{member.name}"):
                expense_tracker.delete_family_member(member)
                st.rerun()

        st.markdown("---")
        st.header("Expenses")
        if not expense_tracker.expense_list:
            st.info("Currently, no expenses have been added. Get started by clicking the 'Add Expenses' from the Data Entry Tab.")
        else:
            col_e1, col_e2, col_e3, col_e4, col_e5 = st.columns(5)
            col_e1.write("**Value**")
            col_e2.write("**Category**")
            col_e3.write("**Description**")
            col_e4.write("**Date**")
            col_e5.write("**Delete**")

            for idx, expense in enumerate(expense_tracker.expense_list):
                col_e1.write(f"₹{expense.value}")
                col_e2.write(expense.category)
                col_e3.write(expense.description)
                col_e4.write(str(expense.date))
                if col_e5.button(f"Delete", key=f"del_exp_{idx}"):
                    expense_tracker.delete_expense(expense)
                    st.rerun()

        st.markdown("---")
        total_earnings = expense_tracker.calculate_total_earnings()
        total_expenditure = expense_tracker.calculate_total_expenditure()
        remaining_balance = total_earnings - total_expenditure
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Earnings", f"₹{total_earnings}")
        c2.metric("Total Expenditure", f"₹{total_expenditure}")
        c3.metric("Remaining Balance", f"₹{remaining_balance}")

# --- DATA VISUALIZATION TAB (टेक्स्ट कलर फिक्स किया हुआ सेक्शन) ---
elif selected == "Data Visualization":
    st.header("Expense Visualization")
    
    if os.path.exists(file_name) and os.path.getsize(file_name) > 10:
        df_viz = pd.read_csv(file_name)
        expense_only = df_viz[df_viz["Type"] == "Expense"]
        
        if not expense_only.empty:
            cat_summary = expense_only.groupby("Category")["Amount"].sum().reset_index()
            expenses = cat_summary["Category"].tolist()
            values = cat_summary["Amount"].tolist()
            
            fig, ax = plt.subplots(figsize=(5, 5), dpi=300)
            
            # टेक्स्ट का कलर गहरे रॉयल ब्लू (#0b1d33) में सेट किया ताकि सफेद पर एकदम साफ दिखे
            ax.pie(
                values,
                labels=expenses,
                autopct="%1.1f%%",
                startangle=140,
                textprops={"fontsize": 9, "color": "#0b1d33", "fontweight": "bold"},
            )
            ax.set_title("Expense Distribution", fontsize=14, fontweight="bold", color="#0b1d33")
            fig.patch.set_facecolor("none")
            ax.set_facecolor("none")
            st.pyplot(fig)
        else:
            st.info("Currently, no expenses have been added to visualize. Please add some expenses first!")
    else:
        st.info("Currently, no expenses have been added to visualize. Please add some expenses first!")

# --- 📊 LIVE MONTHLY HISTORY SECTION ---
st.markdown("---")
st.subheader("📊 Saved Excel Database & Monthly Summary")

if os.path.exists(file_name) and os.path.getsize(file_name) > 10:
    history_df = pd.read_csv(file_name)
    st.write("### All Time Excel Logs")
    st.dataframe(history_df, use_container_width=True)
    
    with st.expander("🛠️ Delete Old History Record From Excel", expanded=False):
        row_to_delete = st.selectbox(
            "Select Row Index to Delete:", 
            options=history_df.index.tolist(),
            format_func=lambda x: f"Row {x}: {history_df.loc[x, 'Date']} | {history_df.loc[x, 'Category']} | ₹{history_df.loc[x, 'Amount']}"
        )
        
        if st.button("🗑️ Permanent Delete Selected Row", type="primary"):
            try:
                history_df = history_df.drop(row_to_delete)
                history_df.to_csv(file_name, index=False)
                st.success(f"Row {row_to_delete} successfully removed from Database!")
                
                if "expense_tracker" in st.session_state:
                    del st.session_state.expense_tracker
                st.rerun()
            except Exception as e:
                st.error(f"Error while deleting: {e}")
    
    expense_only = history_df[history_df["Type"] == "Expense"]
    if not expense_only.empty:
        st.write("### Month-wise Total Expense Summary")
        monthly_summary = expense_only.groupby("Month")["Amount"].sum().reset_index()
        monthly_summary.columns = ["Month", "Total Expense (₹)"]
        st.table(monthly_summary)
else:
    st.info("No permanent history found yet.")