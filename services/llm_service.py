import requests
import json
from typing import List, Optional, Callable, Dict


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL      = "mistral"


def _build_prompt(
    language: str,
    goal: str,
    criteria_info: str,
    ranking_info: str
) -> str:

    if language == "fr":
        return f"""Vous êtes un expert en Analyse Hiérarchique des Procédés (AHP) et en aide à la décision multicritère.

Objectif de décision : « {goal} »

POIDS DES CRITÈRES (plus le poids est élevé, plus le critère est important) :
{criteria_info}

CLASSEMENT FINAL DES ALTERNATIVES :
{ranking_info}

Rédigez une explication claire et professionnelle en 3 à 5 paragraphes couvrant :
1. Pourquoi l'alternative classée première a obtenu le meilleur résultat
2. Quels critères ont eu le plus grand impact sur la décision
3. Les compromis clés entre les 2 ou 3 premières alternatives
4. Des recommandations ou mises en garde pour le décideur

Citez les noms et les chiffres réels. Répondez UNIQUEMENT en français."""

    if language == "ar":
        return f"""أنت خبير في طريقة التحليل الهرمي (AHP) ودعم القرار متعدد المعايير.

هدف القرار: « {goal} »

أوزان المعايير (كلما زاد الوزن، زادت أهمية المعيار):
{criteria_info}

الترتيب النهائي للبدائل:
{ranking_info}

اكتب شرحاً واضحاً واحترافياً في 3 إلى 5 فقرات يتناول:
1. لماذا حصلت البديل الأول على أعلى تقييم
2. أي المعايير كان لها التأثير الأكبر على القرار
3. المقايضات الرئيسية بين أفضل 2 أو 3 بدائل
4. توصيات أو تحفظات للمسؤول عن القرار

استشهد بالأسماء والأرقام الفعلية. أجب باللغة العربية الفصحى فقط."""

    # Default: English
    return f"""You are an expert in the Analytic Hierarchy Process (AHP) and multi-criteria decision analysis.

Decision goal: "{goal}"

CRITERIA WEIGHTS (higher = more important):
{criteria_info}

FINAL RANKING:
{ranking_info}

Write a clear professional explanation in 3 to 5 paragraphs covering:
1. Why the top-ranked alternative won
2. Which criteria had the biggest impact on the decision
3. Key trade-offs between the top 2 or 3 alternatives
4. Recommendations or caveats for the decision-maker

Reference actual names and numbers. Reply in English only."""


class LLMService:

    def _call_ollama(self, prompt: str, stream: bool = False,
                     on_token: Optional[Callable[[str], None]] = None) -> str:
        payload = {"model": MODEL, "prompt": prompt, "stream": stream}
        try:
            response = requests.post(OLLAMA_URL, json=payload,
                                     stream=stream, timeout=180)
            response.raise_for_status()
            if stream:
                full = ""
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line.decode("utf-8"))
                        tok = chunk.get("response", "")
                        full += tok
                        if on_token:
                            on_token(tok)
                        if chunk.get("done", False):
                            break
                return full
            return response.json().get("response", "")
        except requests.exceptions.ConnectionError:
            return "[ERROR] Cannot connect to Ollama. Make sure it is running at localhost:11434."
        except requests.exceptions.Timeout:
            return "[ERROR] Request timed out."
        except Exception as e:
            return f"[ERROR] {e}"


    def verify_criteria_consistency(
        self,
        goal: str,
        criteria: List[str],
        questions: List[Dict],
        cr: float,
        ci: float,
        on_token: Optional[Callable[[str], None]] = None
    ) -> str:
        comparisons = "\n".join(
            f'  • "{q["a"]}" vs "{q["b"]}"  →  {q["value"]:.3f}x'
            for q in questions
        )
        prompt = f"""You are an AHP expert.

Decision goal: "{goal}"

PAIRWISE ANSWERS:
{comparisons}

Consistency ratio: CR={cr:.4f} (threshold = 0.10)

Reply with EXACTLY one line, nothing else:
- If CR <= 0.10: "✓ CONSISTENT — CR = {cr:.4f}"
- If CR >  0.10: "✗ INCONSISTENT — CR = {cr:.4f}. Revisit: [name the single most contradictory pair]"

One line only. No explanation. No paragraphs."""

        return self._call_ollama(prompt, stream=False)


    def explain_results(
        self,
        goal: str,
        criteria: List[str],
        criteria_weights: List[float],
        alternatives: List[str],
        scores: List[float],
        ranking: list,
        language: str = "en",
        on_token: Optional[Callable[[str], None]] = None
    ) -> str:

        criteria_info = "\n".join(
            f"  - {c}: {w:.4f}" for c, w in zip(criteria, criteria_weights)
        )
        ranking_info = "\n".join(
            f"  {r}. {name}: {score:.4f}" for r, name, score in ranking
        )

        prompt = _build_prompt(language, goal, criteria_info, ranking_info)
        return self._call_ollama(prompt, stream=True, on_token=on_token)


def generate_criteria(goal: str):
    prompt = f"""
You are an expert in decision making (AHP).

Given this goal:
"{goal}"

Generate a list of 5 to 8 relevant decision criteria.

Rules:
- Short names (2-4 words)
- Clear and professional
- No explanations
- Return ONLY a Python list

Example:
["Cost", "Quality", "Delivery Time"]

Now generate:
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }
    )

    data = response.json()
    text = data.get("response", "")

    try:
        # Convert string list → Python list
        criteria = eval(text)
        if isinstance(criteria, list):
            return criteria
    except:
        pass

    # fallback parsing
    lines = [l.strip("-• ").strip() for l in text.split("\n") if l.strip()]
    return lines[:8]