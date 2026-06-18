from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

python_desc = """
Python programming language, functions, classes,
    decorators, generators, list comprehensions,
    pandas, numpy, flask, fastapi, django,
    object oriented programming, python debugging
"""

sql_desc = """
SQL queries, joins, group by, order by,
    database design, indexing, normalization,
    mysql, postgresql, database optimization
"""

excel_desc = """
Excel formulas, pivot tables, vlookup,
    xlookup, charts, dashboards,
    conditional formatting, spreadsheets
"""

ml_desc = """
Machine learning, deep learning,
    regression, classification,
    random forest, xgboost,
    neural networks, feature engineering,
    model evaluation, statistics
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


domain_embeddings, domain_names = create_domain_embedding()


def get_selected_domain(user_query, threshold = 0.25) : 
    
    try :
        query_embedding = embedding_model.encode(user_query, normalize_embeddings=True )

        similarities = cosine_similarity( [query_embedding], domain_embeddings)[0]

        for domain, score in zip(domain_names, similarities):
            print(domain, round(float(score), 4))

        selected_domains = []
        cum_sum =  0.0

        for domain, score in zip(domain_names, similarities) :
            if score >= threshold : 
                selected_domains.append(domain)
                cum_sum = cum_sum + score


        print(selected_domains)
        print(cum_sum)

        return selected_domains, cum_sum
    
    except Exception as e: 
        print("Error in getting selected domain : ", e)



