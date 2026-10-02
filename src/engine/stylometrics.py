"""
Stylometrics and Burrows' Delta Distance Engine for Upstage.
"""

import re
import math
from collections import Counter
from typing import List, Dict, Tuple, Union

DEFAULT_MFW_LIST = [
    "the", "and", "i", "to", "of", "a", "you", "my", "that", "in",
    "is", "not", "it", "with", "me", "for", "be", "this", "your", "his",
    "but", "he", "have", "as", "thou", "so", "what", "will", "all", "him"
]


class StylometricEngine:
    def __init__(self, mfw_words: List[str] = None):
        self.mfw_words = mfw_words or DEFAULT_MFW_LIST

    @staticmethod
    def tokenize(text: str) -> List[str]:
        return re.findall(r"\b[a-zA-Z']+\b", text.lower())

    def compute_word_frequencies(self, text: str) -> Dict[str, float]:
        tokens = self.tokenize(text)
        total_tokens = len(tokens)
        if total_tokens == 0:
            return {w: 0.0 for w in self.mfw_words}
        counts = Counter(tokens)
        return {w: (counts[w] / total_tokens) * 1000.0 for w in self.mfw_words}

    def fit_corpus_statistics(
        self,
        corpus_samples: List[str]
    ) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        Fits mean and standard deviation across a collection of text chunks
        or turns to establish authentic linguistic variability across the drama.
        """
        all_freqs = [self.compute_word_frequencies(t) for t in corpus_samples if t.strip()]
        if not all_freqs:
            return {w: 0.0 for w in self.mfw_words}, {w: 1.0 for w in self.mfw_words}

        means = {}
        stdevs = {}
        for w in self.mfw_words:
            vals = [f[w] for f in all_freqs]
            m = sum(vals) / len(vals)
            var = sum((v - m)**2 for v in vals) / max(len(vals) - 1, 1)
            # Minimum variance floor to avoid division by zero on rare words
            s = math.sqrt(var) if var > 0.1 else 1.0
            means[w] = m
            stdevs[w] = s

        return means, stdevs

    def compute_burrows_delta(
        self,
        candidate_text: str,
        target_text: str,
        corpus_means: Dict[str, float],
        corpus_stdevs: Dict[str, float]
    ) -> float:
        cand_freqs = self.compute_word_frequencies(candidate_text)
        target_freqs = self.compute_word_frequencies(target_text)
        delta_sum = 0.0
        for w in self.mfw_words:
            mean = corpus_means.get(w, 0.0)
            std = corpus_stdevs.get(w, 1.0)
            z_cand = (cand_freqs[w] - mean) / std
            z_target = (target_freqs[w] - mean) / std
            delta_sum += abs(z_cand - z_target)
        return delta_sum / len(self.mfw_words)

    def analyze_stylometric_affinity(
        self,
        generated_text: str,
        donor_corpus: str,
        target_original_corpus: str,
        reference_samples: List[str] = None
    ) -> Dict[str, float]:
        samples = reference_samples or [donor_corpus, target_original_corpus]
        means, stdevs = self.fit_corpus_statistics(samples)

        delta_to_donor = self.compute_burrows_delta(generated_text, donor_corpus, means, stdevs)
        delta_to_target = self.compute_burrows_delta(generated_text, target_original_corpus, means, stdevs)

        return {
            "delta_to_donor": round(delta_to_donor, 4),
            "delta_to_target": round(delta_to_target, 4),
            "donor_stylistic_affinity_ratio": round(delta_to_target / (delta_to_donor + 1e-6), 4)
        }
