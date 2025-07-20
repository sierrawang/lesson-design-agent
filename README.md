# learning-design-agent

## Setup Environment

We use Selenium for web browsing automation. Follow these steps to set up:

**Set up Conda Environment**:
```bash
conda create -n agent python=3.10
conda activate agent
pip install -r requirements.txt
```

Started from clone of WebVoyager repository: [WebVoyager by MinorJerry](https://github.com/MinorJerry/WebVoyager.git)

* Run the descriptive agent
```bash
python -m agent_runner
```