import pandas as pd

# Load the profiles data CSV
profiles_csv = 'mentor_profiles_data.csv'  # Replace with your actual CSV file name
profiles_df = pd.read_csv(profiles_csv)

# Ensure the 'Skills_x' column exists
if 'Skills_x' in profiles_df.columns:
    # Split the skills and extract unique ones
    unique_skills = set()
    profiles_df['Skills_x'].dropna().apply(lambda x: unique_skills.update(skill.strip() for skill in x.split(',')))

    # Convert to a sorted list for better readability
    unique_skills = sorted(unique_skills)

    # Save the unique skills to a CSV file
    unique_skills_csv = 'unique_skills.csv'
    skills_df = pd.DataFrame(unique_skills, columns=['Skill'])
    skills_df.to_csv(unique_skills_csv, index=False, encoding='utf-8')

    print(f"Found {len(unique_skills)} unique skills.")
    print(f"Unique skills have been saved to {unique_skills_csv}")
else:
    print("Error: 'Skills_x' column not found in the CSV.")
