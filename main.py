import pandas as pd
import os
from datetime import datetime

class FamilyMember:
    def __init__(self, name, earning_status, earnings):
        self.name = name
        self.earning_status = earning_status
        self.earnings = earnings

class Expense:
    def __init__(self, value, category, description, date):
        self.value = value
        self.category = category
        self.description = description
        self.date = date

class FamilyExpenseTracker:
    def __init__(self):
        self.file_name = "family_expenses.csv"
        self.members = []       # <--- अब ऐप को यह मिल जाएगा और एरर नहीं आएगी!
        self.expense_list = []  # <--- एक्सपेंस लिस्ट भी इनिशियलाइज कर दी
        
        # अगर डेटा फ़ाइल पहले से नहीं बनी है, तो हेडिंग्स के साथ बना लें
        if not os.path.exists(self.file_name):
            df = pd.DataFrame(columns=["Date", "Month", "Category", "Description", "Amount", "Type"])
            df.to_csv(self.file_name, index=False)

    def add_family_member(self, name, earning_status, earnings):
        """नया फैमिली मेंबर लिस्ट में जोड़ने के लिए"""
        member = FamilyMember(name, earning_status, earnings)
        self.members.append(member)
        return member

    def update_family_member(self, member, earning_status, earnings):
        """मौजूद मेंबर का डेटा अपडेट करने के लिए"""
        member.earning_status = earning_status
        member.earnings = earnings

    def delete_family_member(self, member):
        """फैमिली मेंबर को लिस्ट से हटाने के लिए"""
        if member in self.members:
            self.members.remove(member)

    def merge_similar_category(self, value, category, description, date):
        """नया खर्चा लिस्ट में जोड़ने के लिए"""
        expense = Expense(value, category, description, date)
        self.expense_list.append(expense)

    def delete_expense(self, expense):
        """खर्चे को लिस्ट से हटाने के लिए"""
        if expense in self.expense_list:
            self.expense_list.remove(expense)

    def calculate_total_earnings(self):
        """कुल कमाई का हिसाब लगाने के लिए"""
        return sum(m.earnings for m in self.members)

    def calculate_total_expenditure(self):
        """कुल खर्चों का हिसाब लगाने के लिए"""
        return sum(e.value for e in self.expense_list)