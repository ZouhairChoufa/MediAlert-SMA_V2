import os

from crewai import LLM
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task






@CrewBase
class SumiSystemeUrgenceMedicaleIntelligentCrew:
    """SumiSystemeUrgenceMedicaleIntelligent crew"""

    
    @agent
    def emetteur_d_alerte(self) -> Agent:
        
        return Agent(
            config=self.agents_config["emetteur_d_alerte"],
            
            
            tools=[],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            max_execution_time=None,
            llm=LLM(
                model="groq/llama-3.1-70b-versatile",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def medical_regulation_ai_triage(self) -> Agent:
        
        return Agent(
            config=self.agents_config["medical_regulation_ai_triage"],
            
            
            tools=[],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            max_execution_time=None,
            llm=LLM(
                model="groq/llama-3.1-70b-versatile",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def operational_regulation_chief(self) -> Agent:
        
        return Agent(
            config=self.agents_config["operational_regulation_chief"],
            
            
            tools=[],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            max_execution_time=None,
            llm=LLM(
                model="groq/llama-3.1-70b-versatile",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def mobile_intervention_pilot(self) -> Agent:
        
        return Agent(
            config=self.agents_config["mobile_intervention_pilot"],
            
            
            tools=[],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            max_execution_time=None,
            llm=LLM(
                model="groq/llama-3.1-70b-versatile",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def hospital_resource_manager(self) -> Agent:
        
        return Agent(
            config=self.agents_config["hospital_resource_manager"],
            
            
            tools=[],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            max_execution_time=None,
            llm=LLM(
                model="groq/llama-3.1-70b-versatile",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def clinical_protocols_engine(self) -> Agent:
        
        return Agent(
            config=self.agents_config["clinical_protocols_engine"],
            
            
            tools=[],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            max_execution_time=None,
            llm=LLM(
                model="groq/llama-3.1-70b-versatile",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def patient_interface_reporting(self) -> Agent:
        
        return Agent(
            config=self.agents_config["patient_interface_reporting"],
            
            
            tools=[],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            max_execution_time=None,
            llm=LLM(
                model="groq/llama-3.1-70b-versatile",
                temperature=0.7,
            ),
            
        )
    

    
    @task
    def creer_l_alerte(self) -> Task:
        return Task(
            config=self.tasks_config["creer_l_alerte"],
            markdown=False,
            
            
        )
    
    @task
    def analyse_medicale_d_urgence(self) -> Task:
        return Task(
            config=self.tasks_config["analyse_medicale_d_urgence"],
            markdown=False,
            
            
        )
    
    @task
    def triage_patients_et_selection_ambulance(self) -> Task:
        return Task(
            config=self.tasks_config["triage_patients_et_selection_ambulance"],
            markdown=False,
            
            
        )
    
    @task
    def traitement_du_specialiste(self) -> Task:
        return Task(
            config=self.tasks_config["traitement_du_specialiste"],
            markdown=False,
            
            
        )
    
    @task
    def valider_la_demande_du_coordonnateur(self) -> Task:
        return Task(
            config=self.tasks_config["valider_la_demande_du_coordonnateur"],
            markdown=False,
            
            
        )
    
    @task
    def recevoir_les_patients(self) -> Task:
        return Task(
            config=self.tasks_config["recevoir_les_patients"],
            markdown=False,
            
            
        )
    
    @task
    def consolider_dossier_pour_ui(self) -> Task:
        return Task(
            config=self.tasks_config["consolider_dossier_pour_ui"],
            markdown=False,
            
            
        )
    

    @crew
    def crew(self) -> Crew:
        """Creates the SumiSystemeUrgenceMedicaleIntelligent crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )

    def _load_response_format(self, name):
        with open(os.path.join(self.base_directory, "config", f"{name}.json")) as f:
            json_schema = json.loads(f.read())

        return SchemaConverter.build(json_schema)
