# Deduplication Example

Remove duplicate content from RAG retrieval results.

## Scenario

Your RAG system retrieved multiple similar chunks that contain overlapping information.

## Example Code

```python
from prompt_groomer import Groomer, Deduplicate

# RAG results with duplicates
rag_results = """
Python is a high-level programming language.

Python is a high level programming language.

Python supports multiple programming paradigms.
"""

groomer = Groomer().pipe(Deduplicate(similarity_threshold=0.85))
deduplicated = groomer.run(rag_results)

print(deduplicated)
# Output: Only unique paragraphs remain
```

## Adjusting Sensitivity

```python
# More aggressive (70% similarity)
groomer = Groomer().pipe(Deduplicate(similarity_threshold=0.70))

# Sentence-level deduplication
groomer = Groomer().pipe(Deduplicate(granularity="sentence"))
```

## Full Example

See: [`examples/compressor/deduplication.py`](https://github.com/JacobHuang91/prompt-groomer/blob/main/examples/compressor/deduplication.py)

## Related

- [Deduplicate API Reference](../api-reference/compressor.md#deduplicate)
- [Compressor Module Guide](../modules/compressor.md)
