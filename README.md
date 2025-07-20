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

To get as close to perfect matching as possible, we need more than just names and types. The table below lists key challenges and the extra data needed to solve them, with sources relevant to both India and global use cases. Here’s what helps:

| **Limitation**                    | **Required Data Point**                                 | **How It Improves Matching**                                                         | **Data Source (Global + India)**                                                      |
| --------------------------------- | ------------------------------------------------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------- |
| Name ambiguity / variants         | Unique ID (e.g., PAN, SWIFT, LEI)                       | Disambiguates individuals/entities with the same name                                | **India**: PAN, Aadhaar, MCA CIN, LEI<br>**Global**: SWIFT BIC, LEI, National ID, KYC |
| Transliteration / cultural issues | Aliases, alternate spellings, phonetic forms            | Enables matching across scripts and languages (e.g., Mohammad vs Muhammad)           | **India**: RBI lists, FIU<br>**Global**: OFAC, UN, World-Check, Refinitiv             |
| Entity hierarchy confusion        | Parent/subsidiary relationships                         | Helps associate known risky parent or child companies                                | **India**: MCA, ROC<br>**Global**: Orbis, OpenCorporates, D\&B, LexisNexis            |
| Type misclassification            | Explicit Type Field (Person / Entity)                   | Avoids person-entity confusion and improves model classification                     | **India**: KYC metadata, NSDL, UIDAI<br>**Global**: FATF KYC guidelines               |
| Contextual ambiguity              | Transaction purpose, sender/receiver country            | Helps rule out false matches from benign sources                                     | **India**: SWIFT data, NEFT/RTGS metadata<br>**Global**: Payment rails metadata       |
| Same name problem                 | Date of Birth (person) / Date of Incorporation (entity) | Distinguishes similar-named individuals/entities                                     | **India**: UIDAI, PAN, KYC, MCA<br>**Global**: World-Check, Refinitiv                 |
| List freshness                    | List version and last update date                       | Prevents outdated or stale matches                                                   | **India**: RBI, SEBI Sanctions List<br>**Global**: OFAC, UN, EU, Interpol             |
| Country-level ambiguity           | Nationality / Country of Incorporation                  | Helps resolve culturally ambiguous names and enforce local jurisdictional rules      | **India**: Aadhaar, MCA ROC<br>**Global**: UN, OFAC, International Sanctions Lists    |
| Hidden aliases or nicknames       | Known aliases / nicknames / banned name patterns        | Increases detection accuracy, especially in politically sensitive or high-risk zones | **India**: FIU, SEBI Watchlists<br>**Global**: LexisNexis, PEP databases              |

---


## Files in This Project
- `prompt.py` - Main script for running the evaluation
- `prompt.csv` - Input test cases (originally 25, but additional ones have been added for further testing, feel free to edit or extend as needed)
- `test_results.xlsx` - Output with model results and reasoning

---

## Final Notes

This AML Risk Evaluation Agent project is now complete. With the current prompt and test cases, the model achieved an accuracy of **98.33%** demonstrating strong performance on both standard and challenging real-world scenarios.

I hope you found this README clean, comprehensive, and easy to follow. If you have any queries or do not understand anything, please let me know by email.

