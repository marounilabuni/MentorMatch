from flask import Flask, request, jsonify, render_template
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json

app = Flask(__name__)

# Load mentors data
mentors_path = "linkedin_mentors.csv"
mentors_df = pd.read_csv(mentors_path)
scraped_mentors_df = pd.read_csv(mentors_path)

mentors_df['source'] = 'LinkedIn'
scraped_mentors_df['source'] = 'Web Scraping'


# Convert embeddings from string back to list
mentors_df['embedding'] = mentors_df['embedding'].apply(lambda x: json.loads(x))
scraped_mentors_df['embedding'] = scraped_mentors_df['embedding'].apply(lambda x: json.loads(x))

mentors_df = pd.concat([mentors_df, scraped_mentors_df], ignore_index=True)


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
    return top_mentors[['name', 'about', 'certifications', 'similarity', 'source']].to_dict(orient='records')

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
