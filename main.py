
from src.graph import create_workflow_graph
from utils.utils import save_graph


graph = create_workflow_graph()
instructor = graph.compile()
save_graph(instructor)

# user_question = "How do I train a Random Forest Model in Python?" 
# user_question = "How do I write a formula in Excel to JOIN two tables like SQL does?"
# user_question = "How do I build a logistic regression model using scikit-learn?"
user_question = "How do I optimize hyperparameters using GridSearchCV in sklearn?"
# user_question = "How to write sql queries using python library"
# user_question = "How does gradient descent work?"
# user_question  = "What is a decorator in Python ?"
# user_question = "Tell me about BlockChain"
# user_question  = "Tell me about MS Dhoni"

answer = instructor.invoke({"query": user_question})
print(answer)
# print(answer['final_response'])

print('-----------------------------------------------------------------------------')

# # #  debug
# for event in instructor.stream({"query": user_question}):    
#     print(event)