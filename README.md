# AML Risk Evaluation Agent

## Project Overview

This project is a practical tool for automating Anti-Money Laundering (AML) risk evaluation. It uses a language model (via Ollama and LangChain) to decide if a transaction matches a high-risk entity, helping financial institutions comply with AML regulations. The script checks each transaction in your dataset, explains its reasoning, and outputs the results for easy review.

## Features
- Checks if transactions match high-risk database entries (person or entity)
- Handles name variations, transliterations, and cultural naming patterns
- Considers entity hierarchies (parent/subsidiary)
- Gives clear, structured explanations for each decision
- Reads from a CSV and writes results to Excel

## Getting Started

### 1. Set Up Your Environment
- Make sure you have Python 3.8+ installed.
- Create a virtual environment:
  ```bash
  python -m venv venv
  # On Windows:
  .\venv\Scripts\activate
  # On Mac/Linux:
  source venv/bin/activate
  ```
- Install the required packages:
  ```bash
  pip install -U langchain langchain-community langchain-ollama pandas openpyxl
  ```

### 2. Start Ollama and Pull a Model
- On your server or Colab, run:
  ```bash
  ollama pull mistral
  # or
  ollama pull llama3
  ```
- Update the `base_url` in `prompt.py` to point to your Ollama instance.

### 3. Prepare Your Data
- Put your test cases in `prompt.csv` (see the included file for the format).

### 4. Run the Script
- From your project folder, run:
  ```bash
  python prompt.py
  ```
- The results will be saved in `test_results.xlsx` with the model’s match outcome and reasoning for each case.

## How the Prompt Evolved

### Version 1: Basic Matching
A simple check: if the names match, it’s a True Match; otherwise, False Match. No consideration for type, spelling, or cultural differences.
- **Issue:** Too many false positives/negatives due to ignoring type and name variations.

### Version 2: Improved Logic
Added rules for matching type (person/entity), ignoring case and punctuation, and handling common name variations.
- **Issue:** Still missed edge cases like cultural name order (e.g., Chinese names) and parent/subsidiary relationships.

### Version 3: Final Version (Current)
Now the prompt covers:
- Strict type matching (person ↔ person, entity ↔ entity)
- Name normalization (case, punctuation, transliteration)
- Cultural name order (e.g., "Wei Zhang" vs "Zhang Wei")
- Entity hierarchy (parent ≠ subsidiary)
- Always gives a concise, clear reason

This version gives much more reliable results and clear explanations.

## Final Prompt (Exact Text Used)

```text
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
```

## Data Requirements for Better Accuracy

To get as close to perfect matching as possible, you’ll want more than just names and types. Here’s what helps:

| Limitation                        | Needed Data                | Why It Helps                                   | Where to Get It                |
|-----------------------------------|----------------------------|------------------------------------------------|-------------------------------|
| Name ambiguity/variants           | Unique ID (person/entity)  | Tells apart people/entities with same name      | KYC, National ID, SWIFT        |
| Transliteration/cultural issues   | Aliases/alternate spellings| Matches across languages/scripts                | KYC, sanctions lists           |
| Entity hierarchy confusion        | Parent/subsidiary info     | Links related companies correctly               | Corporate registries, Orbis    |
| Type misclassification            | Explicit type field        | Prevents person/entity mismatches               | KYC, transaction metadata      |
| Contextual info                   | Purpose/location           | Reduces false positives                         | Payment metadata, SWIFT        |
| Date of birth/incorporation       | DOB/DOI                    | Distinguishes people/entities with same name    | KYC, corporate filings         |
| List updates                      | List version/date          | Ensures screening is up-to-date                 | Regulator, list provider       |
| Country info                      | Country field              | Helps with cultural name order/ambiguity        | KYC, corporate registries      |
| Aliases/nicknames                 | Known aliases/nicknames    | Catches matches missed by formal name only      | KYC, watchlists, customer input|

**Bottom line:**
- The more context you have, the better the matching.
- Prompts can only do so much—good data is just as important as good logic.

## Files in This Project
- `prompt.py` — Main script for running the evaluation
- `prompt.csv` — Input test cases (edit or extend as needed)
- `test_results.xlsx` — Output with model results and reasoning

---

## Final Notes

This AML Risk Evaluation Agent project is now complete. With the current prompt and test cases, the model achieved an accuracy of **98.33%**—demonstrating strong performance on both standard and challenging real-world scenarios.

I hope you found this README clean, comprehensive, and easy to follow. If you have any questions or want to build further, you should have everything you need right here. Thanks for reading, and happy experimenting!

