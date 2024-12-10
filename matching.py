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


class MatchingEngine:
    def __init__(self, job_skills, candidates):
        self.job_skills = [skill.lower() for skill in job_skills]
        self.resumes_skills = [[skill.lower() for skill in candidate['skills']] for candidate in candidates]
        self.candidates = candidates

    def simple_intersection_score(self):
        rank = []
        for index, skills in enumerate(self.resumes_skills):
            job_skills_set = set(self.job_skills)
            resume_skills_set = set(skills)
            common_skills = job_skills_set.intersection(resume_skills_set)
            score = len(common_skills) / len(job_skills_set) if job_skills_set else 0
            rank.append({'name': self.candidates[index]['name'], 'score': to_percentage(score)})
        return rank

    def cosine_similarity_with_tfidf(self):
        rank = []
        for index, skills in enumerate(self.resumes_skills):
            vectorizer = TfidfVectorizer()
            vectors = vectorizer.fit_transform([" ".join(self.job_skills), " ".join(skills)])
            cosine_sim = cosine_similarity(vectors[0:1], vectors[1:2])
            score = cosine_sim[0, 0]
            rank.append({'name': self.candidates[index]['name'], 'score': to_percentage(score)})
        return rank

    def jaccard_similarity_score(self):
        rank = []
        for index, skills in enumerate(self.resumes_skills):
            job_skills_set = set(self.job_skills)
            resume_skills_set = set(skills)
            intersection = job_skills_set.intersection(resume_skills_set)
            union = job_skills_set.union(resume_skills_set)
            score = len(intersection) / len(union) if union else 0
            rank.append({'name': self.candidates[index]['name'], 'score': to_percentage(score)})
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
        dict: A dictionary containing profile score, relevancy score, and candidate matching results.
    """
    subject_skills = set(data["subjectData"]["recommendedSkills"])
    expert_skills = set(data["expertData"]["skills"])
    candidate_skills = [set(candidate["skills"]) for candidate in data["candidateData"]]

    # Aggregate all candidate skills
    aggregated_candidate_skills = set().union(*candidate_skills)

    # Calculate Profile Score
    profile_score = len(expert_skills.intersection(aggregated_candidate_skills)) / len(aggregated_candidate_skills) * 100

    # Calculate Relevancy Score
    job_match_score = len(expert_skills.intersection(subject_skills)) / len(subject_skills) * 100
    relevancy_score = (0.6 * profile_score) + (0.4 * job_match_score)

    # Candidate Matching Results
    results = []
    for candidate in data["candidateData"]:
        intersection_score = len(subject_skills.intersection(set(candidate["skills"]))) / len(subject_skills) * 100
        cosine_score = 100  # Placeholder; adjust if cosine similarity computation is included
        jaccard_score = len(subject_skills.intersection(set(candidate["skills"]))) / len(subject_skills.union(set(candidate["skills"]))) * 100
        overall_similarity = (intersection_score + cosine_score + jaccard_score) / 3

        results.append({
            "name": candidate["name"],
            "intersection_score": round(intersection_score, 2),
            "cosine_similarity": round(cosine_score, 2),
            "jaccard_similarity": round(jaccard_score, 2),
            "overall_similarity": round(overall_similarity, 2)
        })

    return {
        "profile_score": round(profile_score, 2),
        "relevancy_score": round(relevancy_score, 2),
        "candidates": results
    }



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



        # Process JSON Input
        #result = compare_profiles_with_expert(json_input)
        # results = [p.get() for p in results]

        pprint.pprint(result)