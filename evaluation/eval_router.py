from collections import defaultdict
from dataclasses import dataclass, field

from typing import List, Set, Dict, Callable
import csv
import argparse

from src.states import State
from src.nodes import router_node_with_embedding
from .utils import load_dataset

DOMAINS = ["python", "sql", "excel", "ml"]



def call_router(query :str) :

    state = State()
    state['query'] = query
    state['routes'] = router_node_with_embedding(state)

    return state['routes']


@dataclass
class CaseResult:
    query: str
    expected: Set[str]
    predicted: Set[str]
    # category: str
    # difficulty: str
    correct: bool = False


@dataclass
class DomainStats:
    tp: int = 0
    fp: int = 0
    fn: int = 0
 
    @property
    def precision(self) -> float:
        denom = self.tp + self.fp
        return self.tp / denom if denom else 0.0
 
    @property
    def recall(self) -> float:
        denom = self.tp + self.fn
        return self.tp / denom if denom else 0.0
 
    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) else 0.0
    

### Score 

def score_exact(expected: Set[str], predicted: Set[str]) -> bool:
    return expected == predicted

def score_subset(expected: Set[str], predicted: Set[str]) -> bool:
    """Credit if predicted is non-empty and every predicted domain is
    actually in expected (no wrong domains), and at least one expected
    domain was found. Good for 'any plausible domain is fine' cases."""
    if not predicted:
        return len(expected) == 0
    return predicted.issubset(expected) and len(predicted & expected) > 0

def score_overlap(expected: Set[str], predicted: Set[str]) -> bool:
    """Lenient: any overlap counts as a hit. Both empty also counts."""
    if not expected and not predicted:
        return True
    return len(expected & predicted) > 0


SCORERS: Dict[str, Callable[[Set[str], Set[str]], bool]] = {
    "exact": score_exact,
    "subset": score_subset,
    "overlap": score_overlap,
    }


def run_evaluation(cases: List[dict], scoring: str) -> List[CaseResult]:
    scorer = SCORERS[scoring]
    results = []
 
    for case in cases:
        query = case["query"]
        expected = set(case["expected"])
 
        try:
            pred_output = call_router(query)
            predicted_raw = pred_output['routes'].routes

        except NotImplementedError:
            raise
        except Exception as e:
            print(f"[WARN] Router raised an exception for query: {query!r} -> {e}")
            predicted_raw = []
 
        predicted = set(predicted_raw)
        correct = scorer(expected, predicted)
 
        results.append(CaseResult(
            query=query,
            expected=expected,
            predicted=predicted,
            # category=case.get("category", "unknown"),
            # difficulty=case.get("difficulty", "unknown"),
            correct=correct,
        ))
 
    return results

def compute_domain_stats(results: List[CaseResult]) -> Dict[str, DomainStats]:
    """Multi-label precision/recall/F1 per domain. This is computed the
    same way regardless of --scoring mode, since it's set-based ground
    truth, not dependent on the exact/subset/overlap acceptance rule."""
    
    stats = {d: DomainStats() for d in DOMAINS}
 
    for r in results:
        for d in DOMAINS:
            in_expected = d in r.expected
            in_predicted = d in r.predicted
            if in_predicted and in_expected:
                stats[d].tp += 1
            elif in_predicted and not in_expected:
                stats[d].fp += 1
            elif not in_predicted and in_expected:
                stats[d].fn += 1
            # true negatives aren't tracked; not needed for P/R/F1
 
    return stats


def compute_breakdown(results: List[CaseResult], key: str) -> Dict[str, dict]:

    """Accuracy broken down by an arbitrary field (category or difficulty)."""
    buckets = defaultdict(lambda: {"correct": 0, "total": 0})
    for r in results:
        bucket_key = getattr(r, key)
        buckets[bucket_key]["total"] += 1
        if r.correct:
            buckets[bucket_key]["correct"] += 1
 
    out = {}
    for k, v in buckets.items():
        out[k] = {
            **v,
            "accuracy": v["correct"] / v["total"] if v["total"] else 0.0,
        }
    return out


def print_report(results: List[CaseResult], scoring: str):
    total = len(results)
    correct = sum(1 for r in results if r.correct)
    overall_acc = correct / total if total else 0.0
 
    print("=" * 70)
    print("ROUTER EVALUATION REPORT")
    print("=" * 70)
    print(f"Scoring mode      : {scoring}")
    print(f"Total test cases  : {total}")
    print(f"Correct           : {correct}")
    print(f"Overall accuracy  : {overall_acc:.1%}")
    print()
 
    # --- Per-domain precision/recall/F1 ---
    print("-" * 70)
    print("PER-DOMAIN METRICS (multi-label)")
    print("-" * 70)
    print(f"{'Domain':<10}{'Precision':>12}{'Recall':>12}{'F1':>12}{'TP':>6}{'FP':>6}{'FN':>6}")
    domain_stats = compute_domain_stats(results)
    for d in DOMAINS:
        s = domain_stats[d]
        print(f"{d:<10}{s.precision:>12.1%}{s.recall:>12.1%}{s.f1:>12.1%}{s.tp:>6}{s.fp:>6}{s.fn:>6}")
    print()
 
    # Macro averages (unweighted mean across domains — treats each
    # domain equally regardless of how many examples it has)
    macro_p = sum(domain_stats[d].precision for d in DOMAINS) / len(DOMAINS)
    macro_r = sum(domain_stats[d].recall for d in DOMAINS) / len(DOMAINS)
    macro_f1 = sum(domain_stats[d].f1 for d in DOMAINS) / len(DOMAINS)
    print(f"Macro-avg Precision: {macro_p:.1%} | Recall: {macro_r:.1%} | F1: {macro_f1:.1%}")
    print()
 
    # # --- Breakdown by category ---
    # print("-" * 70)
    # print("ACCURACY BY CATEGORY")
    # print("-" * 70)
    # cat_breakdown = compute_breakdown(results, "category")
    # for cat, v in sorted(cat_breakdown.items(), key=lambda x: -x[1]["total"]):
    #     print(f"{cat:<28}{v['correct']:>4}/{v['total']:<4}  {v['accuracy']:.1%}")
    # print()
 
    # # --- Breakdown by difficulty ---
    # print("-" * 70)
    # print("ACCURACY BY DIFFICULTY")
    # print("-" * 70)
    # diff_order = ["easy", "medium", "hard", "edge"]
    # diff_breakdown = compute_breakdown(results, "difficulty")
    # for diff in diff_order:
    #     if diff in diff_breakdown:
    #         v = diff_breakdown[diff]
    #         print(f"{diff:<28}{v['correct']:>4}/{v['total']:<4}  {v['accuracy']:.1%}")
    # print()


def export_misclassified(results: List[CaseResult], out_path: str):
    misses = [r for r in results if not r.correct]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["query", "expected", "predicted", "category", "difficulty"])
        for r in misses:
            writer.writerow([
                r.query,
                "|".join(sorted(r.expected)) or "(none)",
                "|".join(sorted(r.predicted)) or "(none)",
                # r.category,
                # r.difficulty,
            ])
    print(f"Misclassified cases ({len(misses)}) written to: {out_path}")


def main():

    # router_eval_path = r"D:\New_Folder\DS_intructor_agent\artifacts\eval_dataset\difficulty\router_eval_dataset_easy.json"

    eval_json_path = r"D:\New_Folder\DS_intructor_agent\artifacts\eval_dataset\difficulty\router_eval_dataset_easy.json"


    parser = argparse.ArgumentParser(description="Evaluate the DS Instructor router node.")
    # parser.add_argument("--data", default="artifacts\eval_dataset\difficulty\router_eval_dataset_easy_sample.json", help="Path to eval dataset JSON")
    parser.add_argument("--scoring", choices=list(SCORERS.keys()), default="exact",
                         help="Scoring strictness for the overall accuracy metric")
    parser.add_argument("--out", default="misclassified_cases.csv", help="Path for misclassified-cases CSV")
    args = parser.parse_args()
 
    cases = load_dataset(eval_json_path)
    results = run_evaluation(cases, args.scoring)
    print_report(results, args.scoring)
    export_misclassified(results, args.out)
 
 
if __name__ == "__main__":
    main()
