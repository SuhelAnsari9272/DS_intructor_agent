router_prompt = """
You are an expert classifier.

Analyse the user query .

Return all domains that are required to answer the question completely.

- python
- sql
- excel
- ml

Also, provide a confidence for the selected domains based on the relevance with Question. (0.0 - 1.0)

Return only the structured output.

Question  : {query}
"""