import json
from matching import compare_profiles_with_expert  # Replace with your module name

def main():
    # Example JSON Input
    json_input = {
        "subjectData": {
            "title": "React Developer",
            "recommendedSkills": ["React", "JavaScript", "HTML", "CSS"]
        },
        "candidateData": [
            {
                "name": "John Doe",
                "skills": ["React", "JavaScript", "HTML", "CSS"]
            },
            {
                "name": "Jane Doe",
                "skills": ["React", "JavaScript", "HTML"]
            },
            {
                "name": "Jim Doe",
                "skills": ["React", "JavaScript", "CSS"]
            }
        ],
        "expertData": {
            "name": "Expert",
            "skills": ["React", "JavaScript", "HTML", "CSS"]
        }
    }

    # Call the function and get results
    output = compare_profiles_with_expert(json_input)

    # Extract profile and relevancy scores
    profile_score = output["profile_score"]
    relevancy_score = output["relevancy_score"]
    results = output["candidates"]

    # Print the scores
    print(f"Profile Score: {profile_score}%")
    print(f"Relevancy Score: {relevancy_score}%\n")

    # Print the candidate matching results
    print("Matching Results:")
    for result in results:
        print(f"Candidate: {result['name']}")
        print(f"  Intersection Score: {result['intersection_score']}%")
        print(f"  Cosine Similarity: {result['cosine_similarity']}%")
        print(f"  Jaccard Similarity: {result['jaccard_similarity']}%")
        print(f"  Overall Similarity: {result['overall_similarity']}%\n")

if __name__ == "__main__":
    main()
