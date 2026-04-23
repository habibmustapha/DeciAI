# AHP Decision Support System
## Powered by Mistral AI via Ollama

A full-featured desktop application implementing the **Analytic Hierarchy Process (AHP)** for multi-criteria decision analysis, with an integrated local LLM for AI-assisted criteria generation and result explanation.

---

## Features

| Feature | Description |
|---|---|
| 🎯 Goal Input | Define your decision objective |
| 📋 Criteria | Manual or AI-generated via Mistral |
| ⚖️ Pairwise Matrices | Saaty 1-9 scale with auto-reciprocals |
| 📊 AHP Engine | Normalized matrices, eigenvector method |
| 🔍 Consistency | CI/CR check with Saaty's RI table |
| 🤖 AI Explanation | Streaming Mistral explanation of results |
| 💾 Export | CSV matrices + optional PDF report |

---

## Installation

```bash
pip install -r requirements.txt
```

For PDF export support:
```bash
pip install reportlab
```

---

## Ollama Setup

1. Install Ollama: https://ollama.ai
2. Pull the Mistral model:
```bash
ollama pull mistral
```
3. Start Ollama (it runs in background by default):
```bash
ollama serve
```

---

## Running

```bash
cd ahp_app
python main.py
```

---

## Architecture

```
ahp_app/
├── main.py                     # Entry point
├── view/
│   ├── main_window.py          # App shell & navigation
│   ├── goal_view.py            # Step 1: Goal & alternatives
│   ├── criteria_view.py        # Step 2: Criteria (manual/AI)
│   ├── matrix_view.py          # Step 3: Pairwise comparisons
│   └── result_view.py          # Step 4: Results & explanation
├── viewmodel/
│   └── ahp_viewmodel.py        # State orchestrator (MVVM)
├── model/
│   ├── ahp_model.py            # Data model
│   └── matrix_model.py         # Matrix helper
├── services/
│   ├── ahp_engine.py           # AHP math engine
│   ├── consistency.py          # CI/CR calculator
│   └── llm_service.py          # Ollama/Mistral client
└── utils/
    └── helpers.py              # CSV/PDF export utilities
```

---

## AHP Math Summary

1. **Pairwise Comparison**: User rates each pair on Saaty's 1-9 scale
2. **Normalization**: Each element divided by column sum
3. **Priority Vector**: Row averages of normalized matrix
4. **Consistency Check**: λmax → CI = (λmax - n)/(n-1) → CR = CI/RI
5. **Final Score**: Weighted sum of alternative priorities × criterion weights

CR ≤ 0.10 indicates acceptable consistency.
# DeciAI
