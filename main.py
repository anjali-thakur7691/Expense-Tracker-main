import pandas as pd
import os
from datetime import datetime

class FamilyExpenseTracker:
    def __init__(self):
        self.file_name = "family_expenses.csv"
        # अगर डेटा फ़ाइल पहले से नहीं बनी है, तो हेडिंग्स के साथ बना लें
        if not os.path.exists(self.file_name):
            df = pd.DataFrame(columns=["Date", "Month", "Member", "Category", "Amount", "Type"])
            df.to_csv(self.file_name, index=False)

    def add_entry(self, date_obj, member, category, amount, entry_type):
        """नया डेटा एक्सेल/CSV फ़ाइल में हमेशा के लिए सेव करने के लिए"""
        # तारीख से महीने का नाम (जैसे July 2026) अलग निकालना हिस्ट्री के लिए
        month_name = date_obj.strftime("%B %Y")
        
        new_data = {
            "Date": [date_obj.strftime("%Y-%m-%d")],
            "Month": [month_name],
            "Member": [member],
            "Category": [category],
            "Amount": [float(amount)],
            "Type": [entry_type]
        }
        new_df = pd.DataFrame(new_data)
        # mode='a' से पुराना डेटा डिलीट नहीं होता, नया नीचे जुड़ता जाता है
        new_df.to_csv(self.file_name, mode='a', header=False, index=False)
        return True

    def get_all_expenses(self):
        """फ़ाइल से सारा डेटा लोड करने के लिए"""
        if os.path.exists(self.file_name) and os.path.getsize(self.file_name) > 10:
            return pd.read_csv(self.file_name)
        return pd.DataFrame(columns=["Date", "Month", "Member", "Category", "Amount", "Type"])