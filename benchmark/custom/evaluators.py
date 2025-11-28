"""Quality evaluation metrics for benchmark."""

from typing import Dict, Any, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class CosineEvaluator:
    """
    Evaluate response similarity using cosine similarity of embeddings.

    Uses OpenAI's text-embedding-3-small model for generating embeddings.
    """

    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        """
        Initialize the cosine evaluator.

        Args:
            api_key: OpenAI API key
            model: Embedding model to use
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "OpenAI package is required for cosine evaluation. "
                "Install with: pip install openai"
            )

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def _get_embedding(self, text: str) -> list:
        """
        Get embedding for a text.

        Args:
            text: Input text

        Returns:
            Embedding vector as list
        """
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding

    def evaluate(self, response_a: str, response_b: str) -> Dict[str, Any]:
        """
        Evaluate similarity between two responses.

        Args:
            response_a: First response (raw)
            response_b: Second response (refined)

        Returns:
            Dictionary with:
            - similarity: Cosine similarity score (0-1)
            - equivalent: Boolean, True if similarity > 0.95
        """
        # Get embeddings
        emb_a = self._get_embedding(response_a)
        emb_b = self._get_embedding(response_b)

        # Calculate cosine similarity
        similarity = cosine_similarity(
            [emb_a],
            [emb_b]
        )[0][0]

        return {
            "similarity": float(similarity),
            "equivalent": similarity >= 0.95,
            "method": "cosine"
        }


class LLMJudgeEvaluator:
    """
    Evaluate response quality using LLM-as-a-judge approach.

    Uses GPT-4 to judge whether two responses are equivalent.
    """

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Initialize the LLM judge evaluator.

        Args:
            api_key: OpenAI API key
            model: Judge model to use (default: gpt-4o-mini for cost efficiency)
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "OpenAI package is required for LLM judge evaluation. "
                "Install with: pip install openai"
            )

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def evaluate(
        self,
        question: str,
        response_a: str,
        response_b: str
    ) -> Dict[str, Any]:
        """
        Evaluate whether two responses are equivalent using LLM judgment.

        Args:
            question: The original question/query
            response_a: First response (raw)
            response_b: Second response (refined)

        Returns:
            Dictionary with:
            - equivalent: Boolean, True if responses are judged as equivalent
            - confidence: Confidence score (0-1)
            - reasoning: Judge's explanation
        """
        prompt = f"""You are evaluating the quality of two AI responses to the same question.

Question: {question}

Response A (Original):
{response_a}

Response B (After Refining):
{response_b}

Task: Determine if Response B provides essentially the same information and quality as Response A.
Consider:
- Are the key facts the same?
- Is the information equally accurate?
- Is the answer equally complete?

Minor differences in wording or formatting are acceptable.

Respond in JSON format:
{{
    "equivalent": true or false,
    "confidence": 0.0 to 1.0,
    "reasoning": "brief explanation"
}}"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a precise evaluation assistant. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            response_format={"type": "json_object"}
        )

        import json
        result = json.loads(response.choices[0].message.content)

        return {
            "equivalent": result.get("equivalent", False),
            "confidence": result.get("confidence", 0.0),
            "reasoning": result.get("reasoning", ""),
            "method": "llm_judge"
        }


def evaluate_responses(
    question: str,
    response_raw: str,
    response_refined: str,
    cosine_evaluator: Optional[CosineEvaluator] = None,
    judge_evaluator: Optional[LLMJudgeEvaluator] = None
) -> Dict[str, Any]:
    """
    Evaluate responses using available evaluators.

    Args:
        question: Original question/query
        response_raw: Response from raw prompt
        response_refined: Response from refined prompt
        cosine_evaluator: Optional CosineEvaluator instance
        judge_evaluator: Optional LLMJudgeEvaluator instance

    Returns:
        Dictionary with evaluation results
    """
    results = {}

    if cosine_evaluator:
        results["cosine"] = cosine_evaluator.evaluate(
            response_raw,
            response_refined
        )

    if judge_evaluator:
        results["judge"] = judge_evaluator.evaluate(
            question,
            response_raw,
            response_refined
        )

    # Aggregate decision
    if "cosine" in results and "judge" in results:
        # Both must agree for overall equivalence
        results["overall_equivalent"] = (
            results["cosine"]["equivalent"] and
            results["judge"]["equivalent"]
        )
    elif "cosine" in results:
        results["overall_equivalent"] = results["cosine"]["equivalent"]
    elif "judge" in results:
        results["overall_equivalent"] = results["judge"]["equivalent"]
    else:
        results["overall_equivalent"] = None

    return results


if __name__ == "__main__":
    print("Evaluators module loaded successfully")
    print("Available evaluators: CosineEvaluator, LLMJudgeEvaluator")
