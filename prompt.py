# Install updated Ollama wrapper
# pip install -U langchain langchain-community langchain-ollama pandas openpyxl

import pandas as pd
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import re

# Initialize Ollama LLM (update base_url as needed)
llm = OllamaLLM(model="mistral", base_url="https://72b00638958d.ngrok-free.app")

# Comprehensive AML evaluation prompt
prompt_template = ChatPromptTemplate.from_template(
    """
You are an Anti-Money Laundering (AML) Risk Evaluation Agent.

Your task is to determine if a transaction matches a high-risk database record. Return either "True Match" or "False Match", based on the criteria below.

Evaluate carefully using these rules:

1. Record Type Validation:
   - Match only if both are of the same type: Person–Person or Entity–Entity.
   - If types differ, always return False Match.

2. Name Normalization:
   - Ignore case, punctuation, suffixes (Inc, Ltd, LLC), and spacing differences.
   - Handle known transliterations (e.g., Mohammad vs Muhammad).
   - Use fuzzy logic for close matches (e.g., Microsoft Corp vs Microsoft Corporation).

3. Cultural Name Variants:
   - Consider alternate name orderings or formats (e.g., Li Ming Hao vs Ming Hao Li).
   - Islamic names may use different structures (e.g., Abdul Rahman vs Rahman Abdul).

4. Entity Hierarchies:
   - Different legal entities (e.g., Tesla Motors LLC vs Tesla Inc) should not be assumed identical unless clearly parent/subsidiary.

Return your judgment in this format:

Match Outcome: True Match / False Match  
Reason: [Concise explanation citing rules used]

Transaction: {transaction}  
Database Record: {db_entry}  
Type: {type_}  
Match Type: {match_type}
"""
)

# Set up the chain
chain = prompt_template | llm

# Read the CSV file
df = pd.read_csv("prompt.csv")
results = []

# Process each test case
for idx, row in df.iterrows():
    result = chain.invoke({
        "transaction": row["Transaction Data"],
        "db_entry": row["High Risk Database Entry"],
        "type_": row["High Risk Database Entry Type"],
        "match_type": row["Match Type"]
    })
    print(f"Case {row['SI. No']}:\n{result}\n{'-'*40}")
    results.append(result)

# Save results to Excel
df["LLM_Evaluation"] = results
df.to_excel("test_results.xlsx", index=False)

def extract_match_outcome(llm_response):
    """Extracts 'True Match' or 'False Match' from the LLM's response."""
    match = re.search(r"Match Outcome:\s*(True Match|False Match)", str(llm_response), re.IGNORECASE)
    if match:
        return match.group(1).strip().lower()
    return None

# Calculate accuracy
correct = 0
total = len(df)
for idx, row in df.iterrows():
    pred = extract_match_outcome(row['LLM_Evaluation'])
    actual = str(row['Match Type']).strip().lower()
    # Normalize for comparison
    if actual == "true":
        actual = "true match"
    elif actual == "false":
        actual = "false match"
    if pred == actual:
        correct += 1

accuracy = correct / total * 100
print(f"Overall LLM Accuracy: {accuracy:.2f}% ({correct}/{total})")
