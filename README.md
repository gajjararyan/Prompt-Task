# AML Risk Evaluation Agent

## Overview
This project implements an AI-powered AML (Anti-Money Laundering) Risk Evaluation Agent that classifies transaction matches against a high-risk database as either True Match or False Match. It leverages LangChain, Ollama (Mistral or Llama3), and pandas to automate and explain the matching process, helping financial institutions comply with AML regulations.

## Features
- Validates record types (person/entity)
- Handles name normalization, transliteration, and cultural naming patterns
- Distinguishes entity hierarchies
- Outputs structured results with clear reasoning
- Processes test cases from a CSV file and saves results to Excel

## Setup Instructions
1. **Clone or download this repository.**
2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -U langchain langchain-community langchain-ollama pandas openpyxl
   ```
4. **Start Ollama and pull your model (on your server/Colab):**
   ```bash
   ollama pull mistral
   # or
   ollama pull llama3
   ```
5. **Update the `base_url` in `prompt.py`** to point to your running Ollama instance (local or remote).

## How to Run
1. Place your test cases in `prompt.csv` (see the provided format).
2. Run the evaluation script:
   ```bash
   python prompt.py
   ```
3. Results will be saved in `test_results.xlsx` with LLM-generated match outcomes and reasoning.

## Prompt Engineering Process

### Version 1: Basic Matching Prompt
```text
You are an AML assistant. Check if a transaction matches a high-risk record.  
If names match, output **True Match**; otherwise, **False Match**.  

**Transaction:** {transaction}  
**Database Record:** {db_entry}  
**Type:** {type_}  
**Match Type:** {match_type}  

Respond **only** with:  
`Match Outcome: True Match / False Match`  
`Reason: [Brief explanation]`
```
- **Issue:** LLM may ignore **record types, name variations, cultural ordering, or entity hierarchies**, leading to false positives/negatives.

---

### Version 2: Improved Prompt *(Fixes basic issues but misses edge cases)*
```text
You are an AML Risk Evaluation Agent.  
Determine if the transaction matches the high-risk database entry as **True Match** or **False Match**.  

**Rules:**  
1. **Type Match:** Only person-to-person or entity-to-entity (False if mismatched).  
2. **Name Normalization:** Ignore case, punctuation, and common abbreviations (e.g., "Inc." vs "Incorporated").  
3. **Variations:** Handle minor name differences (e.g., "Mohammad" vs "Muhammad").  

**Response Format:**  
```
Match Outcome: True Match / False Match  
Reason: [1-sentence explanation]  
```

**Input Data:**  
Transaction: {transaction}  
Database Record: {db_entry}  
Type: {type_}  
Match Type: {match_type}  
```
- **Issue:** Still misses **cultural name orders** (e.g., "Li Wei" vs "Wei Li") and **entity hierarchies** (parent vs subsidiary).

---

### Version 3: Final Refined Prompt *(Handles all edge cases)*
```text
You are an AML Risk Evaluation Agent.  

**Task:** Decide if a transaction matches a high-risk database entry as **True Match** or **False Match**.  

**Critical Rules:**  
1. **Type Strictness:** Person ↔ Person / Entity ↔ Entity (False if types differ).  
2. **Name Handling:**  
   - Ignore case, punctuation, abbreviations.  
   - Account for transliterations (e.g., "Mohammed" vs "Muhammad").  
   - Cultural order awareness (e.g., Chinese surnames first: "Zhang Wei" ≠ "Wei Zhang").  
3. **Entity Logic:** Subsidiaries ≠ Parent companies (e.g., "Google LLC" ≠ "Alphabet Inc.").  

**Output Format:**  
```
Match Outcome: True Match / False Match  
Reason: [Concise justification]  
```

**Input Fields:**  
Transaction: {transaction}  
Database Record: {db_entry}  
Type: {type_}  
Match Type: {match_type}  
```
- **Result:** **High accuracy** with clear reasoning, covering all edge cases (types, names, hierarchies).

---

## Data Requirements for Perfect Matching

| Limitation                        | Required Data Point                | How it Improves Matching                                 | Data Source                        |
|-----------------------------------|------------------------------------|----------------------------------------------------------|-------------------------------------|
| Name ambiguity/variants           | Unique entity/person ID            | Disambiguates similar names                              | KYC/Onboarding, National ID, SWIFT  |
| Transliteration/cultural issues   | Alternate spellings/aliases        | Matches across languages and scripts                     | Sanctions lists, KYC, Watchlists    |
| Entity hierarchy confusion        | Parent/subsidiary relationships    | Correctly links related companies                        | Corporate registries, Orbis, D&B    |
| Record type misclassification     | Explicit type field (person/entity)| Prevents mismatches across types                         | KYC, Transaction metadata           |
| Contextual info                   | Transaction purpose/location       | Reduces false positives by adding context                | Payment metadata, SWIFT, Banks      |
| Date of birth/incorporation       | DOB/DOI fields                     | Distinguishes between people/entities with same name     | KYC, Corporate filings              |
| Sanction/PEP list updates         | List version/date                  | Ensures up-to-date screening                             | Regulator, List provider            |
| Country of registration/residence | Country field                      | Helps resolve name/cultural ambiguities                  | KYC, Corporate registries           |
| Alias/nickname/maiden name        | Known aliases/nicknames            | Catches matches missed by formal name only               | KYC, Watchlists, Customer input     |

### How These Data Points Help
- **Unique IDs** (e.g., government ID, LEI, SWIFT BIC) ensure you’re matching the right person/entity, not just a name.
- **Aliases/Alternate spellings** catch transliteration and nickname issues.
- **Parent/subsidiary info** prevents false matches between related but distinct companies.
- **Explicit type fields** (person/entity) prevent cross-type mismatches.
- **Contextual info** (purpose, location) helps filter out false positives.
- **DOB/DOI** distinguishes between people/entities with the same name.
- **Country** helps with cultural name order and regional variations.
- **List version/date** ensures you’re screening against the latest data.


## Files
- `prompt.py` — Main script for running the evaluation
- `prompt.csv` — Input test cases (edit or extend as needed, I have got the 25 initial data I have added more to check.)
- `test_results.xlsx` — Output with LLM results and reasoning

---