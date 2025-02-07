from transformers import pipeline
import pandas as pd

print("starting...")
# Load unique skills from CSV
skills_csv = 'unique_skills.csv'
skills_df = pd.read_csv(skills_csv)
skills_list = skills_df['Skill'].tolist()

# Initialize the zero-shot classifier
print("Initialize...")

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")


def predict_top_skills(profile_description, skills_list, top_n=20, threshold=0.5):
    """
    Predict the top N skills for a given profile description.

    Args:
        profile_description (str): Profile description.
        skills_list (list): List of candidate skills.
        top_n (int): Number of top skills to return.
        threshold (float): Minimum confidence score to include a skill.

    Returns:
        list: Top N matched skills sorted by confidence score.
    """
    # Perform zero-shot classification
    result = classifier(
        profile_description,
        candidate_labels=skills_list,
        multi_label=True
    )

    # Combine labels and scores, then filter by threshold
    skills_with_scores = [
        (skill, score) for skill, score in zip(result['labels'], result['scores']) if score > threshold
    ]

    # Sort by score in descending order and return top N
    top_skills = sorted(skills_with_scores, key=lambda x: x[1], reverse=True)[:top_n]

    return [skill for skill, _ in top_skills]  # Return only skill names


# Example profile
profile_description = "I have experience in leading engineering teams, software architecture, and cloud infrastructure."
top_skills = predict_top_skills(profile_description, skills_list, top_n=20, threshold=0.6)

print("Top 20 skills matched to the profile:")
print(top_skills)
