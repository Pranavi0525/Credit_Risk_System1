## Week 3 · Day 3 — Transaction & Expense Behavior

### Spending Volume
- Monthly spend distribution is __________
- A small proportion of cycles account for high total spend, indicating __________

### Category Behavior
- Top spending categories are __________
- Some billing cycles show high category concentration (>60%), suggesting __________

### Volatility
- Cards with high spend volatility may indicate __________
- Stable spend patterns are associated with __________ behavior

### Modeling Implications
- Monthly spend should be used as a behavioral feature
- Spend volatility is a strong early-warning signal
- Category concentration may distinguish lifestyle risk vs financial stress
# Week 3 Day 2 - WHY We're Doing Credit Behavior Analysis
## Complete Explanation of Purpose and Reasoning

---

## 🎯 THE BIG PICTURE: What Are We Actually Doing?

### In Simple Terms

Imagine you're a bank manager trying to figure out **who might miss their credit card payment next month**.

You don't have a crystal ball, but you DO have their past credit card statements.

**Question:** If you look at someone's credit card statement today, what clues tell you they might be in trouble?

**Answer:** How much of their credit limit they're using!

**This is what Day 2 is all about** - finding those early warning signals in credit behavior.

---

## 🧠 WHY Credit Behavior Analysis Comes BEFORE Everything Else

### The Logical Order

```
Week 3 Day 1: Load data, make sure it's valid ✅
              ↓
Week 3 Day 2: Study CREDIT BEHAVIOR (← YOU ARE HERE)
              ↓
Week 3 Day 3: Study SPENDING patterns (transactions)
              ↓
Week 3 Day 4: Study PAYMENT patterns (when they pay)
              ↓
Week 3 Days 5-7: Put it all together
```

### Why This Order?

**Credit behavior is the FOUNDATION** because:

1. **It's the most predictive** - How much someone owes vs. their limit is the #1 risk signal
2. **It's monthly** - Aligns with billing cycles (our prediction unit)
3. **It's simple** - Just balance ÷ limit (no complex calculations yet)
4. **It's what banks look at first** - In real life, this is where risk assessment starts

**Analogy:**
- Credit behavior = Your overall health (blood pressure, weight)
- Spending patterns = Your diet details
- Payment patterns = Your exercise habits

You check overall health FIRST before diving into details.

---

## 📊 STEP-BY-STEP: Why We Do Each Thing

### STEP 0: Why Add a Markdown Section?

**Purpose:** Organization and documentation

**Real Reason:**
- When you come back to this notebook in 2 months, you need to know what each section does
- When a recruiter looks at your notebook, clear sections show professionalism
- It's like chapter titles in a book

**Without this:** One giant blob of code that's impossible to navigate

---

## 🔍 STEP 1: Why Create Core Behavioral Variables?

### 1.1 Why Merge Cards + Billing Cycles?

**Code:**
```python
cycles_enriched = cycles.merge(
    cards[["card_id", "credit_limit"]],
    on="card_id",
    how="left"
)
```

**What This Does:**
Combines two tables so each billing cycle row now has the credit limit attached.

**Why We Need This:**

Think about it:
- **billing_cycles table** has: "You owe $800 this month"
- **credit_cards table** has: "Your limit is $1,000"

**Question:** Is owing $800 good or bad?

**Answer:** It depends!
- If limit is $1,000 → You've used 80% (BAD! ⚠️)
- If limit is $10,000 → You've used 8% (Good ✅)

**Same $800, totally different risk!**

We MUST merge these tables to calculate the ratio.

**Real-World Example:**

**Person A:**
- Owes: $2,000
- Limit: $2,500
- Utilization: 80% → HIGH RISK ⚠️

**Person B:**
- Owes: $2,000
- Limit: $20,000
- Utilization: 10% → LOW RISK ✅

Same debt amount, different risk levels!

---

### 1.2 Why Calculate Credit Utilization?

**Code:**
```python
cycles_enriched["credit_utilization"] = (
    cycles_enriched["total_due"] / cycles_enriched["credit_limit"]
)
```

**What This Calculates:**
The percentage of available credit being used.

**Why This Is THE MOST IMPORTANT METRIC:**

**Financial Research Shows:**

1. **People who max out their cards are more likely to miss payments**
   - Using 90%+ of limit = often can't pay
   - Using 30% of limit = comfortably managing debt

2. **Credit bureaus use this for credit scores**
   - Low utilization → Good credit score
   - High utilization → Bad credit score

3. **It's a stress indicator**
   - High utilization = "I need every dollar I can borrow"
   - Low utilization = "I'm using credit strategically"

**Real-Life Scenario:**

**Sarah's Credit Card:**
- Limit: $5,000
- Balance: $4,800
- Utilization: 96%

**What this tells us:**
- ⚠️ Sarah is living RIGHT at the edge
- ⚠️ One unexpected expense and she can't pay
- ⚠️ She probably doesn't have savings
- ⚠️ HIGH RISK of missing next payment

**John's Credit Card:**
- Limit: $5,000
- Balance: $500
- Utilization: 10%

**What this tells us:**
- ✅ John uses credit responsibly
- ✅ Lots of cushion if needed
- ✅ Likely has other resources
- ✅ LOW RISK of missing payment

**This ONE number (utilization) tells you so much about risk!**

---

## 📈 STEP 2: Why Plot Distributions?

### 2.1 Why Plot Utilization Distribution?

**Code:**
```python
plt.hist(cycles_enriched["credit_utilization"], bins=30)
```

**What We're Looking For:**

```
     |
     |     ┌─┐
     |     │ │
Count|  ┌──┤ ├──┐
     |  │  │ │  │
     |──┴──┴─┴──┴────
        0% 50% 100%
       Utilization
```

**Questions This Answers:**

1. **How many people are in danger?**
   - If most bars are on the right (80-100%) → LOTS of high-risk users
   - If most bars are on the left (0-30%) → Mostly safe users

2. **What's "normal" in our data?**
   - Peak at 20%? → Users are conservative
   - Peak at 70%? → Users are stressed

3. **Are there concerning patterns?**
   - Big spike at 100%? → Many people maxed out (crisis!)
   - Spread evenly? → Diverse user base

**Real-World Insight:**

Imagine two scenarios:

**Scenario A: Healthy Portfolio**
```
Most people at 20-40% utilization
Few people above 80%
→ Low default risk overall
```

**Scenario B: Risky Portfolio**
```
Many people at 80-100% utilization
Very few at low utilization
→ High default risk, potential crisis
```

**The histogram INSTANTLY shows you which scenario you're in!**

---

### 2.2 Why Plot Minimum Due Ratio?

**Code:**
```python
cycles_enriched["min_due_ratio"] = (
    cycles_enriched["minimum_due"] / cycles_enriched["total_due"]
)
```

**What This Means:**

- Total due: $1,000 (what you owe)
- Minimum due: $25 (smallest payment allowed)
- Ratio: 25/1000 = 2.5%

**Why This Matters:**

**Low ratio (1-3%):**
- Bank is saying: "We trust you, just pay a tiny amount"
- Usually means: Lower balance OR good payment history
- Risk: LOW

**High ratio (10-20%):**
- Bank is saying: "You need to pay more NOW"
- Usually means: High balance OR missed payments before
- Risk: HIGH

**Real Example:**

**Alice:**
- Owes: $500
- Minimum: $25
- Ratio: 5%
- Interpretation: Small balance, easy to manage

**Bob:**
- Owes: $5,000
- Minimum: $750
- Ratio: 15%
- Interpretation: Large balance, bank wants significant payment

**Bob is in trouble - the bank is making him pay 15% minimum because they're worried!**

---

## 🎯 STEP 3: Why Risk Segmentation?

### 3.1 Why Bucket Users by Utilization?

**Code:**
```python
def utilization_bucket(u):
    if u < 0.3:
        return "low"
    elif u < 0.6:
        return "medium"
    elif u < 0.9:
        return "high"
    else:
        return "critical"
```

**What This Does:**
Puts every billing cycle into a risk category.

**Why We Do This:**

**1. Humans think in categories, not decimals**

Instead of saying:
- "User A has 0.273 utilization"
- "User B has 0.831 utilization"

We say:
- "User A: LOW RISK ✅"
- "User B: HIGH RISK ⚠️"

Much clearer!

**2. Enables comparison across groups**

We can ask:
- "How many users are in each risk bucket?"
- "Do high-risk users have higher balances?"
- "Do critical users pay less often?"

**3. Matches how banks actually operate**

Real banks have risk tiers:
- "Prime" customers (low risk)
- "Subprime" customers (high risk)

We're mimicking real-world practice.

**Real-World Use:**

```
Portfolio Risk Report:
- Low risk: 60% of users (safe ✅)
- Medium risk: 25% of users (watch 👀)
- High risk: 10% of users (intervene soon ⚠️)
- Critical risk: 5% of users (urgent! 🚨)
```

**A manager can understand this instantly!**

---

### 3.2 Why Average Debt by Risk Bucket?

**Code:**
```python
cycles_enriched.groupby("util_bucket")[["total_due", "minimum_due"]].mean()
```

**What This Shows:**

```
Risk Level    Avg Total Due    Avg Min Due
low           $500             $15
medium        $1,200           $40
high          $2,500           $150
critical      $4,800           $500
```

**Why This Is Important:**

**Validates our intuition:**
- If high-risk users DON'T have higher balances → Something's wrong with our bucketing
- If critical users have 10x the debt of low-risk → Our bucketing makes sense

**Reveals the severity:**
- "Critical" users owe $4,800 on average
- That's a REAL number for planning interventions
- "We need to help 100 users who owe ~$5,000 each"

**Real-World Example:**

**Unexpected finding:**
"Wait, our 'critical' users actually have LOWER balances than 'high' users?!"

**Possible explanation:**
Critical users have LOW credit limits but maxed them out!
- Critical: $500 owed, $500 limit (100% utilization)
- High: $2,000 owed, $3,000 limit (67% utilization)

**This insight changes your strategy!**

---

## ⏰ STEP 4: Why Temporal Behavior?

### 4.1 Why Sort by Date?

**Code:**
```python
cycles_enriched = cycles_enriched.sort_values(
    ["card_id", "cycle_end_date"]
)
```

**Why This Is Critical:**

Imagine looking at someone's medical records out of order:
- December: Healthy
- March: Sick
- January: Healthy
- February: Healthy

**Question:** When did they get sick?

You can't tell because the order is scrambled!

**Sorted by date:**
- January: Healthy
- February: Healthy
- March: Sick ⚠️
- December: Still sick

**Now you can see: Got sick in March!**

**For credit cards:**

**Unsorted:**
- August: 40% utilization
- April: 20% utilization
- June: 60% utilization

**Sorted:**
- April: 20%
- June: 60%
- August: 40%

**Now we see:** Spike in June! What happened?

---

### 4.2 Why Plot Utilization Trends?

**Code:**
```python
plt.plot(card_data["cycle_end_date"], card_data["credit_utilization"])
```

**What We're Looking For:**

**Pattern 1: Rising Trend (Danger!)**
```
Utilization
100% |                    ●
     |                ●
 50% |            ●
     |        ●
  0% |    ●
     └─────────────────────
     Jan  Mar  May  Jul  Sep
```
**Meaning:** Financial stress is INCREASING
**Risk:** HIGH - likely to miss payment soon

---

**Pattern 2: Flat High (Chronic Stress)**
```
Utilization
100% |    ●──●──●──●──●
     |
 50% |
     |
  0% |
     └─────────────────────
     Jan  Mar  May  Jul  Sep
```
**Meaning:** Living at the edge constantly
**Risk:** HIGH - one mistake and they default

---

**Pattern 3: Stable Low (Safe)**
```
Utilization
100% |
     |
 50% |
     |
  0% |    ●──●──●──●──●
     └─────────────────────
     Jan  Mar  May  Jul  Sep
```
**Meaning:** Responsible user
**Risk:** LOW - consistently manages well

---

**Pattern 4: Volatile (Unpredictable)**
```
Utilization
100% |        ●
     |    ●       ●
 50% |            
     |●              ●
  0% |    
     └─────────────────────
     Jan  Mar  May  Jul  Sep
```
**Meaning:** Irregular income or spending
**Risk:** MEDIUM - unstable but not necessarily bad

---

**Why This Matters for ML:**

**Static feature (just current month):**
- "User has 70% utilization"
- Moderately informative

**Temporal feature (trend over 6 months):**
- "User went from 20% → 70% in 6 months"
- MUCH more informative! Tells a story of deterioration

**Future Feature Idea:**
```python
utilization_slope = (current_utilization - utilization_6_months_ago) / 6
```

If slope is positive and large → Early warning signal!

---

## ✍️ STEP 5: Why Write Insights?

### Why Not Just Make Plots?

**Problem with just plots:**
- You make 10 beautiful graphs
- Come back next week
- **What did they mean?** You forgot!

**Solution: Written insights**

```markdown
## Credit Utilization
- 35% of billing cycles have utilization > 60%
- This is HIGH compared to industry standard (20%)
- Suggests portfolio has elevated risk
```

**Why This Is Gold:**

**For you:**
- Remember what you found
- Guide feature engineering
- Make modeling decisions

**For interviewers:**
- Shows you THINK, not just code
- Demonstrates business understanding
- Proves communication skills

**Real Interview Question:**
"What did you discover in your EDA?"

**Bad answer:**
"I made some plots of utilization"

**Good answer:**
"I found that 35% of our billing cycles had utilization above 60%, which is significantly higher than the industry benchmark. This indicated our portfolio has elevated risk, so I made sure to include utilization trend as a primary feature and..."

**The second answer gets you hired!**

---

## 🎯 The Bigger Picture: Why Day 2 Matters

### Building Knowledge Like a Pyramid

```
Week 6: Deploy model
        ↑
Week 5: Train model
        ↑
Week 4: Engineer features ← Needs insights from Week 3
        ↑
Week 3 Day 2: Credit behavior ← YOU ARE HERE
```

**What We're Building Today:**

1. **Intuition about risk**
   - What does 80% utilization mean?
   - Is rising utilization dangerous?

2. **Feature ideas**
   - Current utilization (yes!)
   - Utilization trend (yes!)
   - Utilization volatility (yes!)

3. **Data quality checks**
   - Are there weird patterns?
   - Missing values?
   - Outliers?

4. **Business understanding**
   - What's normal in credit cards?
   - What signals trouble?

**Without Day 2:**
- Week 4: "What features should I create?" (No idea!)
- Week 5: "Why is my model performing poorly?" (No understanding!)
- Interview: "What's important in credit risk?" (Blank stare!)

**With Day 2:**
- Week 4: "I'll create utilization, trend, and volatility features because my EDA showed..."
- Week 5: "My model works well because I engineered features based on actual risk patterns..."
- Interview: "Credit utilization is the key risk signal, and I validated this through distribution analysis showing..."

---

## 🚫 What We're NOT Doing (And Why)

### Why No Machine Learning Yet?

**You don't build a house starting with the roof!**

```
❌ WRONG ORDER:
1. Train model
2. Get bad results
3. Go back and look at data
4. Realize you misunderstood the problem

✅ RIGHT ORDER:
1. Understand the data (← DAY 2)
2. Understand the patterns
3. Engineer features based on understanding
4. THEN train model with confidence
```

### Why No Payments or Transactions Yet?

**Complexity management.**

**If we added everything at once:**
- 7 tables
- 100+ potential features
- Overwhelming!
- Can't tell what matters

**Instead, layer by layer:**
- Day 2: Credit behavior (simple, critical)
- Day 3: Add spending (more complex)
- Day 4: Add payments (temporal complexity)
- Day 5+: Combine everything

**Each day builds on the previous day's understanding.**

---

## 💡 Summary: The Purpose of Day 2

### What We're Really Doing

**Surface Level:**
"Making plots of credit utilization"

**Actual Purpose:**
1. **Build risk intuition** - Learn what signals danger
2. **Validate data quality** - Make sure data makes sense
3. **Generate feature ideas** - What to build in Week 4
4. **Create documentation** - Insights for future reference
5. **Develop business understanding** - Think like a bank analyst

### The Mental Model

**You're a detective investigating:**
- "Who might not pay next month?"
- "What patterns do risky users show?"
- "How can I spot trouble early?"

**Credit behavior analysis = Looking at the most obvious clues first**

Just like a detective checks:
1. The obvious suspects first (credit utilization)
2. Then digs deeper (spending patterns - Day 3)
3. Then looks at timeline (payment history - Day 4)

---

## 🎯 Final Thought

**This is how professionals work:**

❌ **Amateur approach:**
"Let me throw data into XGBoost and see what happens"

✅ **Professional approach:**
"Let me understand the domain, explore the data systematically, build intuition, document insights, THEN engineer features and model"

**Day 2 is you being a professional.**

The code is simple, but the THINKING is sophisticated.

**That's what separates good data scientists from code monkeys!** 🎯

---

**Now you understand not just WHAT to do, but WHY it matters!**
## Week 3 · Day 4 — Time-Series Risk Signals

### Utilization Trends
- Cards with steadily increasing utilization indicate __________
- Rolling averages smooth noise and highlight __________

### Acceleration Signals
- Positive utilization change over multiple cycles suggests __________
- Acceleration is more informative than absolute level because __________

### Spending Shocks
- Sudden spend spikes often precede __________
- Shock indicators can complement utilization-based risk metrics

### Modeling Implications
- Rolling features capture behavioral momentum
- Acceleration features help detect early-stage risk
- Combining level + trend improves prediction robustness
## Week 3 · Day 5 — Target Leakage & Validation

### Leakage Risks Identified
- Using post-due-date transactions would introduce leakage
- Forward-looking rolling features can falsely boost performance

### Prevention Measures
- Strict observation cutoffs enforced at billing-cycle level
- All rolling features computed using backward windows
- Explicit rejection of future-derived features

### Modeling Readiness
- Data is safe for supervised learning
- Temporal integrity verified
- Ready for label creation in subsequent steps

