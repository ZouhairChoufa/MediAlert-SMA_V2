import os
from crewai import LLM, Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

@CrewBase
class OptimizedSystemeUrgencesCrew:
    """Optimized crew with hybrid LLM strategy"""
    
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def _get_llm(self, task_complexity: str):
        """Select LLM based on task complexity"""
        if task_complexity == "critical":
            # Use powerful model for medical triage
            return LLM(model="groq/llama-3.3-70b-versatile", temperature=0.3)
        else:
            # Use fast model for medium/simple tasks
            return LLM(model="groq/llama-3.1-8b-instant", temperature=0.5)

    @agent
    def agentpatient(self) -> Agent:
        return Agent(
            config=self.agents_config["agentpatient"],
            tools=[],
            verbose=True,
            llm=self._get_llm("medium"),  # Simple data normalization
        )

    @agent
    def agentmedecinurgence(self) -> Agent:
        return Agent(
            config=self.agents_config["agentmedecinurgence"],
            tools=[],
            verbose=True,
            llm=self._get_llm("critical"),  # Medical triage = critical
        )

    @agent
    def agentcordonnateur(self) -> Agent:
        return Agent(
            config=self.agents_config["agentcordonnateur"],
            tools=[],
            verbose=True,
            llm=self._get_llm("medium"),  # Logistics
        )

    @agent
    def agentambulence(self) -> Agent:
        return Agent(
            config=self.agents_config["agentambulence"],
            tools=[],
            verbose=True,
            llm=self._get_llm("simple"),  # Route calculation
        )

    @agent
    def agenthopital(self) -> Agent:
        return Agent(
            config=self.agents_config["agenthopital"],
            tools=[],
            verbose=True,
            llm=self._get_llm("simple"),
        )

    @agent
    def agentmedecinspecialiste(self) -> Agent:
        return Agent(
            config=self.agents_config["agentmedecinspecialiste"],
            tools=[],
            verbose=True,
            llm=self._get_llm("critical"),  # Medical protocols = critical
        )

    @agent
    def agentadministratif(self) -> Agent:
        return Agent(
            config=self.agents_config["agentadministratif"],
            tools=[],
            verbose=True,
            llm=self._get_llm("simple"),  # UI formatting
        )

    @task
    def creer_l_alerte(self):
        return Task(config=self.tasks_config["creer_l_alerte"])

    @task
    def analyse_medicale_d_urgence(self):
        return Task(config=self.tasks_config["analyse_medicale_d_urgence"])

    @task
    def triage_patients_et_selection_ambulance(self):
        return Task(config=self.tasks_config["triage_patients_et_selection_ambulance"])

    @task
    def traitement_du_specialiste(self):
        return Task(config=self.tasks_config["traitement_du_specialiste"])

    @task
    def valider_la_demande_du_coordonnateur(self):
        return Task(config=self.tasks_config["valider_la_demande_du_coordonnateur"])

    @task
    def recevoir_les_patients(self):
        return Task(config=self.tasks_config["recevoir_les_patients"])

    @task
    def consolider_dossier_pour_ui(self):
        return Task(config=self.tasks_config["consolider_dossier_pour_ui"])

    @crew
    def crew(self) -> Crew:
        """Optimized crew with parallel processing where possible"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,  # Can switch to hierarchical for parallel
            verbose=True,
            cache=True,  # Enable caching to reduce API calls
        )