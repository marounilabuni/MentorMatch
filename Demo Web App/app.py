from flask import Flask, request, jsonify, render_template
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import os

app = Flask(__name__)

# Load mentors data
mentors_path = "linkedin_mentors.csv"
scraped_mentors_path = "mentor_scraped_data.csv"
scraped_mentors_df = pd.read_csv(scraped_mentors_path)
scraped_mentors_df['source'] = 'Web Scraping'
scraped_mentors_df['about'] = scraped_mentors_df['Bio_x']
scraped_mentors_df['name'] = scraped_mentors_df['Name']

scraped_mentors_df['embedding'] = scraped_mentors_df['embedding'].apply(lambda x: json.loads(x))


if os.path.exists(mentors_path):

    mentors_df = pd.read_csv(mentors_path)

    mentors_df['source'] = 'LinkedIn'

    mentors_df['embedding'] = mentors_df['embedding'].apply(lambda x: json.loads(x))

    mentors_df = pd.concat([mentors_df, scraped_mentors_df], ignore_index=True)
else:
    print('[!] LinkedIn data NOT FOUND, we will use scraped data only')
    mentors_df = scraped_mentors_df

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
    #mentors_df['similarity'] +=  0.2* (mentors_df['source'] == 'LinkedIn')
    top_mentors = mentors_df.sort_values(by='similarity', ascending=False).head(top_n)
    return top_mentors[['name', 'about', 'similarity', 'source']].to_dict(orient='records')

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
