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
    results, average_similarity = compare_profiles_with_expert(json_input)

    # Print the results in a readable format
    print("Matching Results:")
    for result in results:
        print(f"Candidate: {result['name']}")
        print(f"  Profile Score: {result['profile_score']}%")
        print(f"  Relevancy Score: {result['relevancy_score']}%")
        print(f"  Jaccard Similarity: {result['jaccard_similarity']}%")
        print(f"  Cosine Similarity: {result['cosine_similarity']}%")
        print(f"  Overall Similarity: {result['overall_similarity']}%\n")

    print(f"Average Similarity for all candidates: {average_similarity}%")

if __name__ == "__main__":
    main()
