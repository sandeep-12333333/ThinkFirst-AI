# ThinkFirst AI
## Project User Guide, Demonstration Guide, and Viva Preparation

**Project type:** Streamlit-based reasoning-aware adaptive learning platform  
**Language:** Python  
**Persistence:** SQLite  
**Optional AI provider:** OpenAI API  
**Main entry file:** `app.py`

---

## 1. Project Summary

ThinkFirst AI is an educational application that asks students to attempt a problem and explain their reasoning before offering assistance. It evaluates the structure and quality of the explanation, identifies weak reasoning patterns, recommends progressively stronger support, and records progress in SQLite.

The project does not claim to understand every subject with perfect accuracy. The current “reasoning quality” score is a transparent text-based indicator based on explanation depth, justification words, sequential language, and relevance to the question. It is not an examination of factual correctness.

### Main project objective

The project aims to reduce AI dependency by encouraging this sequence:

> Independent Thinking → Reasoning Analysis → Adaptive Assistance → Socratic Challenge → Counterexample Testing → Independent Reassessment → Knowledge Transfer

### Implemented versus partially implemented

**Implemented:**

- Dashboard and navigation
- Think First Workspace
- Reasoning Lab
- Adaptive Tutor with three user-selectable levels
- Basic misconception detection
- Independent Challenge
- Learning Journey
- Reasoning DNA Profile
- Socratic Challenge Mode
- Explain My AI Decision
- Counterexample Laboratory
- Confidence versus reasoning-quality comparison
- AI Dependency Detector
- Knowledge Transfer Challenge
- SQLite persistence
- Optional OpenAI integration
- Local fallback prompts
- Visual assets and custom Streamlit styling

**Partially implemented or important limitations:**

- The reasoning engine is keyword-and-structure based, not semantic AI evaluation.
- It does not independently verify whether a factual answer is correct.
- “Accuracy” in Confidence versus Accuracy is explicitly a reasoning-quality proxy.
- The Independent Challenge creates a reusable local prompt rather than a complete subject-specific question bank.
- `Explain My AI Decision` currently explains a Level 1 or Level 2 decision in `core/intelligence_engine.py`; Level 3 is available in the Adaptive Tutor and in adaptive selection logic, but the explanation module does not yet contain a Level 3 branch.
- Socratic Challenge, Counterexample Laboratory, and Knowledge Transfer use the fallback prompt when no API key is available. They do not perform a domain-specific factual answer evaluation.
- The page files in `pages/` are empty. Navigation is controlled by `app.py`, not by those page files.
- `config.py` is empty and does not currently control application configuration.
- There is no authentication or real authorization system. The student name is used as a local SQLite identity.
- The system state is local to the application and database. It is not designed for secure multi-user deployment yet.
- No automated test suite is included in the repository.

---

## 2. Existing Features

## 2.1 Dashboard

### What it is

The Dashboard is the starting overview of the app. It shows a welcoming hero section, learning-attempt count, assistance-level count, the three-part learning principle, and cards linking conceptually to each workspace.

### Why it exists

It provides one clear entry point and communicates the learning philosophy: attempt first, understand, and use AI intelligently.

### Problem it solves

It gives students an overview instead of immediately exposing the student to a generic AI assistant.

### How it works internally

`app.py` initializes the student session, loads previous attempts from SQLite, and calculates the displayed attempt count from `st.session_state.attempts`. Navigation is controlled by the `workspace_menu` radio widget. The dashboard card data is rendered with Streamlit elements and custom HTML.

### Student usage

The student chooses another workspace from the sidebar or reads the project summary and principle.

### Output

- Learning-attempt count
- Three assistance-level count
- Reasoning-aware learning label
- Feature overview cards
- Learning principle message

### Example

Before the first submission, the Learning Attempts card shows `0`. After submitting and saving one response, it displays `1`.

---

## 2.2 Think First Workspace

### What it is

Think First collects the learning topic, question, and student’s initial explanation.

### Why it exists

The platform deliberately requires an initial attempt before support is available.

### Problem it solves

It prevents students from copying an immediate AI answer and creates a baseline for comparison and feedback.

### How it works internally

The student selects a topic and enters:

- A learning question
- Their own reasoning

The Submit button validates that both fields contain text. It then:

1. Adds the attempt to `st.session_state.attempts`
2. Calls `analyze_reasoning()`
3. Saves the attempt in SQLite
4. Saves an `initial_attempt` event

See `app.py`, `core/reasoning_engine.py`, and `database/db_manager.py`.

### Student usage

1. Select a learning area.
2. Enter a real question or problem.
3. Explain assumptions and steps, not just the final answer.
4. Submit My Thinking.

### Output

A recorded attempt and a message directing the student to the Reasoning Lab.

### Example

**Topic:** Artificial Intelligence

**Question:** “Why does a machine-learning model overfit?”

**Reasoning:** “I think it overfits because the model is too complex and memorizes the training examples. It may perform well on training data but not new data.”

### Database effect

The attempt is stored in the `attempts` table with topic, question, reasoning, score, confidence signal, and challenge flag.

---

## 2.3 Reasoning Lab

### What it is

Reasoning Lab analyses and presents the latest submitted attempt.

### Why it exists

It explains why the student’s reasoning appears strong or weak instead of only assigning a number.

### Problem it solves

It gives actionable feedback such as adding evidence, using numbered steps, or linking the explanation to the question.

### How it works internally

`analyze_reasoning()` counts:

- Explanation words and reasoning markers
- Sequential markers
- Uncertainty markers
- Relevance between question terms and response terms
- Approximate explanation length

The dimension formulas are:

- Depth: number of words / 45, capped at 100%
- Justification: reasoning markers / 3, capped at 100%
- Structure: step markers / 3, capped at 100%
- Relevance: common important question and answer terms / 3, capped at 100%

Overall score:

```text
30% Depth + 30% Justification + 20% Structure + 20% Relevance
```

The score is a proxy for explanation quality, not factual accuracy.

Reasoning Lab also sends the student text to `detect_misconceptions()`, which searches for:

- “always”
- “never”
- “guess”
- “obviously”
- “magic”
- excessive use of “and” or “or”

### Student usage

The student opens Reasoning Lab after submitting initial reasoning and reviews the score, dimensions, strengths, improvements, and misconception watch.

### Output

- Reasoning score out of 100
- Confidence signal
- Depth score
- Justification score
- Structure score
- Relevance score
- Strength statements
- Improvement statements
- Misconception warning or confirmation
- Button to open Adaptive Tutor

### Example

A 40-word response containing “because” and “first” can receive a higher structure and justification score than a 10-word final-answer-only response.

---

## 2.4 Adaptive Tutor

### What it is

Adaptive Tutor chooses a level of assistance based on the latest reasoning score and recorded hint history.

### The levels

#### Level 1 – Minimal Hint

Used when:

- The reasoning score is at least 70
- No repeated-hint condition forces stronger support

The purpose is to preserve independence. It identifies known and missing information without solving the problem.

#### Level 2 – Guided Question

Used when:

- The reasoning score is below 70
- Hint history is below the repeated-hint threshold

It asks the student to identify an assumption and explain or test it.

#### Level 3 – Structured Support

Used when:

- The reasoning score is below 40, or
- The student has recorded at least three hints

It provides more structure by organizing the response as claim, evidence, reasoning, and conclusion.

Level 3 is intended as a stronger support measure, not a complete answer generator.

### Why these levels exist

A single AI answer encourages copying and passive learning. Progressive support makes help depend on demonstrated understanding.

### How it works internally

`select_assistance_level()` in `core/adaptive_engine.py` reads:

- Latest reasoning score
- Number of `hint_used` events

The internal decision order is:

```text
If score < 40 OR hint_count >= 3: Level 3
Else if score < 70: Level 2
Else: Level 1
```

The student can manually override the recommendation through `st.segmented_control`. Recording assistance creates a `hint_used` event in SQLite.

### Student usage

1. Open Adaptive Tutor directly or from Reasoning Lab.
2. Review the recommended level and its reason.
3. Choose a level manually if needed.
4. Read the support prompt.
5. Record the assistance used.

### Output

- Recommended level name
- Level-specific prompt
- Override control
- Explanation of that level
- Recorded hint event
- Independence encouragement

### Example

If the latest reasoning score is 52 and no hint has been recorded, the app recommends Level 2:

> “Explain one assumption, then use it to make the next step.”

---

## 2.5 Misconception Detector

### What it is

A local, rule-based detector for suspicious wording.

### Why it exists

It helps identify unsupported absolute claims and weak explanation habits.

### Problem it solves

It warns students about possible misconceptions before a more complete answer is available.

### How it works internally

It converts reasoning to lowercase and applies regular-expression keyword checks.

Examples:

- “always” or “never” indicates possible absolute thinking.
- “guess” indicates unsupported speculation.
- “obviously” indicates an assumption may be unstated.
- “magic” indicates a missing explanation.
- Many “and” or “or” words indicate an unstructured explanation.

### Student usage

The detector appears automatically in Reasoning Lab. The student should read each warning and revise the explanation.

### Output

Specific warning strings or:

> “No obvious misconception cue was detected. Validate the reasoning with a counterexample.”

### Example

Input: “It never overfits if I use a lot of data.”

Output: “Absolute language (‘always’ or ‘never’) may hide important exceptions.”

### Limitations

It does not understand meaning. “Never” in a correctly worded explanation can still trigger it.

---

## 2.6 Independent Challenge

### What it is

A no-hint reassessment section that creates a simple challenge based on the latest confidence signal and topic.

### Why it exists

It verifies whether the student can maintain reasoning without repeating the original response.

### Problem it solves

It distinguishes initial effort from independent reassessment.

### How it works internally

`get_next_challenge()` reads the latest inferred confidence signal:

- “uncertain”: familiar problem plus one stated assumption
- “developing”: create a similar problem and explain why an alternative answer is wrong
- “confident”: defend the solution and construct a counterexample

The answer is analysed with `analyze_reasoning()` and stored with `is_challenge=True`.

### Student usage

1. Submit an initial attempt.
2. Open Independent Challenge.
3. Read the challenge.
4. Answer without selecting hints.
5. Submit independent answer.

### Output

- A challenge text
- Independent reasoning score
- SQLite attempt marked as a challenge
- `independent_attempt` event

### Example

For Artificial Intelligence, the system may ask:

> “Defend an overfitting solution, then construct a counterexample that tests it.”

---

## 2.7 Learning Journey

### What it is

A chronological history and progress line for all session attempts.

### Why it exists

It allows the student to observe improvement over several submissions.

### Problem it solves

One isolated score is less useful than a trend over time.

### How it works internally

The app combines session attempts, recalculates a reasoning analysis for each attempt, and creates a table with:

- Attempt number
- Reasoning score
- Confidence label
- Topic

It uses `st.line_chart()` to display score changes. It also lists previous questions and reasoning in expanders.

### Student usage

Open Learning Journey to view total attempts and revisit previous reasoning.

### Output

- Total attempts metric
- Reasoning progress line
- Previous question and reasoning history

### Example

Scores of 28, 52, and 67 show that later explanations are more detailed or structured.

### Persistence limitation

The page loads from session state. Session state is initialized from SQLite for the active student name, but page objects and widgets can still behave differently after a student name change until rerun. The database remains the permanent source.

---

## 3. Thinking Intelligence Lab Features

The Thinking Intelligence Lab is in `ui/thinking_lab.py` and uses the latest student attempt where possible.

## 3.1 Reasoning DNA Profile

### What it is

A four-dimension profile:

- Analytical thinking
- Logical reasoning
- Critical evaluation
- Evidence-based thinking

### Why it exists

It gives a broader picture than one overall reasoning score.

### Problem it solves

A student may explain a lot but provide no evidence, or provide evidence without structured steps.

### How it works internally

The four scores are calculated in `core/reasoning_engine.py`:

- Analytical thinking: 55% depth + 45% relevance
- Logical reasoning: 60% structure + 40% justification
- Critical evaluation: 50% justification + 50% critical markers
- Evidence-based thinking: evidence score

The Lab averages each dimension across all of the student’s attempts.

A Plotly radar chart displays the averages. If more than one analysis exists, a line chart displays overall reasoning-quality trend.

### Student usage

Open the Reasoning DNA tab to identify the weakest dimension and repeat work in that area.

### Output

- Radar chart
- Improvement trend after multiple attempts
- Averaged dimensions
- Weakest dimension value used for other decisions

### Example

A response may produce:

- Analytical: 43
- Logical: 60
- Critical: 50
- Evidence: 100

The weakest area is analytical thinking.

---

## 3.2 Socratic Challenge Mode

### What it is

A follow-up question system that prompts the student to defend or revise an explanation.

### Why it exists

Socratic questioning develops reasoning instead of immediately providing an answer.

### Problem it solves

It reveals hidden assumptions and missing links in the explanation.

### How it works internally

The UI reads the latest saved attempt and sends topic, question, and reasoning to `get_socratic_question()`. If no API key is available or the API call fails, it uses:

> “What assumption is most important to your explanation, and what evidence would support or weaken it?”

With an API key, OpenAI receives an instruction to create one concise follow-up question and avoid giving the final answer first.

The student response is scored and stored as a challenge attempt.

### Student usage

1. Open Socratic Challenge.
2. Read the question.
3. Defend or revise the explanation.
4. Submit the response.

### Output

- One follow-up question
- New reasoning score
- Challenge attempt in SQLite
- `socratic_response` event

### Example

> “If the model memorizes training data, what evidence would show that it has not learned general rules?”

---

## 3.3 Explain My AI Decision

### What it is

A transparent explanation of why the system chose the current assistance level.

### Why it exists

It makes the adaptive decision understandable rather than mysterious.

### Problem it solves

Students can see the score and weakest reasoning dimension associated with the support decision.

### How it works internally

`explain_assistance_level()` reads:

- Overall reasoning score
- Weakest DNA dimension

Its implemented decisions are:

- Score below 40: Level 2 explanation
- Score from 40 to 69: Level 2 explanation
- Score 70 or higher: Level 1 explanation

It returns the level name and two or three textual reasons.

### Student usage

Open the AI Decision tab and compare the displayed score with the listed reasoning weakness.

### Output

- Selected level
- Level name
- Reasoning-quality explanation
- Weakest measured dimension
- Rationale for minimal or guided support

### Current limitation

The central explanation module is separate from `core/adaptive_engine.py` and does not currently produce the Level 3 branch even though Adaptive Tutor can select Level 3. This should be aligned in future development.

---

## 3.4 Counterexample Laboratory

### What it is

A challenge that asks the student to test the original explanation against an alternative scenario.

### Why it exists

Counterexamples expose assumptions and exceptions.

### Problem it solves

A response may appear convincing for one case but fail under changed conditions.

### How it works internally

The app sends the topic, question, and latest reasoning to `get_counterexample()`. It uses OpenAI if configured or a generic fallback scenario otherwise:

> “Consider a scenario where one condition you assumed is false or reversed. Would your conclusion still hold?”

The revised explanation is analysed and stored as a challenge attempt.

### Student usage

1. Read the counterexample.
2. Defend the original explanation or revise it.
3. Submit revised reasoning.

### Output

- Counterexample prompt
- Revised reasoning score
- `counterexample_response` event
- Updated persisted attempt

### Example

If the original answer says extra data always solves overfitting, a counterexample could vary data quality or label noise.

---

## 3.5 Confidence vs Accuracy

### What it is

A calibration activity that compares the student’s confidence rating with the system’s reasoning-quality score.

### Why it exists

Students often become overconfident or underconfident even when their reasoning has a clear strength or weakness.

### Problem it solves

It makes students reflect on whether confidence matches demonstrated reasoning quality.

### How it works internally

The student chooses a confidence rating from 0 to 100. The system calculates:

```text
confidence gap = student confidence - reasoning-quality proxy
```

Labels:

- Gap within 10 points: Well calibrated
- Gap above 10: Overconfident
- Gap below -10: Underconfident

The UI saves the confidence and repeated reasoning score to SQLite and plots both values.

### Important distinction

“Accuracy” is only a **clearly labelled reasoning-quality proxy** in the current implementation. It does not compare with an expert answer or a verified factual correctness label.

### Student usage

1. Submit a reasoning attempt.
2. Choose confidence.
3. Record confidence.
4. Compare confidence and reasoning proxy across attempts.

### Output

- Calibration label
- Confidence percentage
- Reasoning-quality percentage
- Confidence calibration chart

### Example

Confidence: 85%  
Reasoning proxy: 58%  
Gap: 27  
Label: Overconfident

---

## 3.6 AI Dependency Detector

### What it is

A simple profile of hint usage and independent attempts.

### Why it exists

The app should encourage progressively less AI or hint dependence.

### Problem it solves

It makes reliance visible without merely counting visits.

### How it works internally

It counts:

- `hint_used` learning events
- Attempts with `is_challenge = 1`
- Average reasoning score across the five latest attempts

Profiles:

- No evidence yet
- Low dependence
- Moderate dependence
- Developing independence
- High dependence

The high-dependence branch requires at least three hints and no challenge marked in the latest attempt data.

### Student usage

Open Dependency Detector, review the hint count and independent attempts, and record a hint only when needed. Then complete an independent challenge.

### Output

- Dependency label
- Recorded hint count
- Independent-attempt count
- Recent average score
- Recommended next action

### Example

One hint and a recent average of 68 may produce “Moderate dependence.”

### Limitation

The implementation counts `is_challenge`, and also checks `is_independent` if that field ever exists. It does not verify that all independent work was performed without assistance.

---

## 3.7 Knowledge Transfer Challenge

### What it is

A task asking students to apply their learning to an unfamiliar context.

### Why it exists

Understanding a problem’s repeated pattern is not enough if a student cannot transfer the concept to a new situation.

### Problem it solves

It tests generalization and application rather than recall.

### How it works internally

The module reads the latest topic or defaults to “General University Learning.” It sends a prompt to OpenAI or uses a local fallback, and then scores the student response using `analyze_reasoning()`.

### Student usage

1. Open Knowledge Transfer.
2. Read the unfamiliar real-world problem.
3. Identify the relevant concept.
4. State assumptions and explain how the concept applies.
5. Submit independently.

### Output

- Real-world transfer prompt
- Independent response
- Reasoning score
- `knowledge_transfer` event
- Challenge attempt in SQLite

### Example

After learning about overfitting, a transfer task could involve a bank predicting loan default with limited or changing data.

---

## 4. SQLite Database

### Database file

`thinkfirst.db`

### Why SQLite is used

SQLite requires no separate database server, making the system easy to run locally for a student project or prototype.

### Tables

#### students

Fields:

- `id`
- `name`
- `created_at`

The student name is unique and used as a local identity. It is not authentication.

#### attempts

Fields:

- `id`
- `student_name`
- `topic`
- `question`
- `reasoning`
- `reasoning_score`
- `confidence_signal`
- `confidence_rating`
- `is_challenge`
- `created_at`

This table stores initial, revised, Socratic, counterexample, confidence, and transfer responses.

#### learning_events

Fields:

- `id`
- `student_name`
- `event_type`
- `details`
- `reasoning_score`
- `created_at`

This table records actions such as:

- `initial_attempt`
- `adaptive_support_requested`
- `hint_used`
- `independent_attempt`
- `socratic_response`
- `counterexample_response`
- `confidence_recorded`
- `knowledge_transfer`

### Communication

`app.py` calls `init_database()`, `ensure_student()`, `save_attempt()`, `save_event()`, `get_attempts()`, and `get_events()` from `database/db_manager.py`.

### Limitations

- No password or account security
- No role-based access
- No automatic cloud backup
- SQLite is suitable for a prototype or small local deployment, not as a scalable online multi-user system

---

## 5. OpenAI Integration and Local Fallback

### API configuration

Environment variables:

```text
OPENAI_API_KEY
OPENAI_MODEL
```

The `.env.example` file contains:

```text
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
```

`app.py` calls `load_dotenv()` and `core/llm_service.py` reads the environment variables.

### Implemented behavior

With an API key:

- Socratic mode requests one follow-up question
- Counterexample mode requests an alternative scenario
- Knowledge Transfer mode requests an unfamiliar real-world problem

The system instructs OpenAI not to reveal the final answer first and to encourage independent reasoning.

### Without an API key

The app continues using local fallback prompts:

- Socratic: assumption and evidence question
- Counterexample: reverse or alter one condition
- Transfer: incomplete-information application task

No API call is made when no key is configured.

### If an API call fails

The function catches exceptions and returns the fallback text.

### Security

The API key should remain in `.env` or environment variables. It should never be placed directly in source code or committed to GitHub.

---

## 6. Complete Learning Cycle

### Step 1: Student identity

The student enters a name in the sidebar. The app creates or finds that student in SQLite.

### Step 2: Independent thinking

The student chooses a topic, enters a question, and explains the first attempt in Think First.

### Step 3: Initial analysis

The app calculates score, four DNA dimensions, confidence signal, strengths, improvements, and misconception warnings.

### Step 4: Adaptive assistance

The student opens Adaptive Tutor through the Reasoning Lab or sidebar. The app recommends Level 1, 2, or 3 based on reasoning quality and hint history.

### Step 5: Socratic challenge

The student defends or revises the answer through a follow-up question.

### Step 6: Counterexample testing

The student applies or changes the explanation under a difficult alternative scenario.

### Step 7: Independent reassessment

The student submits the Independent Challenge without requesting the app to provide a full answer.

### Step 8: Knowledge transfer

The student applies the concept in a different real-world situation.

### Step 9: Profile update

Reasoning DNA averages the saved attempt data and shows an improvement trend when several attempts exist.

---

## 7. Practical AI Demonstration

### Example topic

**Artificial Intelligence — Machine Learning Overfitting**

### 7.1 Enter the question

**Topic:** Artificial Intelligence

**Question:**

> “Why does a machine-learning model overfit and how can overfitting be reduced?”

### 7.2 Submit initial reasoning

Example student response:

> “I think a model overfits because it is too complex and memorizes the training data instead of learning general patterns. For example, it may have very high training accuracy but lower test accuracy. The model could be made simpler or trained with regularization or more representative data.”

### 7.3 System analysis

Expected observations:

- The response includes “because,” “for example,” and an explanation of training versus test behavior.
- The score should be stronger than a one-sentence answer.
- The system may identify depth, justification, structure, and relevance.
- It may recommend Level 2 if the overall score is below 70.

The exact numerical score depends on word count and matched terms.

### 7.4 Adaptive Tutor

Example:

- Reasoning quality: 62/100
- No recorded hints
- Recommended level: Level 2 – Guided Question

Prompt:

> “Explain one assumption, then use it to make the next step.”

The student should examine the assumption that model complexity automatically causes overfitting.

### 7.5 Socratic Challenge

The system or local fallback asks:

> “What assumption is most important to your explanation, and what evidence would support or weaken it?”

Student response:

> “My assumption is that memorizing examples creates poor generalization. I would test this by comparing training and validation accuracy and checking whether performance falls on unseen data.”

### 7.6 Counterexample

Prompt:

> “Suppose a model is complex but receives large, diverse, regularly validated data. Would your original explanation still hold in exactly the same way?”

Revised answer:

> “Complexity may increase overfitting risk, but it does not guarantee overfitting. Data diversity, regularization, and validation strategy can affect the outcome.”

### 7.7 Independent Challenge

If confidence is developing, the generated prompt may be:

> “Create a similar machine-learning problem and explain why a plausible alternative answer is wrong.”

Student answer:

> “A model with high validation accuracy could still fail in a real deployment if the validation data comes from the same biased distribution. The alternative claim that high accuracy always proves generalization is wrong.”

The app calculates a reasoning-quality score and saves it as a challenge attempt.

### 7.8 Knowledge Transfer

Example transfer question:

> “A hospital wants to predict readmission using a small historical dataset that changes over time. Explain how overfitting risk should be managed.”

A strong student response would discuss representative data, temporal validation, regularization, and caution about low sample diversity.

### 7.9 Reasoning DNA Update

The radar chart may show:

- Analytical thinking: moderate
- Logical reasoning: improving
- Critical evaluation: improving after the counterexample
- Evidence-based thinking: strong if the student mentions validation and test data

The DNA values are recalculated as averages across saved attempts.

---

## 8. Technical Architecture

## 8.1 Python files

### `app.py`

Main entry point and UI controller.

Responsibilities:

- Loads environment variables
- Loads CSS
- Initializes SQLite
- Initializes session state
- Displays sidebar navigation
- Renders every existing workspace
- Saves initial and independent attempts
- Passes navigation to the Thinking Intelligence Lab

### `core/reasoning_engine.py`

Business logic for text-based reasoning analysis.

Responsibilities:

- Counts words and markers
- Calculates relevance
- Calculates overall reasoning quality
- Calculates DNA dimensions
- Produces strengths and improvements
- Infers confidence signal

### `core/adaptive_engine.py`

Business logic for progressive assistance.

Responsibilities:

- Defines Level 1, 2, and 3 prompts
- Recommends a level from score and hint count
- Generates the Independent Challenge prompt

### `core/misconception_detector.py`

Rule-based language checks.

Responsibilities:

- Identifies absolute language
- Identifies guess-like wording
- Identifies missing justification
- Identifies possible sequence problems

### `core/intelligence_engine.py`

Advanced learning analytics.

Responsibilities:

- Averages Reasoning DNA
- Explains adaptive decisions
- Calculates confidence calibration
- Calculates dependency profile
- Defines feature names

### `core/llm_service.py`

Optional AI prompt service.

Responsibilities:

- Reads API configuration
- Calls OpenAI if configured
- Generates Socratic, counterexample, and transfer prompts
- Provides local fallback text

### `database/db_manager.py`

SQLite persistence layer.

Responsibilities:

- Opens SQLite connection
- Creates tables
- Creates or ensures student records
- Saves attempts
- Saves events
- Retrieves attempt and event history

### `ui/thinking_lab.py`

UI module for the seven advanced features.

Responsibilities:

- Displays the seven tabs
- Builds Plotly radar chart
- Displays trend charts
- Records Socratic, counterexample, transfer, and confidence actions
- Shows dependency metrics

### `ui/__init__.py`

Marks the UI directory as a Python package.

### `database/` and `core/` directories

Contain separated business and persistence logic rather than putting every function in `app.py`.

### `config.py`

Currently empty. It is not used as the main configuration source. Environment variables are loaded directly in `app.py` and `llm_service.py`.

### `pages/` directory

Contains empty legacy page files. The app’s sidebar navigation is currently implemented inside `app.py`, so these files do not provide active functionality.

### `assets/` directory

Contains SVG logos and illustrations plus `styles.css`.

### `thinkfirst.db`

Actual SQLite database used by the application.

### `.env.example`

Template showing the optional API-key and model variables.

### `.env`

Optional local secrets file. It should not be committed.

### `requirements.txt`

Dependencies include Streamlit, OpenAI, dotenv, pandas, Plotly, and the option-menu package. The app currently does not depend on `streamlit-option-menu` for navigation after moving to Streamlit radio navigation.

---

## 9. How Modules Communicate

```text
Student enters data in app.py
        ↓
app.py calls reasoning_engine.py
        ↓
Reasoning score and DNA are produced
        ↓
app.py calls adaptive_engine.py
        ↓
Level 1, 2, or 3 is selected
        ↓
app.py and database/db_manager.py save the result
        ↓
Thinking Intelligence Lab reads SQLite history
        ↓
intelligence_engine.py and llm_service.py add advanced feedback
        ↓
Charts and recommendations are displayed in Streamlit
```

`app.py` remains the user-interface entry point. `ui/thinking_lab.py` is a presentation module for advanced features. `core/` contains calculations and AI prompt logic. `database/db_manager.py` is the persistence layer.

---

## 10. Formula Summary

### Overall reasoning score

```text
0.30 × depth
+ 0.30 × justification
+ 0.20 × structure
+ 0.20 × relevance
```

### DNA profile

```text
Analytical thinking = 55% depth + 45% relevance
Logical reasoning = 60% structure + 40% justification
Critical evaluation = 50% justification + 50% critical marker frequency
Evidence-based thinking = justification score
```

### Adaptive level

```text
Score below 40 OR at least 3 hint events → Level 3
Score below 70 → Level 2
Score 70 or above → Level 1
```

### Confidence calibration

```text
confidence - reasoning-quality proxy
```

Within ±10 points is considered well calibrated.

---

## 11. 25 Viva Questions and Simple Answers

### 1. What is ThinkFirst AI?

It is a Streamlit learning platform that asks students to attempt and explain a problem before receiving progressive assistance.

### 2. What is its main innovation?

It combines initial student reasoning, text-based reasoning analysis, adaptive support, challenge activities, and SQLite history into one learning cycle.

### 3. How is it different from ChatGPT?

ChatGPT usually gives direct conversational answers. ThinkFirst AI first asks for the student’s answer and encourages progressive independence rather than immediate complete assistance.

### 4. Why do we require an initial attempt?

It provides a baseline, shows the student’s existing thinking, and prevents the system from judging only the final answer.

### 5. Why use three assistance levels?

They provide progressive support. Level 1 gives the least help, Level 2 asks a guided question, and Level 3 provides structured support.

### 6. Is the reasoning score a factual answer score?

No. It currently measures explanation depth, evidence language, structure, and relevance. It is a proxy, not verified subject correctness.

### 7. What is Reasoning DNA?

It is an averaged four-dimension profile: analytical thinking, logical reasoning, critical evaluation, and evidence-based thinking.

### 8. How are DNA dimensions calculated?

They use combinations of word depth, question relevance, step markers, justification markers, and critical-language markers.

### 9. How does the misconception detector work?

It searches the reasoning text for specific words and language patterns such as “always,” “guess,” “obviously,” and excessive “and/or” structure.

### 10. What is the weakness of the misconception detector?

It is keyword based. It does not fully understand context or meaning.

### 11. What is Socratic learning?

It is a method of asking focused questions that lead the learner to discover weak assumptions or missing links.

### 12. Why use Socratic questioning?

It creates productive struggle and encourages self-explanation instead of copying an answer.

### 13. Why use counterexamples?

Counterexamples test whether an explanation remains valid when conditions change.

### 14. What does Explain My AI Decision do?

It explains that the system selected support using reasoning score and the weakest DNA dimension.

### 15. Is the Explain My AI Decision module fully aligned with Adaptive Tutor?

Currently it contains Level 1 and Level 2 explanations. Level 3 exists in Adaptive Tutor but is not yet fully explained by this module.

### 16. What does Confidence vs Accuracy measure?

It compares student confidence with a reasoning-quality proxy. It does not check factual correctness against a known answer.

### 17. How do you measure AI dependency?

The system counts recorded hint events and challenge attempts and compares them with recent reasoning scores.

### 18. How do hint counts affect the adaptive level?

At least three recorded hints can select Level 3 in Adaptive Tutor even if the score is otherwise high.

### 19. What is the Independent Challenge for?

It requires the student to submit an answer after initial analysis without using hints.

### 20. What is Knowledge Transfer?

It gives the student an unfamiliar real-world context and asks them to apply the learned concept.

### 21. Why is SQLite used?

SQLite is lightweight, local, persistent, and requires no separate database server, making it suitable for a prototype.

### 22. What is stored in SQLite?

Student names, attempts, reasoning scores, confidence ratings, challenge flags, and learning events.

### 23. What happens without an OpenAI API key?

The app uses local fallback prompts and remains usable. No external AI call is made.

### 24. What are the limitations?

The project does not have subject-specific correctness evaluation, authentication, a real factual knowledge model, or deep semantic misconception analysis.

### 25. How would you evaluate effectiveness?

Use a before-and-after experiment comparing reasoning scores, hint use, independent challenge performance, confidence calibration, and transfer scores across multiple sessions.

---

## 12. Professor Presentation Script: 5–7 Minutes

### Opening — 30 seconds

“Good morning. My project is ThinkFirst AI, a reasoning-aware adaptive learning platform. Unlike a normal chatbot that gives an answer immediately, this system asks the student to submit their own reasoning first and provides assistance progressively.”

### Dashboard — 40 seconds

“On the Dashboard, we can see the learning principle and workspace overview. The system currently has modules for initial thinking, reasoning analysis, adaptive support, independent reassessment, progress history, and advanced reasoning intelligence.”

### Student setup — 20 seconds

“I enter the student name. This name is used as a local identity in the SQLite database. It is not a secure login system.”

### Think First — 60 seconds

“In Think First, I select Artificial Intelligence and enter an overfitting question. I do not enter only the final answer. I explain my assumption and reasoning.”

Read the example question and paste a short answer.

Click **Submit My Thinking**.

“The system saves the attempt and immediately creates a score and analysis result.”

### Reasoning Lab — 60 seconds

“Reasoning Lab shows the overall reasoning-quality score and dimensions. It also identifies strengths, improvement areas, and possible misconception cues. The current score is not a factual correctness score; it is based on depth, justification, structure, and relevance.”

Click **Open Adaptive Tutor**.

### Adaptive Tutor — 50 seconds

“The adaptive engine uses the score and the number of recorded hints. A low score produces guided or structured support; a strong score produces a minimal hint. Level 3 is triggered by very low score or repeated hint use. The student can override the suggestion, and hint use is recorded.”

### Independent Challenge — 45 seconds

“Next, Independent Challenge asks for a reassessment without hints. It uses the topic and confidence signal to create a new task. The submitted response is saved as a challenge attempt.”

Enter an example revised response and submit it.

### Thinking Intelligence Lab — 90 seconds

“Finally, this lab contains seven deeper features. Reasoning DNA combines all saved attempts into four dimensions. Socratic mode asks a follow-up instead of giving an answer. Counterexample mode tests assumptions. Confidence calibration compares confidence with reasoning quality. Dependency detection counts hints and challenges. Knowledge Transfer asks the student to apply the concept to a new setting.”

Demonstrate Reasoning DNA and one of the remaining tabs.

### Database — 30 seconds

“The app persists students, attempts, confidence values, challenge flags, and learning events in SQLite. The database module initializes the tables when the app starts.”

### API fallback — 30 seconds

“For Socratic, counterexample, and transfer prompts, OpenAI is optional. If an API key exists, the app uses OpenAI with a Socratic instruction. If no key exists or the API fails, the app uses deterministic fallback prompts. Therefore, the project remains usable without external AI.”

### Closing — 30 seconds

“My main contribution is not an answer chatbot. It is a complete learning cycle that measures and develops independent reasoning, tracks dependence on assistance, and encourages transfer to new situations. The next step would be domain expert evaluation and larger student testing.”

---

## 13. Major Current Limitations

- Reasoning quality is lexical and statistical rather than semantic.
- Factual correctness is not checked by the current system.
- Misconception detection is rule based.
- Independent and confidence measures are limited proxies.
- OpenAI prompts are not evaluated for factual quality after generation.
- Student identity is not an authentication system.
- Level 3 and the Explain My AI Decision module are not fully synchronized.
- Legacy `pages/` files are empty.
- `config.py` is unused.
- No automated test suite is included.
- The reasoning data should be validated with educators and real student studies before claiming measurable learning effectiveness.

---

## 14. Suggested Future Improvements

1. Synchronize all Adaptive Tutor level decisions through one shared function.
2. Add a factual-answer reference or answer rubric for accuracy measurement.
3. Replace the misconception keyword detector with semantic embeddings or an LLM rubric.
4. Add real login and secure student accounts.
5. Store hint level and independent challenge results explicitly in dedicated columns.
6. Add a complete test suite for database operations and pure analysis functions.
7. Add a professor dashboard for aggregated class performance.
8. Add downloadable learning reports.
9. Add domain-specific knowledge structures for each selected topic.
10. Validate the scoring formula against human expert ratings.

---

## 15. Simple One-Sentence Feature Summary

- **Dashboard:** Project overview and starting point.
- **Think First:** Collects the student’s initial reasoning.
- **Reasoning Lab:** Explains the strengths and weaknesses of that reasoning.
- **Adaptive Tutor:** Provides progressively stronger support.
- **Misconception Detector:** Flags possible unsupported language patterns.
- **Independent Challenge:** Tests reassessment without AI hints.
- **Learning Journey:** Shows past attempts and score trends.
- **Reasoning DNA:** Displays four averaged reasoning dimensions.
- **Socratic Mode:** Uses follow-up questions instead of direct answers.
- **AI Decision:** Explains the assistance-level decision.
- **Counterexample Lab:** Challenges assumptions with alternative conditions.
- **Confidence Calibration:** Compares confidence with reasoning quality.
- **Dependency Detector:** Tracks hint use and independent attempts.
- **Knowledge Transfer:** Tests application in a new context.
- **SQLite:** Persistently stores learning records.
- **OpenAI/Fallback:** Generates optional prompts, with local prompts when unavailable.
