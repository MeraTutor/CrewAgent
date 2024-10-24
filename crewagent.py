import os
from crewai import Agent, Task, Crew, LLM, Process
#from crewai_tools import PDFSearchTool

#PDF tool

# Initialize LLM
llm = LLM(model="ibm/granite-20b-multilingual", temperature=0.3, verbose=True, api_key="XXXXXXXXXXXX")

# Collect concept from the user
user_concept = input("Please provide the concept you want to learn or quiz about: ")

# Define agents

# Tutor agent for explaining concepts
tutor_agent = Agent(
    role='AI Tutor for explaining concepts and clearing doubts',
    goal=f"""You are an AI tutor responsible for teaching concepts and helping students understand difficult topics. 
            The user has asked about {user_concept}. Explain the concept clearly with examples using only your knowledge.""",
    backstory="""You have helped students understand complex topics by using your knowledge base alone, without referring to any external documents. 
                You are user-friendly and skilled at simplifying complex ideas for students.""",
    verbose=True,
    allow_delegation=False,
    llm=llm,
    
)

# Quiz generator agent with multiple-choice questions (MCQ) format without answers
quiz_generator_agent = Agent(
    role='AI Quiz Generator',
    goal=f"""You generate multiple-choice quizzes of five questions based on the concept {user_concept}. 
            The quiz should include 4 options per question and should only display the questions and options, without providing the answers.""",
    backstory="""You generate quizzes based purely on your internal knowledge of the topic. The questions should be challenging, but only the questions and options should be provided.""",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# Quiz evaluator agent for generating answer keys and evaluating responses
quiz_evaluator_agent = Agent(
    role='AI Quiz Evaluator and Report Generator',
    goal=f"""You evaluate the student's quiz responses based on the concept {user_concept}, 
            providing grades, feedback, and a report card using only your internal knowledge. You also extract the correct answers after the quiz is generated.""",
    backstory="""You assess student performance, generate feedback, and extract the correct answer key based entirely on your knowledge of the topic. No external resources or documents are used during the evaluation.""",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

assignment_agent = Agent(
    role='AI Assignment Generator',
    goal=f"""You are an AI assignment generator responsible for creating a set of five targeted assignment questions. 
            Based on the student's areas of improvement from the quiz evaluation, you must provide questions that will help the student strengthen their understanding. 
            The assignment should focus on the areas of improvement. Provide a mix of theoretical and application-based questions.""",
    backstory="""You are highly experienced in identifying weak areas in students' understanding and generating assignments that target those areas to improve their knowledge and skills. 
                You provide challenging but appropriate questions that reinforce learning.""",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# Answer key extractor agent
answer_key_agent = Agent(
    role='AI Answer Key Generator',
    goal=f"""After a quiz is generated for the concept {user_concept}, extract the correct answer key. 
            For each question, identify the correct option and provide the answer key.""",
    backstory="""You generate answer keys based on the questions and options presented in the quiz, using your knowledge of the topic to identify the correct answers.""",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# Interactive flow

# Task 1: Explain the concept
explanation_task = Task(
    description=f"Explain the concept of {user_concept}.",
    agent=tutor_agent,
    expected_output=f"Detailed explanation of {user_concept}."
)

# Initialize crew with the tutor agent
crew_tutor = Crew(
    agents=[tutor_agent],
    tasks=[explanation_task],
    verbose=True
)

# Start explaining the concept
explanation_result = crew_tutor.kickoff()

# Check the structure of explanation_result and print the correct attribute
print("\n### Concept Explanation ###")
print(explanation_result)  # Use .output to extract the explanation if it's the correct attribute

# Ask user if they understood the concept
confirmation = input("\nDid you understand the concept? (yes/no): ").strip().lower()

if confirmation == 'yes':
    # Task 2: Generate the quiz
    quiz_task = Task(
        description=f"Generate a quiz based on {user_concept}.",
        agent=quiz_generator_agent,
        expected_output=f"A quiz with multiple-choice questions testing the understanding of {user_concept}."
    )

    crew_quiz_generator = Crew(
        agents=[quiz_generator_agent],
        tasks=[quiz_task],
        verbose=True
    )

    # Generate quiz
    quiz_result = crew_quiz_generator.kickoff()
    print("\n### Quiz Generated ###")

    # Assuming the quiz result contains the questions and options
    quiz_questions = quiz_result  # Correct attribute to access the result
    print(quiz_questions)  # Display all questions and options

    # Task 3: Extract the correct answer key using answer_key_agent
    answer_key_task = Task(
        description=f"Extract the only correct answer option (example a,c,b) for the generated quiz on {quiz_questions}.and return that options only",
        agent=answer_key_agent,
        expected_output=f"Correct answers option for the generated quiz."
    )

    crew_answer_key_extractor = Crew(
        agents=[answer_key_agent],
        tasks=[answer_key_task],
        verbose=True
    )

    # Get the answer key
    answer_key_result = crew_answer_key_extractor.kickoff()
    correct_answers = answer_key_result  # Assuming the output is a list of correct answers (e.g., ['b', 'a', 'c', ...])
    #print("\n### Correct Answer Key ###")
    #print(correct_answers)

    # Collect user's answers all at once
    print("\nPlease answer all the questions. Enter your answers as letters separated by commas (e.g., a,b,c,d):")
    user_answers = input("Your answers: ")
    # Task 4: Evaluate the user's answers (no need for a direct argument in kickoff)
    quiz_evaluation_task = Task(
        description=f"Evaluate the student's responses to the {user_answers} quiz by comparing it with {correct_answers} and generate feedback.",
        agent=quiz_evaluator_agent,
        expected_output=f"Feedback and grades based on quiz performance."
    )

    # Create a crew for the evaluator agent
    crew_quiz_evaluator = Crew(
        agents=[quiz_evaluator_agent],
        tasks=[quiz_evaluation_task],
        verbose=True
    )


    print("\n### Quiz Evaluation and Feedback ###")
    #print(f"You answered {score} out of {total_questions} questions correctly.")
    feedback = crew_quiz_evaluator.kickoff()
    print(feedback)
else:
    print("No worries! Let me explain the concept again.")
    explanation_result = crew_tutor.kickoff()
    print(explanation_result)
