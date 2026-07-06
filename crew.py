from crewai import Crew
from agents.agent import agent
from agents.tasks import task

crew = Crew(
    agents= [agent],
    tasks = [task],
    verbose = True
)

print(crew.kickoff({"question":"What is the packging size of Ethyl acetate and alo tell its purity?"}))
