# ThinkFirst AI – A Reasoning-Aware Adaptive Learning Platform

**Project:** ThinkFirst AI  
**Developer:** Sandeep Chouhan  
**Programme:** MSc Advanced Computer Science  
**University:** University of Birmingham  
**Repository:** https://github.com/sandeep-12333333/ThinkFirst-AI  
**Status:** Working prototype under development

## 1. Project Overview

ThinkFirst AI is a reasoning-aware adaptive learning platform designed to help students develop independent thinking, logical reasoning, critical evaluation and evidence-based explanations.

Unlike conventional AI chatbots that primarily provide direct answers, ThinkFirst AI encourages students to think independently before receiving assistance. It uses adaptive support, reasoning analysis and interactive learning activities to encourage active engagement with problems.

The main objective is to support meaningful human-AI collaboration while reducing unnecessary dependence on AI-generated answers.

## 2. Problem Statement

Generative AI tools can make learning more convenient, but students may become overly dependent on AI-generated explanations without independently evaluating information or developing their own reasoning.

ThinkFirst AI addresses this challenge through a think-first approach. Students are encouraged to explain their initial understanding, receive appropriate guidance and demonstrate their learning through independent challenges.

## 3. Key Features

### 3.1 Think First Workspace
- Allows students to enter a question or learning problem.
- Encourages students to submit their own understanding before receiving assistance.
- Promotes independent attempts before AI support.

### 3.2 Adaptive Assistance System
Provides three levels of assistance:

- **Level 1 – Minimal Hint:** Provides a small clue to encourage independent thinking.
- **Level 2 – Guided Question:** Uses questions to help students identify the next reasoning step.
- **Level 3 – Structured Support:** Helps students organise their explanation using claim, evidence, reasoning and conclusion.

### 3.3 Reasoning Lab
Evaluates the structure and quality of student explanations using four dimensions:

- Analytical depth – 30%
- Justification – 30%
- Structure – 20%
- Relevance – 20%

These scores are indicative measures of explanation quality, not validated measurements of intelligence or factual accuracy.

### 3.4 Misconception Detector
Identifies potential weaknesses in student explanations, such as unsupported statements, speculation and missing explanations.

### 3.5 Independent Challenge
Encourages students to create a similar problem, develop their own answer and explain why an alternative answer may be incorrect.

### 3.6 Reasoning DNA
Presents a four-dimensional reasoning profile:

- Analytical thinking
- Logical reasoning
- Critical evaluation
- Evidence-based thinking

### 3.7 Additional Learning Features
- Socratic Challenge
- Counterexample Laboratory
- Explain My AI Decision
- Confidence vs Accuracy
- AI Dependency Detector
- Knowledge Transfer Challenge
- Learning Journey

These features aim to encourage reflection, knowledge transfer and independent problem-solving.

## 4. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Streamlit | Interactive web interface |
| SQLite | Local data persistence |
| OpenAI API | Optional AI-assisted interactions |
| Session State | Interaction and application state management |

The application also includes local fallback behaviour for supported interactions when the external AI service is unavailable.

## 5. System Architecture

The application follows a modular architecture:

- `app.py` – Main application entry point.
- `core/` – Reasoning, adaptive assistance and intelligence logic.
- `ui/` – User interface components and learning activities.
- `database/` – SQLite database management.
- `pages/` – Application pages.
- `llm_service.py` – AI service integration.

The interface receives student input, passes it to the relevant reasoning and adaptive components, and displays feedback or assistance. Learning information can be stored through the database layer.

## 6. Installation and Execution

### Prerequisites
- Python 3.10 or later (use a version compatible with the installed dependencies).
- pip.
- Git.

### Clone the repository

```bash
git clone https://github.com/sandeep-12333333/ThinkFirst-AI.git
cd ThinkFirst-AI
```

### Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**macOS/Linux**
```bash
source .venv/bin/activate
```

**Windows**
```bash
.venv\Scripts\activate
```

### Install dependencies

If the repository contains `requirements.txt`:

```bash
pip install -r requirements.txt
```

Otherwise, install the dependencies listed in the project:

```bash
pip install streamlit
```

Install any other required packages identified by the project imports.

### Run the application

```bash
streamlit run app.py
```

Open the local URL displayed in the terminal.

## 7. Development Process and Design Decisions

The project was developed around the principle that students should attempt to reason independently before receiving AI assistance.

Key development decisions included:

1. Introducing a Think First Workspace to encourage independent attempts.
2. Developing three assistance levels to provide different amounts of support.
3. Introducing reasoning dimensions to provide structured feedback.
4. Adding independent challenges to encourage knowledge transfer.
5. Introducing a Learning Journey to retain a record of learning activity.

The development process involved implementing application components, integrating the interface with reasoning logic, and refining the interaction flow.

**Development evidence:** See the repository commit history and project files for implementation changes. Add a dated development log below describing the actual changes, reasons and checks performed.

## 8. AI Tools and Development Assistance

AI-assisted development tools were used to support selected development activities, such as:
- Exploring implementation approaches.
- Supporting code development and debugging.
- Improving interface and interaction ideas.
- Reviewing explanations and documentation.

AI-generated suggestions were treated as assistance rather than automatically accepted solutions. Code and outputs were reviewed against the application requirements and checked through manual inspection and application execution.

The developer remains responsible for the final implementation and verification.

## 9. Limitations

The current prototype has several limitations:

- Reasoning analysis is based on rule-based indicators and text structure rather than complete semantic understanding.
- Reasoning scores do not establish whether an answer is factually correct.
- Confidence comparison uses reasoning-quality scores as a proxy; it does not measure factual accuracy.
- The AI Dependency Detector analyses interaction patterns and is not a validated psychological assessment.
- AI-generated content may require independent verification.
- The application has not yet been evaluated through a controlled user study.
- Automated test coverage is not currently established.

## 10. Future Development

Potential improvements include:

- Improving semantic evaluation of student reasoning.
- Strengthening misconception detection.
- Improving the consistency of AI decision explanations across all assistance levels.
- Adding automated tests for reasoning calculations, adaptive assistance and database operations.
- Conducting user evaluations to investigate the impact on independent learning.

## 11. Academic Context

This project builds on the Assignment 1 literature review, *Human-AI Interaction in Higher Education: A Critical Review of Generative AI, Cognitive Offloading, and Student Learning*.

The project explores how an interactive learning system can encourage students to engage critically with AI assistance rather than relying entirely on generated answers.

## 12. Author

**Sandeep Chouhan**  
MSc Advanced Computer Science  
University of Birmingham

GitHub: https://github.com/sandeep-12333333/ThinkFirst-AI
