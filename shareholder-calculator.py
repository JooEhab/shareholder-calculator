import streamlit as st
import json
import os

# File for saving persistent data
DATA_FILE = "shareholders_data.json"

# -------------------------
# Language Setup
# -------------------------
LANGUAGES = {
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
        "language": "اللغة",
        "save": "💾 حفظ البيانات"
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
        "language": "Language",
        "save": "💾 Save Data"
    }
}

# -------------------------
# Helper Functions
# -------------------------
def t(key, **kwargs):
    return LANGUAGES[st.session_state.lang][key].format(**kwargs) if kwargs else LANGUAGES[st.session_state.lang][key]

def init_state():
    st.session_state.setdefault("lang", "ar")
    st.session_state.setdefault("shareholders", [])
    st.session_state.setdefault("total_profit", "")

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            st.session_state.shareholders = data.get("shareholders", [])
            st.session_state.total_profit = data.get("total_profit", "")

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "shareholders": st.session_state.shareholders,
            "total_profit": st.session_state.total_profit
        }, f, ensure_ascii=False, indent=2)

def add_shareholder(name, shares):
    try:
        shares = float(shares)
        if not name.strip() or shares <= 0:
            raise ValueError
        st.session_state.shareholders.append({"name": name.strip(), "shares": shares})
    except ValueError:
        st.warning(t("error_input"))

def delete_shareholder(index):
    st.session_state.shareholders.pop(index)

def calculate_results():
    try:
        total_profit = float(st.session_state.total_profit)
        valid_shareholders = st.session_state.shareholders
        total_shares = sum(s["shares"] for s in valid_shareholders)

        if total_shares == 0:
            st.warning(t("no_shares"))
            return

        st.markdown(f"### {t('total_profit_val', val=total_profit)}")
        st.markdown(f"### {t('total_shares', val=total_shares)}")

        for s in valid_shareholders:
            percent = (s["shares"] / total_shares) * 100
            profit = (s["shares"] / total_shares) * total_profit
            st.text(t("result_item", name=s["name"], shares=s["shares"], percent=percent, profit=profit))

    except ValueError:
        st.error(t("error_profit"))

def reset_data():
    st.session_state.shareholders = []
    st.session_state.total_profit = ""
    st.success(t("reset_done"))


# -------------------------
# Streamlit App Layout
# -------------------------
init_state()
load_data()

# Sidebar language toggle
lang_options = {"العربية": "ar", "English": "en"}
selected = st.sidebar.selectbox("🌐 " + t("language"), options=list(lang_options.keys()))
st.session_state.lang = lang_options[selected]

st.title(t("title"))

# Form to add new shareholder
with st.form("add_form"):
    name = st.text_input(t("name"))
    shares = st.text_input(t("shares"))
    if st.form_submit_button(t("add")):
        add_shareholder(name, shares)

# Shareholders list
if st.session_state.shareholders:
    st.subheader("📋 " + t("title"))
    for i, sh in enumerate(st.session_state.shareholders):
        col1, col2, col3 = st.columns([3, 1, 1])
        col1.markdown(f"- **{sh['name']}** – {sh['shares']}")
        if col2.button(t("edit"), key=f"edit_{i}"):
            with st.expander(t("edit") + f": {sh['name']}", expanded=True):
                new_name = st.text_input("Name", value=sh["name"], key=f"name_{i}")
                new_shares = st.text_input("Shares", value=str(sh["shares"]), key=f"shares_{i}")
                if st.button("✔️ Save", key=f"save_{i}"):
                    try:
                        st.session_state.shareholders[i] = {"name": new_name.strip(), "shares": float(new_shares)}
                        st.experimental_rerun()
                    except ValueError:
                        st.warning(t("error_input"))
        if col3.button(t("delete"), key=f"delete_{i}"):
            delete_shareholder(i)
            st.experimental_rerun()

# Profit input and calculation
st.text_input(t("total_profit"), key="total_profit")
if st.button(t("calculate")):
    calculate_results()

# Buttons at the bottom
colA, colB, colC = st.columns(3)
with colA:
    if st.button(t("reset")):
        reset_data()
with colB:
    if st.button(t("save")):
        save_data()
        st.success("✅ Saved!")

