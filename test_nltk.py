import nltk
nltk.download('punkt_tab')

from nltk.tokenize import word_tokenize

nltk.data.path.append('C:/Users/osama/nltk_data')

text = "Show all employees in HR department."
tokens = word_tokenize(text.lower())
print(tokens)
