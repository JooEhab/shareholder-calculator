import streamlit as st
import json
import os

DATA_FILE = "shareholders_data.json"

# Language dictionary
LANGUAGES = {
    "ar": {
        "title": "برنامج حساب نسب وأرباح المساهمين",
        "name": "اسم المساهم",
        "shares": "عدد الأسهم",
        "total_profit": "إجمالي الأرباح",
        "add": "➕ إضافة",
        "edit": "✏️ تعديل المحدد",
        "delete": "🗑️ حذف المحدد",
        "calculate": "🧮 حساب الأرباح",
        "reset": "🔁 إعادة تعيين",
        "error_input": "❌ أدخل بيانات صحيحة",
        "error_profit": "❌ أدخل رقماً صحيحاً في خانة الأرباح",
        "no_shares": "⚠️ لا يوجد أسهم لحساب الأرباح",
        "total_profit_val": "إجمالي الأرباح: {}",
        "total_shares": "إجمالي الأسهم: {}",
        "result_item": "{}:\n - الأسهم: {}\n - النسبة: {:.2f}%\n - الأرباح: {:.2f}",
        "language": "اللغة"
    },
    "en": {
        "title": "Shareholder Profit Calculator",
        "name": "Shareholder Name",
        "shares": "Number of Shares",
        "total_profit": "Total Profit",
        "add": "➕ Add",
        "edit": "✏️ Edit Selected",
        "delete": "🗑️ Delete Selected",
        "calculate": "🧮 Calculate Profits",
        "reset": "🔁 Reset All",
        "error_input": "❌ Please enter valid input.",
        "error_profit": "❌ Please enter a valid number in the Total Profit field.",
        "no_shares": "⚠️ No shares to calculate profits.",
        "total_profit_val": "Total Profit: {}",
        "total_shares": "Total Shares: {}",
        "result_item": "{}:\n - Shares: {}\n - Percentage: {:.2f}%\n - Profit: {:.2f}",
        "language": "Language"
    }
}

# Load data
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"shareholders": [], "total_profit": ""}

# Save data
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Initial load
if "data" not in st.session_state:
    st.session_state.data = load_data()

if "selected_index" not in st.session_state:
    st.session_state.selected_index = None

# Language selector
lang_key = st.sidebar.selectbox("🌐 " + LANGUAGES["en"]["language"], ["English", "العربية"])
lang = "ar" if lang_key == "العربية" else "en"
T = LANGUAGES[lang]

st.title(T["title"])

# Input fields
name = st.text_input(T["name"])
shares = st.text_input(T["shares"])
total_profit_input = st.text_input(T["total_profit"], value=st.session_state.data.get("total_profit", ""))

col1, col2, col3 = st.columns(3)

if col1.button(T["add"]):
    try:
        shares_val = float(shares)
        if not name or shares_val <= 0:
            raise ValueError
        st.session_state.data["shareholders"].append({"name": name, "shares": shares_val})
        name = ""
        shares = ""
    except ValueError:
        st.warning(T["error_input"])

if col2.button(T["edit"]):
    idx = st.session_state.selected_index
    if idx is not None:
        try:
            shares_val = float(shares)
            if not name or shares_val <= 0:
                raise ValueError
            st.session_state.data["shareholders"][idx] = {"name": name, "shares": shares_val}
            st.session_state.selected_index = None
        except ValueError:
            st.warning(T["error_input"])

if col3.button(T["delete"]):
    idx = st.session_state.selected_index
    if idx is not None:
        st.session_state.data["shareholders"].pop(idx)
        st.session_state.selected_index = None

# Show current shareholders
st.subheader("📋 " + T["name"] + " / " + T["shares"])
for i, sh in enumerate(st.session_state.data["shareholders"]):
    label = f"{sh['name']} - {sh['shares']} 📌"
    if st.button(label, key=f"select_{i}"):
        name = sh["name"]
        shares = str(sh["shares"])
        st.session_state.selected_index = i

# Calculation
if st.button("🧮 " + T["calculate"]):
    st.session_state.data["total_profit"] = total_profit_input
    try:
        total_profit = float(total_profit_input)
        valid_shareholders = st.session_state.data["shareholders"]
        total_shares = sum(s["shares"] for s in valid_shareholders)

        if total_shares == 0:
            st.warning(T["no_shares"])
        else:
            st.info(T["total_profit_val"].format(total_profit))
            st.info(T["total_shares"].format(total_shares))
            for s in valid_shareholders:
                percent = (s["shares"] / total_shares) * 100
                profit = (s["shares"] / total_shares) * total_profit
                st.text(T["result_item"].format(s["name"], s["shares"], percent, profit))

    except ValueError:
        st.error(T["error_profit"])

# Reset all
if st.button("🔁 " + T["reset"]):
    st.session_state.data = {"shareholders": [], "total_profit": ""}
    st.session_state.selected_index = None
    name = ""
    shares = ""
    st.success("✅ " + T["reset"])

# Save on app rerun
save_data(st.session_state.data)
