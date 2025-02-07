from flask import Flask, request, jsonify, render_template
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json

app = Flask(__name__)

# Load mentors data
mentors_path = "mentors_with_embeddings.csv"
mentors_df = pd.read_csv(mentors_path)

# Convert embeddings from string back to list
mentors_df['embedding'] = mentors_df['embedding'].apply(lambda x: json.loads(x))

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

def find_best_mentors(query, top_n=5):
    """
    Finds the top N mentors based on the similarity of the user's query to mentors' embeddings.
    """
    query_embedding = model.encode(query).reshape(1, -1)
    mentors_df['similarity'] = mentors_df['embedding'].apply(
        lambda x: cosine_similarity(query_embedding, [x])[0][0]
    )
    top_mentors = mentors_df.sort_values(by='similarity', ascending=False).head(top_n)
    return top_mentors[['name', 'about', 'certifications', 'similarity']].to_dict(orient='records')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/find_mentor', methods=['POST'])
def find_mentor():
    data = request.json
    query = data.get('query', '')
    top_mentors = find_best_mentors(query)
    return jsonify(top_mentors)

if __name__ == '__main__':
    app.run(debug=True)
