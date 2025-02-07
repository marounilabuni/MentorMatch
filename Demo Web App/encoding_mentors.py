import pandas as pd
from sentence_transformers import SentenceTransformer


mentors_path = "mentor_scraped_data.csv"
mentors_df = pd.read_csv(mentors_path)

required_columns = ["Bio_x", "Skills_x"]

model = SentenceTransformer("all-MiniLM-L6-v2")

mentors_df["Bio_x"] = mentors_df["Bio_x"].fillna("").astype(str)
mentors_df["Skills_x"] = mentors_df["Skills_x"].fillna("").astype(str)

mentors_embeddings = model.encode(mentors_df["Bio_x"])

mentors_df["embedding"] = [list(x) for x in mentors_embeddings]
mentors_df.to_csv(mentors_path, index=False)
