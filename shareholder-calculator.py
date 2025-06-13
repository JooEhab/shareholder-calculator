import streamlit as st
import json
import os

DATA_FILE = "shareholders_data.json"

# Initialize session state
if "shareholders" not in st.session_state:
    st.session_state.shareholders = []
if "total_profit" not in st.session_state:
    st.session_state.total_profit = ""

# Language support
languages = {
    "ar": {
        "title": "برنامج حساب نسب وأرباح المساهمين",
        "total_profit": "إجمالي الأرباح:",
        "name": "اسم المساهم:",
        "shares": "عدد الأسهم:",
        "add": "➕ إضافة",
        "calculate": "🧮 حساب الأرباح",
        "reset": "🔁 إعادة",
        "edit": "✏️ تعديل",
        "delete": "🗑️ حذف",
        "error_input": "يرجى إدخال بيانات صحيحة.",
        "error_profit": "يرجى إدخال رقم صحيح في حقل الأرباح.",
        "no_shares": "⚠️ لا يوجد أسهم لحساب الأرباح.",
        "total_profit_val": "إجمالي الأرباح: {val}",
        "total_shares": "إجمالي الأسهم: {val}",
        "result_item": "{name}:\n - الأسهم: {shares}\n - النسبة: {percent:.2f}%\n - الأرباح: {profit:.2f}\n\n",
        "reset_done": "🔄 تمت إعادة تعيين جميع البيانات.",
        "language": "اللغة"
    },
    "en": {
        "title": "Shareholder Profit Calculator",
        "total_profit": "Total Profit:",
        "name": "Shareholder Name:",
        "shares": "Number of Shares:",
        "add": "➕ Add",
        "calculate": "🧮 Calculate Profits",
        "reset": "🔁 Reset",
        "edit": "✏️ Edit",
        "delete": "🗑️ Delete",
        "error_input": "Please enter valid input.",
        "error_profit": "Please enter a valid number in the Total Profit field.",
        "no_shares": "⚠️ No shares to calculate profits.",
        "total_profit_val": "Total Profit: {val}",
        "total_shares": "Total Shares: {val}",
        "result_item": "{name}:\n - Shares: {shares}\n - Percentage: {percent:.2f}%\n - Profit: {profit:.2f}\n\n",
        "reset_done": "🔄 All data has been reset.",
        "language": "Language"
    }
}

# Language switch
lang_map = {"العربية": "ar", "English": "en"}
selected_lang = st.sidebar.selectbox("Language / اللغة", options=list(lang_map.keys()))
lang = lang_map[selected_lang]
t = lambda key, **kwargs: languages[lang][key].format(**kwargs) if kwargs else languages[lang][key]

st.title(t("title"))

# Input form
with st.form("shareholder_form"):
    name = st.text_input(t("name"))
    shares = st.text_input(t("shares"))
    submitted = st.form_submit_button(t("add"))
    if submitted:
        try:
            shares_val = float(shares)
            if name.strip() == "" or shares_val <= 0:
                raise ValueError
            st.session_state.shareholders.append({"name": name.strip(), "shares": shares_val})
        except ValueError:
            st.warning(t("error_input"))

# Display shareholders table
if st.session_state.shareholders:
    for i, sh in enumerate(st.session_state.shareholders):
        col1, col2, col3 = st.columns([3, 1, 1])
        col1.markdown(f"**{sh['name']}** – {sh['shares']}")
        if col2.button(t("edit"), key=f"edit_{i}"):
            name = st.text_input("Edit Name", value=sh['name'], key=f"edit_name_{i}")
            shares = st.text_input("Edit Shares", value=str(sh['shares']), key=f"edit_shares_{i}")
            if st.button("✔️ Save", key=f"save_{i}"):
                try:
                    st.session_state.shareholders[i] = {"name": name, "shares": float(shares)}
                except:
                    st.error(t("error_input"))
        if col3.button(t("delete"), key=f"delete_{i}"):
            st.session_state.shareholders.pop(i)
            st.experimental_rerun()

# Profit input and calculation
st.session_state.total_profit = st.text_input(t("total_profit"), value=st.session_state.total_profit)
if st.button(t("calculate")):
    try:
        total_profit = float(st.session_state.total_profit)
        valid_shareholders = st.session_state.shareholders
        total_shares = sum(s["shares"] for s in valid_shareholders)

        if total_shares == 0:
            st.warning(t("no_shares"))
        else:
            st.markdown(f"### {t('total_profit_val', val=total_profit)}")
            st.markdown(f"### {t('total_shares', val=total_shares)}")
            for s in valid_shareholders:
                percent = (s["shares"] / total_shares) * 100
                profit = (s["shares"] / total_shares) * total_profit
                st.text(t("result_item", name=s["name"], shares=s["shares"], percent=percent, profit=profit))
    except ValueError:
        st.error(t("error_profit"))

# Reset all
if st.button(t("reset")):
    st.session_state.shareholders = []
    st.session_state.total_profit = ""
    st.success(t("reset_done"))

# Save/Load persistence
def save_data():
    data = {
        "shareholders": st.session_state.shareholders,
        "total_profit": st.session_state.total_profit
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                st.session_state.shareholders = data.get("shareholders", [])
                st.session_state.total_profit = data.get("total_profit", "")
        except Exception as e:
            st.error("Failed to load saved data.")

load_data()
st.button("💾 Save", on_click=save_data)
