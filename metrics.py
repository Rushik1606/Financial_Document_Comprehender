import re
from typing import Dict, List


NUM_PATTERN = r"[-+]?\$?\s?\d{1,3}(?:[,\s]\d{3})*(?:\.\d+)?\s*(?:million|billion|m|bn|k)?"


def normalize_number(text: str) -> str:
	t = text.lower().replace(",", "").replace("$", "").strip()
	mult = 1.0
	if t.endswith(" billion") or t.endswith(" bn"):
		mult = 1_000_000_000
		t = t.replace(" billion", "").replace(" bn", "")
	elif t.endswith(" million") or t.endswith(" m"):
		mult = 1_000_000
		t = t.replace(" million", "").replace(" m", "")
	elif t.endswith(" k"):
		mult = 1_000
		t = t.replace(" k", "")
	try:
		val = float(t)
		return str(int(val * mult))
	except Exception:
		return text


def extract_metrics_from_texts(texts: List[str]) -> Dict[str, str]:
	joined = "\n\n".join(texts)
	metrics: Dict[str, str] = {}
	patterns = {
		"revenue": r"revenue[:\s\-]+(" + NUM_PATTERN + ")",
		"net_income": r"net\s+income[:\s\-]+(" + NUM_PATTERN + ")",
		"profit": r"(gross|operating|net)?\s*profit[:\s\-]+(" + NUM_PATTERN + ")",
		"operating_expenses": r"operating\s+expenses[:\s\-]+(" + NUM_PATTERN + ")",
		"cogs": r"(cost\s+of\s+goods\s+sold|cogs)[:\s\-]+(" + NUM_PATTERN + ")",
	}
	for key, pat in patterns.items():
		m = re.search(pat, joined, flags=re.IGNORECASE)
		if m:
			val = m.groups()[-1]
			metrics[key] = normalize_number(val)
	return metrics
