import os
from crewai import LLM

class LLMConfig:
    """Centralized LLM configuration with fallback"""
    
    @staticmethod
    def get_llm(priority: str = "medium"):
        """
        Get LLM with fallback strategy
        priority: critical, medium, simple
        """
        groq_key = os.getenv("GROQ_API_KEY")
        
        if not groq_key:
            # Fallback to local Ollama
            return LLM(
                model="ollama/llama3.2:3b",
                base_url="http://localhost:11434",
                temperature=0.7
            )
        
        # Use Groq with appropriate model
        models = {
            "critical": "groq/llama-3.1-70b-versatile",  # Medical decisions
            "medium": "groq/llama-3.1-8b-instant",       # Logistics (10x cheaper)
            "simple": "groq/llama-3.1-8b-instant"        # Simple tasks
        }
        
        return LLM(
            model=models.get(priority, "groq/llama-3.1-8b-instant"),
            temperature=0.3 if priority == "critical" else 0.7
        )

    @staticmethod
    def enable_cache():
        """Enable response caching to reduce API calls"""
        os.environ["CREWAI_CACHE_ENABLED"] = "true"
        os.environ["CREWAI_CACHE_TTL"] = "3600"  # 1 hour
