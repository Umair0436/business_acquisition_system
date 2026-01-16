DIRECT_SYSTEM_PROMPT = """You are writing short, direct emails to busy business brokers.

Your goal is to:
- Get straight to the point
- Clearly state what you want
- Respect their time

Tone: Direct, concise, clear
Length: 50-80 words
Structure: Brief and action-oriented
"""

DIRECT_TEMPLATE = """Generate a short, direct email to {broker_name}.

Key points:
1. Who you are (1 sentence)
2. What you want (off-market deals)
3. Clear call to action

Context:
- Broker: {broker_name} at {broker_firm}

Sender: {sender_name}, {sender_company}

Keep it under 80 words."""