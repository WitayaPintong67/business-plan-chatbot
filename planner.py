from textwrap import dedent

# Define the updated version of planner.py with HTML prompts

def get_swot_prompt():
    return (
        "<h3>SWOT Analysis</h3>"
        "<p>You're a business advisor guiding a user through a SWOT Analysis. Ask the user to describe:</p>"
        "<b>1. Strengths</b><br>"
        "Questions to consider:<ul>"
        "<li>What internal advantages give your business an edge?</li>"
        "<li>Do you have skilled staff, loyal customers, or strong brand recognition?</li>"
        "</ul>"
        "<b>2. Weaknesses</b><br>"
        "Questions to consider:<ul>"
        "<li>What internal limitations hold your business back?</li>"
        "<li>Do you lack experience, resources, or face quality/service issues?</li>"
        "</ul>"
        "<b>3. Opportunities</b><br>"
        "Questions to consider:<ul>"
        "<li>What external trends or needs can you take advantage of?</li>"
        "<li>Is there a niche in the market you can fill?</li>"
        "</ul>"
        "<b>4. Threats</b><br>"
        "Questions to consider:<ul>"
        "<li>What external risks could threaten your success?</li>"
        "<li>Are there competitors or regulations you should watch?</li>"
        "</ul>"
        "<p><i>Please format your responses clearly. All responses will be saved for summary.</i></p>"
    )

def get_vision_prompt():
    return (
            "<h3>Vision, Mission, and Objectives</h3>"
            "<p>Please help the user define:</p>"
            "<b>Vision:</b> A long-term inspirational statement of what the business aims to become.<br>"
            "<b>Mission:</b> A brief statement explaining the purpose and core values of the business.<br>"
            "<b>Objectives:</b> Specific, measurable goals the business will strive to achieve.<br>"
            "<p>Format the output in clear HTML for display on a web interface.</p>"
        )

def get_strategy_prompt():
    return (
            "<h3>Strategic Plan</h3>"
            "<p>Based on the SWOT and Vision/Mission, please propose 3–5 strategies to help the business grow.</p>"
            "<ul><li>Use strategic language</li><li>Use HTML format for clean rendering</li></ul>"
        )

def get_marketing_step_prompt(step):
        prompts = {
            1: "<h4>Step 1: Define your Target Market</h4><p>Who are your ideal customers? Be specific (e.g., age, income, behavior).</p>",
            2: "<h4>Step 2: Positioning Statement</h4><p>How do you want your product/service to be perceived in the market?</p>",
            3: "<h4>Step 3: Marketing Mix - Product</h4><p>What are the key features and benefits of your offering?</p>",
            4: "<h4>Step 4: Marketing Mix - Price, Place, Promotion</h4><p>Describe your pricing model, distribution, and promotional strategy.</p>",
            5: "<h4>Step 5: Additional Considerations</h4><p>Include customer service, digital marketing, branding ideas.</p>"
        }
        return prompts.get(step, "<p><i>Unknown step.</i></p>")

def get_marketing_summary_prompt(marketing_inputs):
        return (
            "<h3>Marketing Plan Summary</h3>"
            "<p>Use the following data to summarize the business's marketing plan:</p>"
            + "".join(f"<p><b>Step {k[-1]}:</b> {v}</p>" for k, v in marketing_inputs.items()) +
            "<p>Format everything in clean HTML for website display.</p>"
        )

def get_executive_summary_prompt(language, user_data):
    if language == "th":
        return f"""
คุณคือผู้เชี่ยวชาญด้านกลยุทธ์ธุรกิจ
กรุณาสรุปแผนธุรกิจจากข้อมูลต่อไปนี้เป็นภาษาไทยในรูปแบบที่มืออาชีพ กระชับ ชัดเจน ใช้ภาษาทางธุรกิจ

- ข้อมูลธุรกิจ: {user_data['business_info']}
- SWOT: {user_data['swot_summary']}
- วิสัยทัศน์ พันธกิจ เป้าหมาย: {user_data['vision_mission']}
- กลยุทธ์: {user_data['strategy']}
- แผนการตลาด: {user_data['marketing']}

เขียน Executive Summary ที่ครอบคลุมจุดเด่น โอกาส และแนวทางโดยรวมของแผนธุรกิจนี้
"""
    else:
        return f"""
<h2>Executive Summary</h2>
<p>Summarize the business plan below based on these inputs:</p>
<b>Business Info:</b> {user_data['business_info']}<br>
<b>SWOT Summary:</b> {user_data['swot_summary']}<br>
<b>Vision/Mission:</b> {user_data['vision_mission']}<br>
<b>Strategies:</b> {user_data['strategy']}<br>
<b>Marketing Plan:</b> {user_data['marketing']}<br>
<p>Please format the entire summary in readable HTML for clear visual presentation.</p>
"""

# ✅ NEW FUNCTION FOR FINANCIAL INPUTS
def get_financial_step_prompt(step):
    prompts = {
        1: """📊 Step 1: INITIAL INVESTMENT

Please enter the following (separated by commas):
1. Initial Investment Amount
2. Lifetime of the investment (number of years)
3. Salvage Value
4. Depreciation Method (1 = Straight-Line, 2 = DDB)
5. Tax Credit (as a decimal, e.g., 0.1 for 10%)""",

        2: """💵 Step 2: CASHFLOW DETAILS

Please enter the following values separated by commas:
1. Revenue in Year 1
2. COGS - Materials
3. COGS - Direct Labor
4. Opex - Rent
5. Opex - Salaries
6. Opex - Marketing
7. Opex - Office Supplies
8. Opex - Utilities
9. Tax Rate on Net Income (e.g., 0.4 for 40%)""",

        3: """📉 Step 3: DISCOUNT RATE

Enter either direct rate or CAPM parameters.
- If using Direct Approach (enter: 1, rate)
- If using CAPM/WACC (enter: 2, beta, risk-free rate, market premium, debt ratio, cost of debt)

Example (direct): 1, 0.1  
Example (CAPM): 2, 1.2, 0.05, 0.06, 0.3, 0.08""",

        4: """💼 Step 4: WORKING CAPITAL

Please enter the following (comma-separated):
1. Initial Working Capital
2. % of Revenue allocated to Working Capital (e.g., 0.2)
3. % of Working Capital recovered at the end (e.g., 1.0 = 100%)""",

        5: """📈 Step 5: GROWTH RATES

Provide up to 4 growth ranges each for Revenue, COGS, and Operating Expenses.

Input format for each is:
FromYear.ToYear.GrowthRate;...  
Example for Revenue: 1.3.0.05; 4.6.0.10; 7.10.0.03

Please enter the 3 rows (Revenue, COGS, Opex) **separated by line breaks** in the box below and press Send.
"""
    }
    return prompts.get(step, "❌ Unknown financial step.")