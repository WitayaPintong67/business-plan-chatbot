import streamlit as st
import openai
import json
from planner import (
    get_swot_prompt,
    get_vision_prompt,
    get_strategy_prompt,
    get_marketing_step_prompt,
    get_marketing_summary_prompt,
    get_executive_summary_prompt,
    get_financial_step_prompt
)
from exporter import export_to_docx
from financial_engine import calculate_financials

client = openai.OpenAI(api_key=st.secrets["openai_key"])

# --- Initialize State ---
if "chat_log" not in st.session_state:
    st.session_state.chat_log = [{"role": "system", "content": "You are a business plan assistant that guides users step by step."}]
if "awaiting_input_for" not in st.session_state:
    st.session_state.awaiting_input_for = None
if "marketing_step" not in st.session_state:
    st.session_state.marketing_step = 0
if "marketing_inputs" not in st.session_state:
    st.session_state.marketing_inputs = {}
if "financial_step" not in st.session_state:
    st.session_state.financial_step = 0
if "financial_inputs" not in st.session_state:
    st.session_state.financial_inputs = {}

if "financial_file" not in st.session_state:
    st.session_state.financial_file = None

if "user_input" not in st.session_state:
    st.session_state.user_input = ""
if "language" not in st.session_state:
    st.session_state.language = "en"

st.set_page_config(layout="wide")

# --- Improved Layout Styling ---
st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem;
    }
    .chat-box {
        padding: 28px;
        margin-bottom: 1rem;
    }
    .header-assistant {
        background-color: #dcefd8;
        padding: 10px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 32px;
    }
    .header-user {
        background-color: #dbeaf4;
        padding: 10px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 32px;
    }
    .chat-message {
        font-size: 28px;
        line-height: 1.6;
        padding: 4px 0;
    }
    .title-container {
        background-color: #cce0cc;
        padding: 50px;
        border-radius: 8px;
        margin-bottom: 30px;
    }


    </style>
""", unsafe_allow_html=True)


# --- Title ---
col_title, col_controls = st.columns([9, 3])
with col_title:
    st.markdown("""
        <div class="title-container">
            <h1 style="text-align:center; margin-bottom:5px;font-size: 50px">💼 Dr. Witaya Chat Bot for Business Plan</h1>
            <p style="text-align:center;font-size: 34px">We are business plan assistants that guide you step by step.<br>
            Select the buttons on the right to proceed through the plan.</p>
        </div>
    """, unsafe_allow_html=True)

with col_controls:
    st.markdown("### 🌐 Language") 
    st.session_state.language = st.selectbox("Select Language", ["en", "th"], format_func=lambda x: "English" if x == "en" else "Thai")

    st.markdown("### 🛠️ Input Mode")
    st.session_state.input_mode = st.radio(
        "How should your next input be interpreted?",
        ["Follow Steps", "Free Input"],
        index=0,
        key="input_mode_radio"
    )

# --- Step Buttons ---
st.markdown("### 📌 Plan Steps")
cols_steps = st.columns(7)

step_buttons = [
    ("📄 Provide Business Info", "business_info"),
    ("🚀 Start SWOT Analysis", "swot_strengths"),
    ("🏯 Generate Vision, Mission & Objectives", "vision"),
    ("🧭 Generate Strategies", "strategy"),
    ("📣 Create Marketing Plan", "marketing"),
    ("📃 Generate Executive Summary", "executive"),
    ("💰 Financial Analysis", "financial")
]

# CORRECTED LOOP: Add the 'key' argument
for i, (label, button_key) in enumerate(step_buttons): # Use 'button_key' from the tuple
    with cols_steps[i]:
        # Provide a unique key for each button
        if st.button(label, key=f"step_button_{button_key}"): # Crucial: Unique key here!
            st.session_state.awaiting_input_for = button_key # Use button_key here
            # Your existing logic for button clicks
            if label == "📄 Provide Business Info":
                st.session_state.chat_log.append({"role": "assistant", "content": "Please enter your general business information including:\n- Business name\n- Type of business\n- Services\n- Customers"})
            elif label == "🚀 Start SWOT Analysis":
                st.session_state.chat_log.append({"role": "assistant", "content": get_swot_prompt()})
            elif label == "🏯 Generate Vision, Mission & Objectives":
                reply = client.chat.completions.create(
                    model="gpt-4o",
                    messages=st.session_state.chat_log
                )
                st.session_state.chat_log.append({"role": "assistant", "content": reply.choices[0].message.content})
            elif label == "🧭 Generate Strategies":
                reply = client.chat.completions.create(
                    model="gpt-4o",
                    messages=st.session_state.chat_log + [{"role": "user", "content": get_strategy_prompt()}]
                )
                st.session_state.chat_log.append({"role": "assistant", "content": reply.choices[0].message.content})
            elif label == "📣 Create Marketing Plan":
                st.session_state.awaiting_input_for = "marketing_step"
                st.session_state.marketing_step += 1
                step = st.session_state.marketing_step
                if step <= 5:
                    prompt = get_marketing_step_prompt(step)
                    st.session_state.chat_log.append({"role": "assistant", "content": prompt})
                elif step == 6:
                    final_prompt = get_marketing_summary_prompt(st.session_state.marketing_inputs)
                    reply = client.chat.completions.create(
                        model="gpt-4o",
                        messages=st.session_state.chat_log + [{"role": "user", "content": final_prompt}]
                    )
                    st.session_state.chat_log.append({"role": "assistant", "content": reply.choices[0].message.content})
            elif label == "📃 Generate Executive Summary":
                user_data = {
                    "business_info": st.session_state.chat_log[1]["content"] if len(st.session_state.chat_log) > 1 else "",
                    "swot_summary": "\n".join([m["content"] for m in st.session_state.chat_log if "SWOT" in m["content"]]),
                    "vision_mission": "\n".join([m["content"] for m in st.session_state.chat_log if "Vision" in m["content"]]),
                    "strategy": "\n".join([m["content"] for m in st.session_state.chat_log if "Strategy" in m["content"]]),
                    "marketing": "\n".join([m["content"] for m in st.session_state.chat_log if "Marketing Mix" in m["content"] or "Target Market" in m["content"]])
                }
                final_prompt = get_executive_summary_prompt(st.session_state.language, user_data)
                reply = client.chat.completions.create(
                    model="gpt-4o",
                    messages=st.session_state.chat_log + [{"role": "user", "content": final_prompt}]
                )
                st.session_state.chat_log.append({"role": "assistant", "content": reply.choices[0].message.content})

            # You likely want to rerun after a button click to update the UI
            elif label == "💰 Financial Analysis":
                st.session_state.financial_step = 1
            
            st.rerun()


# --- Chat Display ---
#col1, col2 = st.columns(2)
#with col1:
#    st.markdown("### 🧠 Assistant")
#    for msg in st.session_state.chat_log:
#        if msg["role"] == "assistant":
#            st.markdown(f"<div style='padding:8px;'>{msg['content'].replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
#with col2:
#    st.markdown("### 👤 You")
#    for msg in st.session_state.chat_log:
#        if msg["role"] == "user":
#            st.markdown(f"<div style='padding:8px;'>{msg['content'].replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

# --- Chat Display Area ---

# --- File Buttons ---
st.markdown("### 📁 File Operations")
col_save, col_load, col_export = st.columns(3)
with col_save:
    if st.button("💾 Save Chat History", key="save_chat_history_btn"): # Added key
        with open("chat_history.json", "w", encoding="utf-8") as f:
            json.dump(st.session_state.chat_log, f, ensure_ascii=False, indent=2)
        st.success("✅ Chat saved")

with col_load:
    if st.button("📂 Load Chat History", key="load_chat_history_btn"): # Added key
        try:
            with open("chat_history.json", "r", encoding="utf-8") as f:
                st.session_state.chat_log = json.load(f)
            st.success("✅ Chat loaded")
        except FileNotFoundError:
            st.error("No saved file found")

with col_export:
    if st.button("📝 Export to Word", key="export_to_word_btn"): # Added key
        export_to_docx(st.session_state.chat_log)
        st.success("✅ Exported to Business_Plan.docx")



col_assist, col_you = st.columns(2)

with col_assist:
    st.markdown('<div class="header-assistant" style="text-align:center;">🧠 Assistant (System)</div>', unsafe_allow_html=True)
    for msg in st.session_state.chat_log:
        if msg["role"] == "assistant":
            content_html = msg["content"].replace("\n", "<br>")
            st.markdown(f"<div class='chat-message'><strong>Assistant:</strong> {content_html}</div>", unsafe_allow_html=True)

with col_you:
    st.markdown('<div class="header-user" style="text-align:center;">👤 You (User Input)</div>', unsafe_allow_html=True)
    for msg in st.session_state.chat_log:
        if msg["role"] == "user":
            content_html = msg["content"].replace("\n", "<br>")
            st.markdown(f"<div class='chat-message'><strong>You:</strong> {content_html}</div>", unsafe_allow_html=True)





# --- Status and Input Box ---
st.markdown("---")
st.markdown(f"📌 **Current Step:** {st.session_state.awaiting_input_for or 'None'} | ⚙️ **Mode:** {st.session_state.input_mode}")
st.text_area("✏️ Type your message below", height=200, key="user_input")


if st.button("Send", use_container_width=True, key="send_button"): # Added key for the send button
    message = st.session_state.user_input.strip()
    if message:
        st.session_state.chat_log.append({"role": "user", "content": message})

        if st.session_state.input_mode == "Free Input":
            st.rerun()
        else:
            stage = st.session_state.awaiting_input_for
            if stage == "business_info":
                st.session_state.chat_log.append({"role": "assistant", "content": "Thank you. Your business info has been saved.\nNext, please press 🚀 Start SWOT Analysis to continue."})
                st.session_state.awaiting_input_for = None
            elif stage == "swot_strengths":
                st.session_state.chat_log.append({"role": "assistant", "content": "Thank you. Now enter your Weaknesses.\n🔍 What limitations hold your business back?"})
                st.session_state.awaiting_input_for = "swot_weaknesses"
            elif stage == "swot_weaknesses":
                st.session_state.chat_log.append({"role": "assistant", "content": "Great. Now enter your Opportunities.\n🔍 What market trends or needs can you leverage?"})
                st.session_state.awaiting_input_for = "swot_opportunities"
            elif stage == "swot_opportunities":
                st.session_state.chat_log.append({"role": "assistant", "content": "Thanks. Finally, enter your Threats.\n🔍 What external risks could threaten your success?"})
                st.session_state.awaiting_input_for = "swot_threats"
            elif stage == "swot_threats":
                st.session_state.chat_log.append({"role": "assistant", "content": "Thank you. Now summarizing your SWOT analysis.\nPlease press the button 🏯 Generate Vision, Mission & Objectives."})
                st.session_state.awaiting_input_for = None
            elif stage == "marketing_step":
                step = st.session_state.marketing_step
                st.session_state.marketing_inputs[f"step{step}"] = message
                if step < 5:
                    st.session_state.marketing_step += 1
                    prompt = get_marketing_step_prompt(st.session_state.marketing_step)
                    st.session_state.chat_log.append({"role": "assistant", "content": prompt})
                elif step == 5:
                    summary_prompt = get_marketing_summary_prompt(st.session_state.marketing_inputs)
                    reply = client.chat.completions.create(
                        model="gpt-4o",
                        messages=st.session_state.chat_log + [{"role": "user", "content": summary_prompt}]
                    )
                    st.session_state.chat_log.append({"role": "assistant", "content": reply.choices[0].message.content})
                    st.session_state.awaiting_input_for = None
                    st.success("Marketing Summary generated.")
                #    st.session_state.awaiting_input_for = None

            st.rerun()

# --- Modal Input for Financial Analysis ---
if st.session_state.awaiting_input_for == "financial":

#    st.session_state.financial_step += 1
    step = st.session_state.financial_step



    st.markdown(f"### 💰 Financial Analysis - Step {step}")
    st.info(get_financial_step_prompt(step))
    
    # 🔧 Add the input box ONLY during active step (financial)
    #user_fin_input = st.text_area("✏️ Enter your data for this step", height=200, key="user_input_step")
    #if st.button("Send", use_container_width=True, key="send_button_step"):
    #    if user_fin_input.strip():
    #        st.session_state.chat_log.append({"role": "user", "content": user_fin_input.strip()})
    #        st.session_state.user_input = user_fin_input.strip()
    #        st.rerun()




    with st.form(key=f"fin_step_{step}"):
        if step == 1:
            col1, col2 = st.columns(2)
            with col1:
                initial_investment = st.number_input("Initial Investment", min_value=0.0)
                salvage = st.number_input("Salvage Value", min_value=0.0)
                tax_credit = st.number_input("Tax Credit (e.g., 0.1 = 10%)", min_value=0.0, max_value=1.0)
            with col2:
                lifetime = st.number_input("Lifetime (Years)", min_value=1, step=1)
                depr_method = st.selectbox("Depreciation Method", [1, 2], format_func=lambda x: "Straight Line" if x == 1 else "DDB")
            submitted = st.form_submit_button("Submit Step 1")
            if submitted:
                st.session_state.financial_inputs.update({
                    "initial_investment": initial_investment,
                    "salvage_value": salvage,
                    "tax_credit": tax_credit,
                    "lifetime": int(lifetime),
                    "depr_method": depr_method
                })
                st.session_state.financial_step += 1
                st.rerun()

        elif step == 2:
            with st.expander("Input Cashflow Details"):
                revenue = st.number_input("Revenue Year 1", min_value=0.0)
                mat = st.number_input("COGS - Materials", min_value=0.0)
                labor = st.number_input("COGS - Direct Labor", min_value=0.0)
                rent = st.number_input("Opex - Rent", min_value=0.0)
                sal = st.number_input("Opex - Salaries", min_value=0.0)
                mkt = st.number_input("Opex - Marketing", min_value=0.0)
                supplies = st.number_input("Opex - Office Supplies", min_value=0.0)
                util = st.number_input("Opex - Utilities", min_value=0.0)
                tax = st.number_input("Tax Rate", min_value=0.0, max_value=1.0)
            submitted = st.form_submit_button("Submit Step 2")
            if submitted:
                st.session_state.financial_inputs.update({
                    "revenue_year1": revenue,
                    "cogs_items": {"Materials": mat, "Direct Labor": labor},
                    "opex_items": {"Rent": rent, "Salaries": sal, "Marketing": mkt, "Office Supplies": supplies, "Utilities": util},
                    "tax_rate": tax
                })
                st.session_state.financial_step += 1
                st.rerun()

        # Steps 3–5: (You can continue similarly)
        elif step == 3:
            approach = st.radio("Choose Discount Rate Approach", ["Direct Rate", "CAPM/WACC"])
            if approach == "Direct Rate":
                rate = st.number_input("Discount Rate (e.g., 0.1 for 10%)", min_value=0.0, max_value=1.0)
                submitted = st.form_submit_button("Submit Step 3")
                if submitted:
                    st.session_state.financial_inputs.update({"discount_approach": 1, "discount_rate": rate})
                    st.session_state.financial_step += 1
                    st.rerun()
            else:
                beta = st.number_input("Beta", min_value=0.0)
                risk_free = st.number_input("Risk-Free Rate", min_value=0.0, max_value=1.0)
                premium = st.number_input("Market Premium", min_value=0.0, max_value=1.0)
                debt_ratio = st.number_input("Debt Ratio", min_value=0.0, max_value=1.0)
                cost_of_debt = st.number_input("Cost of Debt", min_value=0.0, max_value=1.0)
                submitted = st.form_submit_button("Submit Step 3")
                if submitted:
                    st.session_state.financial_inputs.update({
                        "discount_approach": 2,
                        "beta": beta,
                        "risk_free": risk_free,
                        "market_premium": premium,
                        "debt_ratio": debt_ratio,
                        "cost_of_debt": cost_of_debt
                    })
                    st.session_state.financial_step += 1
                    st.rerun()

        elif step == 4:
            col1, col2, col3 = st.columns(3)
            with col1:
                initial_wc = st.number_input("Initial Working Capital", min_value=0.0)
            with col2:
                wc_percent = st.number_input("% of Revenue to WC (e.g., 0.2)", min_value=0.0, max_value=1.0)
            with col3:
                wc_salvage = st.number_input("% WC recovered (e.g., 1.0)", min_value=0.0, max_value=1.0)
            submitted = st.form_submit_button("Submit Step 4")
            if submitted:
                st.session_state.financial_inputs.update({
                    "initial_wc": initial_wc,
                    "wc_percent": wc_percent,
                    "wc_salvage": wc_salvage
                })
                st.session_state.financial_step += 1
                st.rerun()

        elif step == 5:
            st.markdown("### 📈 Growth Rate Inputs (Step 5)")
            st.caption("Enter growth rates in this format for each category:\n\n`1-3:0.05; 4-6:0.10; 7-10:0.03`\n\nThis means: 5% for years 1–3, 10% for years 4–6, and 3% for years 7–10.")

            # ✅ Move the function outside the if-block
            def parse_growth_input_fixed(input_str):
                try:
                    segments = input_str.split(";")
                    parsed = []
                    for seg in segments:
                        if not seg.strip():
                            continue
                        yr_part, gr_part = seg.split(":")
                        start, end = map(int, yr_part.strip().split("-"))
                        rate = float(gr_part.strip())
                        parsed.append((start, end, rate))
                    return parsed
                except Exception as e:
                    st.error(f"❌ Invalid format: {e}")
                    return None

            revenue_growth_str = st.text_input("📊 Revenue Growth Ranges", value="1-3:0.05; 4-6:0.10; 7-10:0.03")
            cogs_growth_str = st.text_input("📉 COGS Growth Ranges", value="1-3:0.04; 4-6:0.07; 7-10:0.02")
            opex_growth_str = st.text_input("📈 Operating Expense Growth Ranges", value="1-3:0.03; 4-6:0.05; 7-10:0.01")

            submit_growth = st.form_submit_button("Submit Step 5")

            if submit_growth:
                growth_revenue = parse_growth_input_fixed(revenue_growth_str)
                growth_cogs = parse_growth_input_fixed(cogs_growth_str)
                growth_opex = parse_growth_input_fixed(opex_growth_str)

                if growth_revenue and growth_cogs and growth_opex:
                    st.session_state.financial_inputs.update({
                        "growth_revenue": growth_revenue,
                        "growth_cogs": growth_cogs,
                        "growth_opex": growth_opex
                    })
                    filepath = calculate_financials(st.session_state.financial_inputs)
                    st.session_state.financial_file = filepath
                    st.success("✅ Financial analysis complete.")
                    st.session_state.awaiting_input_for = None
                    st.session_state.financial_step = 0
                    st.rerun()


# --- File Download ---
if st.session_state.financial_file:
    with open(st.session_state.financial_file, "rb") as f:
        st.download_button("📥 Download Financial Excel", f, file_name=st.session_state.financial_file, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")



# --- Chat history toggle ---
if st.checkbox("📜 Show Full Conversation"): # This needs a unique key too if there are other checkboxes
    st.markdown("### Full Chat History")
    for msg in st.session_state.chat_log:
        st.markdown(f"**{msg['role'].capitalize()}:** {msg['content']}")






