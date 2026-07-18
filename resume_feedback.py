import os
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

def generate_resume_feedback(resume_text: str, job_text: str) -> str:
    """Generates analytical feedback on missing parameters without inventing tools."""
    try:
        llm = OllamaLLM(model="llama3", temperature=0.0)
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an expert AI Career Coach and ATS specialist. "
                "Compare the candidate's resume with the job description and provide feedback.\n"
                "CRITICAL: When rewriting bullet points, you MUST ONLY use technologies and skills "
                "already explicitly written in the user's resume. Never assume or add skills like Tableau, "
                "SQL, or Python unless they are already present in the source text.\n\n"
                "Use ONLY these three headers for your output:\n\n"
                "### ATS KEYWORDS\n\n"
                "### STRONG BULLET POINTS\n\n"
                "### US FORMATTING CHECKS"
            )),
            ("user", (
                "Resume:\n{resume_text}\n\nJob Description:\n{job_text}"
            ))
        ])
        
        chain = prompt_template | llm
        return chain.invoke({"resume_text": resume_text, "job_text": job_text})
    except Exception as e:
        return f"Error connecting to Ollama: {e}"

if __name__ == "__main__":
    print("Module resume_feedback loaded cleanly.")