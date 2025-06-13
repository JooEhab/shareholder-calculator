import streamlit as st
import json
import os

DATA_FILE = "shareholders_data.json"

# -------------------------
# Language Definitions
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
# State Initialization
# -------------------------
def init_state():
    defaults = {
        "lang": "ar",
        "shareholders": [],
        "total_profit": "",
        "reset_triggered": False
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


# -------------------------
# Localization
# -------------------------
def t(key, **kwargs):
    return LANGUAGES[st.session_state.lang][key].format(**kwargs) if kwargs else LANGUAGES[st.session_state.lang][key]


# -------------------------
# Data Persistence
# -------------------------
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                st.session_state.shareholders = data.get("shareholders", [])
                st.session_state.total_profit = data.get("total_profit", "")
        except Exception as e:
            st.error("❌ Failed to load saved data.")


def save_data():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "shareholders": st.session_state.shareholders,
                "total_profit": st.session_state.total_profit
            }, f, ensure_ascii=False, indent=2)
        st.success("✅ " + t("save"))
    except Exception as e:
        st.error("❌ Failed to save data.")


# -------------------------
# UI Functions
# -------------------------
def reset_data():
    st.session_state.reset_triggered = True
    st.experimental_rerun()


def apply_reset():
    st.session_state.shareholders = []
    st.session_state.total_profit = ""
    st.session_state.reset_triggered = False
    st.success(t("reset_done"))


def add_shareholder(name, shares):
    try:
        shares = float(shares)
        if not name.strip() or shares <= 0:
            raise ValueError
        st.session_state.shareholders.append({"name": name.strip(), "shares": shares})
    except ValueError:
        st.warning(t("error_input"))


def display_shareholders():
    if not st.session_state.shareholders:
        return

    st.subheader("📋")
    for i, sh in enumerate(st.session_state.shareholders):
        col1, col2, col3 = st.columns([3, 1, 1])
        col1.markdown(f"- **{sh['name']}** – {sh['shares']}")
        if col2.button(t("edit"), key=f"edit_{i}"):
            with st.expander(t("edit") + f": {sh['name']}", expanded=True):
                new_name = st.text_input("Name", value=sh["name"], key=f"name_{i}")
                new_shares = st.text_input("Shares", value=str(sh["shares"]), key=f"shares_{i}")
                if st.button("✔️ Save", key=f"save_{i}"):
                    try:
                        st.session_state.shareholders[i] = {
                            "name": new_name.strip(),
                            "shares": float(new_shares)
                        }
                        st.experimental_rerun()
                    except ValueError:
                        st.warning(t("error_input"))
        if col3.button(t("delete"), key=f"delete_{i}"):
            st.session_state.shareholders.pop(i)
            st.experimental_rerun()


def calculate_profits():
    try:
        total_profit = float(st.session_state.total_profit)
        shareholders = st.session_state.shareholders
        total_shares = sum(s["shares"] for s in shareholders)

        if total_shares == 0:
            st.warning(t("no_shares"))
            return

        st.markdown(f"### {t('total_profit_val', val=total_profit)}")
        st.markdown(f"### {t('total_shares', val=total_shares)}")
        for s in shareholders:
            percent = (s["shares"] / total_shares) * 100
            profit = (s["shares"] / total_shares) * total_profit
            st.text(t("result_item", name=s["name"], shares=s["shares"], percent=percent, profit=profit))

    except ValueError:
        st.error(t("error_profit"))


# -------------------------
# App Start
# -------------------------
init_state()
load_data()

# Language Selector
lang_options = {"العربية": "ar", "English": "en"}
selected_lang = st.sidebar.selectbox("🌐 " + t("language"), options=list(lang_options.keys()))
st.session_state.lang = lang_options[selected_lang]

# Title
st.title(t("title"))

# Input Form
with st.form("add_form"):
    name = st.text_input(t("name"))
    shares = st.text_input(t("shares"))
    if st.form_submit_button(t("add")):
        add_shareholder(name, shares)

# Shareholders Table
display_shareholders()

# Profit Input
st.text_input(t("total_profit"), key="total_profit")

# Buttons
colA, colB, colC = st.columns(3)
with colA:
    if st.button(t("calculate")):
        calculate_profits()
with colB:
    if st.button(t("reset")):
        reset_data()
with colC:
    if st.button(t("save")):
        save_data()

# Post-reset logic
if st.session_state.reset_triggered:
    apply_reset()
