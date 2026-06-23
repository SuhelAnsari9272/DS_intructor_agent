from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from scipy.special import softmax

global domain_embeddings

domain_embeddings = None

python_desc = """
Python, functions, classes,
    decorators, generators, list comprehensions,
    pandas, numpy, flask, fastapi,
    object oriented programming, python debugging, args, kwargs,
    try, except, finally, deep copy, shallow copy, lambda function
"""

sql_desc = """
SQL queries, joins, group by, order by,
    database design, indexing, normalization,
    mysql, postgresql, database optimization, where , having, UNION, UNION ALL, 
    CASE, WHEN, CTE, common table expression, window function, group by clause,
    RANK(), ROW_RANK()
"""

excel_desc = """
Excel formulas, pivot tables, vlookup,
    xlookup, charts, dashboards,
    conditional formatting, spreadsheets, sumif, formula, absolute cell reference, 
    relative cell reference, dropdown list,
"""

ml_desc = """
Machine learning, deep learning,
    regression, classification,
    random forest, xgboost,
    neural networks, feature engineering,
    model evaluation, statistics, bias, variance, bais-variance tradeoff, overfitting,
    precision, recall, precision - recall tradeoff, bagging, boosting, L1, L2, regularization,
    k-means, clustering, cross-validation, PCA, principal component analysis, F1-score, confusion matrix,
    gradient descent, supervised, unsupervised
"""

embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def create_domain_embedding():

    try :
        domain_texts =  {
            "python" : python_desc,
            "sql" : sql_desc, 
            "excel" : excel_desc,
            "ml" : ml_desc
        }

        domain_names = list(domain_texts.keys())

        domain_descriptions = list(domain_texts.values())

        domain_embeddings = embedding_model.encode(domain_descriptions, normalize_embeddings=True)

        return domain_embeddings, domain_names
    
    except Exception as e : 
        print("Error in creating domain embeddings : ", e)

if domain_embeddings is None: 
    domain_embeddings, domain_names = create_domain_embedding()


def get_selected_domain(user_query, sf = 10, threshold = 0.30) : # 0.25  # scaling factor
    
    try :
        query_embedding = embedding_model.encode(user_query, normalize_embeddings=True )

        similarities = cosine_similarity( [query_embedding], domain_embeddings)[0]

        # for domain, score in zip(domain_names, similarities):
        #     print(domain, round(float(score), 4))

        probs = softmax(similarities *  sf)

        similarity_prob_dict = { domain : np.round(score,2) for domain, score in zip(domain_names, similarities)}

        entropy = -np.sum(probs * np.log(probs + 1e-10))
        entropy_norm = entropy / np.log(4)

        # Later we can use top similarity 
        selected_domains = []

        similarity_prob_dict = dict()

        for domain, prob in zip(domain_names, probs)  :
            similarity_prob_dict[domain] = prob

            if prob > threshold :
                selected_domains.append(domain)

        print(f"Query : {user_query} | Domain: {selected_domains}")
        print(f"Similarities : {similarity_prob_dict}")
        print(f"Entropy : {entropy} | Entropy_norm : {entropy_norm}")
        print()


        return selected_domains, entropy_norm
    
    except Exception as e: 
        print("Error in getting selected domain : ", e)
