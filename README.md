# Lesson Design Agent

This repository contains the code used to run experiments for analyzing lesson designs with AI web agents. The system uses AI agents to navigate through Code in Place (CIP) lessons and generate descriptions, which are then used to predict student completion rates and dropout patterns.

This repository is built off the WebVoyager web agent: [WebVoyager](https://github.com/MinorJerry/WebVoyager.git)

## Overview

The repository consists of three main components:
1. **Agent Runner**: AI agents that navigate through CIP lessons and generate descriptions
2. **Prediction Models**: Systems that predict student completion rates and dropout distributions
3. **Evaluation Tools**: Scripts to evaluate prediction accuracy

## Prerequisites

### Required Data (Not Included)
Due to privacy reasons, the following data is not included in this repository:

1. **Code in Place Credentials**: You need valid CIP account credentials to run agents on the site
   - Place credentials in `agent_runner/credentials/cip_agent_credentials.json`
   - Format: List of dictionaries with `username` and `password` fields

2. **Code in Place Data**: Historical student data for prediction tasks
   - Student completion data
   - Dropout distribution data
   - Lesson video transcripts

### Environment Setup

```bash
# Create and activate conda environment
conda create -n agent python=3.10
conda activate agent

# Install dependencies
pip install -r requirements.txt

# Install Chrome WebDriver for Selenium
# Download from: https://chromedriver.chromium.org/
```

## Repository Structure

```markdown
learning-design-agent/
├── agent_runner/           # AI agent system for navigating CIP
│   ├── __main__.py        # Main entry point for running agents
│   ├── action_controller.py # Handles web interactions
│   ├── execution.py       # Task execution logic
│   ├── initializer.py     # Browser and task setup
│   ├── observation_helper.py # Screenshot and element detection
│   ├── prompt_helper.py   # System prompt generation
│   ├── thought_action_helper.py # GPT API integration
│   └── credentials/       # CIP account credentials (not included)
├── predict_completion/    # Student completion prediction system
│   ├── run_predict_completion.py # Main prediction script
│   ├── evaluate_predictions.py # Evaluation metrics
│   └── prompt_helper.py   # Prediction prompt generation
├── predict_dropout/       # Student dropout prediction system
│   ├── run_predict_dropout.py # Main prediction script
│   ├── evaluate_predictions.py # Evaluation metrics
│   └── prompt_helper.py   # Prediction prompt generation
├── cip_helpers/          # Data loading utilities
├── tasks/                # Task definitions and metadata
│   ├── all_tasks.json    # All CIP tasks
│   ├── completion_tasks.json # Tasks for completion prediction
│   └── dropout_tasks.json # Tasks for dropout prediction
└── requirements.txt      # Python dependencies
```

## Usage

### 1. Running AI Agents

To run AI agents through CIP lessons and generate descriptions:

```bash
# Run all lesson tasks (15 runs each)
python -m agent_runner

# Run with custom parameters
python -m agent_runner --max_threads 5 --headless True
```

**Output**: Agent descriptions are saved in `agents/{task_id}/run_{n}/` directories

### 2. Predicting Student Completion Rates

To predict student completion rates:

```bash
# Run completion predictions for all evaluation tasks
python -m predict_completion.run_predict_completion

# Output saved to: ./predictions/run_{n}.json
```

### 3. Predicting Student Dropout Patterns

To predict student dropout distributions for lessons:

```bash
# Run dropout predictions for all evaluation tasks
python -m predict_dropout.run_predict_dropout

# Output saved to: ./predictions/run_{n}.json
```

### 4. Evaluating Predictions

To evaluate prediction accuracy:

```bash
# Evaluate completion predictions
python -m predict_completion.evaluate_predictions

# Evaluate dropout predictions  
python -m predict_dropout.evaluate_predictions
```

## Configuration

### Agent Configuration

Key parameters in `agent_runner/task_loader.py`:
- `--max_threads`: Number of concurrent agent runs (default: 10)
- `--headless`: Run browser in headless mode (default: True)
- `--window_width/height`: Browser window dimensions
- `--max_attached_imgs`: Maximum screenshots in context (default: 3)

### Task Configuration

Tasks are defined in `tasks/` directory:
- `all_tasks.json`: Complete list of CIP tasks
- `completion_tasks.json`: Lesson tasks for completion prediction
- `dropout_tasks.json`: Lesson tasks for dropout prediction

## Data Requirements

### For Agent Execution
- Valid CIP account credentials
- Chrome WebDriver installed
- OpenAI API key configured

### For Prediction Tasks
- Historical student completion data
- Student dropout distribution data
- Lesson video transcripts
- Agent-generated descriptions from previous runs

## Troubleshooting

1. **Missing Credentials**: Ensure `agent_runner/credentials/cip_agent_credentials.json` exists with valid CIP accounts
2. **ChromeDriver Issues**: Download appropriate ChromeDriver version for your Chrome browser
3. **API Rate Limits**: The system uses multiple OpenAI API keys to handle rate limits
4. **Missing Data**: Prediction scripts require historical CIP data that is not included
