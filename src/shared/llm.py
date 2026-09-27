import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv; load_dotenv(override=True)

# Deterministic model for extraction, JSON parsing, and strict ATS formatting
parser_llm = ChatOpenAI(
    model="gpt-5.4-mini",
    temperature=0.0
)

# Creative/polishing model for natural phrasing, narrative, and tailoring
writer_llm = ChatOpenAI(
    model="gpt-5.4-mini",
    temperature=0.3
)