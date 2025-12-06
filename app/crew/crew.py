import os
from crewai import LLM, Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

@CrewBase
class SystemeUrgencesMedicalesCrew:
    """SystemeUrgencesMedicalesCrew crew"""
    
    # Chemins relatifs depuis la racine du projet ou dossier app
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # --- AGENTS (Noms alignés avec agents.yaml) ---
    @agent
    def agentpatient(self) -> Agent:
        return Agent(
            config=self.agents_config["agentpatient"], # Doit matcher la clé YAML
            tools=[],
            verbose=True,
            llm=LLM(model="groq/llama-3.1-70b-versatile", temperature=0.7),
        )

    @agent
    def agentmedecinurgence(self) -> Agent:
        return Agent(
            config=self.agents_config["agentmedecinurgence"],
            tools=[],
            verbose=True,
            llm=LLM(model="groq/llama-3.1-70b-versatile", temperature=0.7),
        )

    @agent
    def agentcordonnateur(self) -> Agent:
        return Agent(
            config=self.agents_config["agentcordonnateur"],
            tools=[],
            verbose=True,
            llm=LLM(model="groq/llama-3.1-70b-versatile", temperature=0.7),
        )

    @agent
    def agentambulence(self) -> Agent:
        return Agent(
            config=self.agents_config["agentambulence"],
            tools=[],
            verbose=True,
            llm=LLM(model="groq/llama-3.1-70b-versatile", temperature=0.7),
        )

    @agent
    def agenthopital(self) -> Agent:
        return Agent(
            config=self.agents_config["agenthopital"],
            tools=[],
            verbose=True,
            llm=LLM(model="groq/llama-3.1-70b-versatile", temperature=0.7),
        )

    @agent
    def agentmedecinspecialiste(self) -> Agent:
        return Agent(
            config=self.agents_config["agentmedecinspecialiste"],
            tools=[],
            verbose=True,
            llm=LLM(model="groq/llama-3.1-70b-versatile", temperature=0.7),
        )

    @agent
    def agentadministratif(self) -> Agent:
        return Agent(
            config=self.agents_config["agentadministratif"],
            tools=[],
            verbose=True,
            llm=LLM(model="groq/llama-3.1-70b-versatile", temperature=0.7),
        )

    # --- TÂCHES ---
    @task
    def creer_l_alerte(self) -> Task:
        return Task(config=self.tasks_config["creer_l_alerte"])

    @task
    def analyse_medicale_d_urgence(self) -> Task:
        return Task(config=self.tasks_config["analyse_medicale_d_urgence"])

    @task
    def triage_patients_et_selection_ambulance(self) -> Task:
        return Task(config=self.tasks_config["triage_patients_et_selection_ambulance"])

    @task
    def traitement_du_specialiste(self) -> Task:
        return Task(config=self.tasks_config["traitement_du_specialiste"])

    @task
    def valider_la_demande_du_coordonnateur(self) -> Task:
        return Task(config=self.tasks_config["valider_la_demande_du_coordonnateur"])

    @task
    def recevoir_les_patients(self) -> Task:
        return Task(config=self.tasks_config["recevoir_les_patients"])

    @task
    def consolider_dossier_pour_ui(self) -> Task:
        return Task(config=self.tasks_config["consolider_dossier_pour_ui"])

    @crew
    def crew(self) -> Crew:
        """Creates the SystemeUrgencesMedicales crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True, 
        )