from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from resume_parser import Resume_Parser
from job_parser import JdParser
import multiprocessing as mp
import os
import pprint
import json


def to_percentage(value):
    percentage = value * 100
    return "{:.2f}".format(percentage)


class MatchingEngine(object):
    def __init__(
            self,
            job_description,
            resumes: list[str],
            skills_file=None,
            custom_regex=None
    ):
        self.jd = job_description
        self.resumes = resumes
        self.parsed_jd = JdParser(job_description).get_extracted_data()
        self.parsed_resumes = []
        for resume in self.resumes:
            self.parsed_resumes.append(Resume_Parser(resume, skills_file, custom_regex).get_extracted_data())

        self.job_skills = [skill.lower() for skill in self.parsed_jd['skills']]
        self.resumes_skills = []

        for resume in self.parsed_resumes:
            batch = []
            for skill in resume['skills']:
                batch.append(skill.lower())
            self.resumes_skills.append(batch)

    def simple_intersection_score(self):
        rank = []
        for index, skills in enumerate(self.resumes_skills):
            job_skills = set(self.job_skills)
            resume_skills = set(skills)
            common_skills = set(job_skills).intersection(set(resume_skills))
            score = len(common_skills) / len(set(job_skills))
            rank.append({'name': self.parsed_resumes[index]['name'], 'score': to_percentage(score)})
        return rank

    def cosine_similarity_with_tfidf(self):
        rank = []
        for index, skills in enumerate(self.resumes_skills):
            vectorizer = TfidfVectorizer()
            vectors = vectorizer.fit_transform([" ".join(self.job_skills), " ".join(skills)])
            cosine_sim = cosine_similarity(vectors[0:1], vectors[1:2])
            score = cosine_sim[0, 0]
            rank.append({'name': self.parsed_resumes[index]['name'], 'score': to_percentage(score)})
        return rank

    def jaccard_similarity_score(self):
        rank = []
        for index, skills in enumerate(self.resumes_skills):
            job_skills = set(self.job_skills)
            resume_skills = set(skills)
            intersection = job_skills.intersection(resume_skills)
            union = job_skills.union(resume_skills)
            score = len(intersection) / len(union)
            rank.append({'name': self.parsed_resumes[index]['name'], 'score': to_percentage(score)})
        return rank


def matching_result_wrapper(jd, resumes: list[str]):
    parser = MatchingEngine(jd, resumes)
    return parser.simple_intersection_score()




def compare_profiles_with_expert(data):
    """
    Compares the skills of candidates and the job opening with an expert's skillset.

    Args:
        data (dict): A JSON object containing subjectData, candidateData, and expertData.

    Returns:
        list[dict]: A list of dictionaries containing similarity scores for each candidate.
    """
    subject_skills = data["subjectData"]["recommendedSkills"]
    expert_skills = data["expertData"]["skills"]
    candidates = data["candidateData"]

    # Initialize MatchingEngine with parsed skills directly
    engine = MatchingEngine(
        job_description={"skills": subject_skills},
        resumes=[{"name": candidate["name"], "skills": candidate["skills"]} for candidate in candidates]
    )

    # Collect similarity scores
    intersection_scores = engine.simple_intersection_score()
    cosine_scores = engine.cosine_similarity_with_tfidf()
    jaccard_scores = engine.jaccard_similarity_score()

    # Compile results
    results = []
    total_similarity = 0  # For calculating average similarity

    for i, candidate in enumerate(candidates):
        # Parse scores
        intersection_score = float(intersection_scores[i]["score"])
        cosine_score = float(cosine_scores[i]["score"])
        jaccard_score = float(jaccard_scores[i]["score"])

        # Calculate overall similarity (weighted average)
        overall_similarity = (intersection_score + cosine_score + jaccard_score) / 3
        total_similarity += overall_similarity

        # Append the candidate's results
        results.append({
            "name": candidate["name"],
            "intersection_score": intersection_score,
            "cosine_similarity": cosine_score,
            "jaccard_similarity": jaccard_score,
            "overall_similarity": round(overall_similarity, 2)
        })

    # Average similarity
    average_similarity = round(total_similarity / len(candidates), 2) if candidates else 0

    return results, average_similarity






if __name__ == '__main__':
    pool = mp.Pool(mp.cpu_count())

    resumes = []
    jds = []
    for root, directories, filenames in os.walk('files/res/pdf'):
        for filename in filenames:
            file = os.path.join(root, filename)
            resumes.append(file)

    for root, directories, filenames in os.walk('files/jd/pdf'):
        for filename in filenames:
            file = os.path.join(root, filename)
            jds.append(file)

    if not jds:
        print("No job description files found in 'files/jd/pdf'. Exiting.")
    elif not resumes:
        print("No resume files found in 'files/res/pdf'. Exiting.")
    else:
        # Perform matching only if both JDs and resumes are available
        results = [
            pool.apply_async(
                matching_result_wrapper,
                args=(jds[0], resumes)
            )
        ]

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

        # Process JSON Input
        result = compare_profiles_with_expert(json_input)
        # results = [p.get() for p in results]

        pprint.pprint(result)
