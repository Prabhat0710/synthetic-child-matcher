# Synthetic Child Matcher

A quick‑start hackathon project that ingests synthetic child and family data, computes compatibility scores, and generates human‑readable explanations via the Gemini API.

## Project layout
```
synthetic_child_matcher/
├─ app/
│  ├─ __init__.py
│  ├─ main.py
│  ├─ ui/
│  │   ├─ __init__.py
│  │   ├─ parent_view.py
│  │   └─ admin_analysis.py
│  └─ processing/
│      ├─ __init__.py
│      ├─ data_loader.py
│      ├─ preprocess.py
│      └─ matcher.py
├─ requirements.txt
├─ data/
│   ├─ synthetic_children.csv
│   └─ families.csv
└─ README.md
```

## Getting started
```bash
pip install -r requirements.txt
streamlit run app/main.py
```