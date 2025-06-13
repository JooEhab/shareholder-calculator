import streamlit as st
import json
import os

DATA_FILE = "shareholders_data.json"

# -------------------------
# Language Configuration
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
# Initialize App State
# -------------------------
def init_state():
    if "lang" not in st.session_state:
        st.session_state.lang = "ar"
    if "shareholders" not in st.session_state:
        st.session_state.shareholders = []
    if "reset_flag" not in st.session_state:
        st.session_state.reset_flag = False
    if "total_profit_input" not in st.session_state:
        st.session_state.total_profit_input = ""
    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = None


def t(key, **kwargs):
    lang = st.session_state.lang
    return LANGUAGES[lang][key].format(**kwargs) if kwargs else LANGUAGES[lang][key]


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                st.session_state.shareholders = data.get("shareholders", [])
                st.session_state.total_profit_input = data.get("total_profit", "")
        except Exception:
            st.error("❌ Failed to load data")


def save_data():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "shareholders": st.session_state.shareholders,
                "total_profit": st.session_state.total_profit_input
            }, f, ensure_ascii=False, indent=2)
        st.success("✅ " + t("save"))
    except Exception:
        st.error("❌ Failed to save data")


# -------------------------
# Reset Handling
# -------------------------
def trigger_reset():
    st.session_state.reset_flag = True
    st.rerun()


def perform_reset():
    st.session_state.shareholders = []
    st.session_state.total_profit_input = ""
    st.session_state.reset_flag = False
    st.success(t("reset_done"))


# -------------------------
# App Logic
# -------------------------
init_state()

if st.session_state.reset_flag:
    perform_reset()

load_data()

# -------------------------
# Sidebar Language Switch
# -------------------------
lang_label = st.sidebar.selectbox("🌐 " + t("language"), ["العربية", "English"])
st.session_state.lang = "ar" if lang_label == "العربية" else "en"

# -------------------------
# App Title
# -------------------------
st.title(t("title"))

# -------------------------
# Shareholder Form
# -------------------------
with st.form("add_form"):
    name = st.text_input(t("name"))
    shares = st.text_input(t("shares"))
    submitted = st.form_submit_button(t("add"))

    if submitted:
        try:
            shares_val = float(shares)
            if not name.strip() or shares_val <= 0:
                raise ValueError
            st.session_state.shareholders.append({"name": name.strip(), "shares": shares_val})
        except ValueError:
            st.warning(t("error_input"))

# -------------------------
# Display Shareholders
# -------------------------
if st.session_state.shareholders:
    for i, sh in enumerate(st.session_state.shareholders):
        col1, col2, col3 = st.columns([3, 1, 1])
        col1.markdown(f"- **{sh['name']}** – {sh['shares']}")

        if col2.button(t("edit"), key=f"edit_{i}"):
            st.session_state.edit_mode = i

        if col3.button(t("delete"), key=f"delete_{i}"):
            st.session_state.shareholders.pop(i)
            st.rerun()

    # Editing Form
    if st.session_state.edit_mode is not None:
        idx = st.session_state.edit_mode
        sh = st.session_state.shareholders[idx]
        with st.form("edit_form"):
            new_name = st.text_input(t("name"), value=sh["name"])
            new_shares = st.text_input(t("shares"), value=str(sh["shares"]))
            save_btn = st.form_submit_button("✔️ Save")
            if save_btn:
                try:
                    st.session_state.shareholders[idx] = {
                        "name": new_name.strip(),
                        "shares": float(new_shares)
                    }
                    st.session_state.edit_mode = None
                    st.rerun()
                except ValueError:
                    st.warning(t("error_input"))

# -------------------------
# Profit Calculation Section
# -------------------------
st.text_input(t("total_profit"), key="total_profit_input")

if st.button(t("calculate")):
    try:
        profit_total = float(st.session_state.total_profit_input)
        shareholders = st.session_state.shareholders
        total_shares = sum(s["shares"] for s in shareholders)

        if total_shares == 0:
            st.warning(t("no_shares"))
        else:
            st.markdown(f"### {t('total_profit_val', val=profit_total)}")
            st.markdown(f"### {t('total_shares', val=total_shares)}")
            for s in shareholders:
                percent = (s["shares"] / total_shares) * 100
                profit = (s["shares"] / total_shares) * profit_total
                st.text(t("result_item", name=s["name"], shares=s["shares"], percent=percent, profit=profit))
    except ValueError:
        st.error(t("error_profit"))

# -------------------------
# Footer Controls
# -------------------------
col1, col2 = st.columns(2)
if col1.button(t("reset")):
    trigger_reset()

if col2.button(t("save")):
    save_data()
