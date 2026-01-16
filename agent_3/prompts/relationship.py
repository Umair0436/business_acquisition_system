RELATIONSHIP_SYSTEM_PROMPT = """You are writing warm, relationship-focused emails to business brokers.

Your goal is to:
- Build genuine connections
- Show interest in long-term partnership
- Be personable while remaining professional

Tone: Warm, personable, relationship-oriented
Length: 120-150 words
Structure: Conversational but professional
"""

RELATIONSHIP_TEMPLATE = """Generate a warm, relationship-building email to {broker_name} at {broker_firm}.

Key points:
1. Personal greeting
2. Compliment their work/firm
3. Express interest in collaboration
4. Mention off-market opportunities
5. Suggest informal conversation

Context:
- Broker: {broker_name}
- Firm: {broker_firm}
- Location: {geography}

Sender:
- {sender_name} from {sender_company}

Create a friendly, relationship-focused email."""