import json
import re
import sys

def summarize_postings(file_path):
    with open(file_path, 'r') as f:
        postings = json.load(f)

    tech_keywords = [
        "React", "TypeScript", "Node.js", "PostgreSQL", "AWS", "Python", "Flask",
        "Docker", "Kubernetes", "Terraform", "Azure", "Vue.js", "JavaScript",
        "HTML5", "CSS3", "Tailwind CSS", "SQL", "Excel", "Tableau", "R",
        "Java", "Spring Boot", "Microservices", "Redis", "Go", "PyTorch",
        "Hugging Face", "vector databases", "LangChain", "Swift", "SwiftUI"
    ]

    grouped_data = {}

    for job in postings:
        exp = job.get("experience_required") or job.get("years_of_experience", 0)
        
        if exp < 3:
            continue
            
        location = job.get("location", "Unknown")
        description = job.get("description", "")
        
        found_keywords = [kw for kw in tech_keywords if re.search(rf"\b{kw}\b", description, re.IGNORECASE)]
        
        if location not in grouped_data:
            grouped_data[location] = []
        
        grouped_data[location].extend(found_keywords)

    for loc, tags in grouped_data.items():
        unique_tags = sorted(list(set(tags)))
        print(f"### {loc}")
        for tag in unique_tags:
            print(f"- {tag}")
        print()

if __name__ == "__main__":
    summarize_postings(sys.argv[1])
