from crewai import LLM, Agent, Crew, Process
from crewai.project import CrewBase, agent, crew, task

@CrewBase
class ParallelSystemeUrgencesCrew:
    """Parallel processing crew for reduced latency"""
    
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @crew
    def crew(self) -> Crew:
        """Hierarchical process with manager agent"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.hierarchical,  # Parallel execution
            manager_llm=LLM(model="groq/llama-3.1-70b-versatile", temperature=0.3),
            verbose=True,
            cache=True,
            max_rpm=60,  # Rate limiting
        )

    # Group independent tasks that can run in parallel:
    # Group 1 (Parallel): Patient Alert + Medical Triage
    # Group 2 (Parallel): Hospital Search + Ambulance Search + Route Calc
    # Group 3 (Sequential): Final consolidation
