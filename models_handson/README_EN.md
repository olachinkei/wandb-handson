# W&B Models Hands-on

[日本語版](README.md)

This hands-on guide introduces experiment tracking, data and model versioning, hyperparameter optimization, and result sharing with W&B Models.

## New to W&B Models?

For an overview of W&B Models features and value, see the [W&B Models documentation](https://docs.wandb.ai/models). A Japanese overview of W&B Models and Weave is also available on the [W&B Japan blog](https://note.com/wandb_jp/n/n94100f3961fc).

## W&B Account and Environment Setup

Before starting the hands-on, create a W&B account and obtain your API key.

The account setup process depends on your environment.

- **W&B Multitenant SaaS**
  - Go to [https://wandb.ai/](https://wandb.ai/) and create an account.
- **Dedicated Cloud or on-premises**
  - Ask your administrator to create a user account for you.
  - Log in from the link in the email you receive after the account is created.
  - Set `WANDB_BASE_URL` to the URL provided by W&B.
  - If login fails, a missing `WANDB_BASE_URL` is a common cause. Ask your administrator or W&B engineer for the correct URL.

**Team-Based Workspace Management**

W&B Models organizes experiments by Team, Project, and Run. A Team is the collaboration unit, and results are shared with members of the same Team. A Project is a folder-like unit under a Team, and a Run represents an individual experiment.

In Enterprise environments, only Admins can create Teams. Ask your Admin for an existing Team name or request a new Team. On the Free plan, you can create one Team.

## Hands-on Agenda

### 1. Experiment Tracking

- Organize Runs with Config, Tags, Group, and Job Type
- Log and compare training and validation metrics
- Use a custom X-axis and Summary Metrics

Script: `en/1_experiment.py`

### 2. Tables and Rich Media

- Log structured data with `wandb.Table`
- Visualize images and segmentation masks
- Compare Tables over time

Script: `en/2_table.py`

### 3. Artifacts

- Create Dataset and Model Artifacts
- Select input versions with `use_artifact()`
- Inspect Lineage across data generation, preprocessing, and training

Script: `en/3_artifacts.py`

### 4. Sweeps

- Create a Random Sweep
- Explore learning rate, epochs, and batch size
- Compare trials in the Sweep Dashboard

Script: `en/4_sweeps.py`

This script runs six local trials.

### 5. Registry

- Link an Artifact Version to a Registry Collection
- Configure Aliases, Tags, and the Collection Card
- Retrieve an Artifact from the Registry and inspect its Lineage

Script: `en/5_registry.py`

Before running this chapter, run `en/3_artifacts.py` to create the Model Artifact. You also need write access to the Registry.

You must also create the following Collection manually in the [W&B Registry](https://wandb.ai/registry/). The script does not create Collections.

1. Open the `models_handson` Registry. Create it in the UI if it does not exist.
2. Select **Create collection**.
3. Set the Collection name to `handson` and the Artifact type to `model`.
4. Confirm that the Target path is `wandb-registry-models_handson/handson`.

Details: [Create a collection](https://docs.wandb.ai/models/registry/create_collection#python-sdk-beta)

### 6. Reports

- Organize results with Run Sets and Panel Grids
- Visualize learning curves and Sweep parameter importance
- Create and share a Report draft

Script: `en/6_report.py`

This chapter uses Runs, Artifacts, and Sweep results created in the preceding chapters. The Report and Workspace API is in Public Preview; refer to the [official documentation](https://docs.wandb.ai/models/reports/create-a-report) for the latest behavior.

### 7. Extended Capabilities

- Resume a Run
- Query history through the Public API
- Log a PR Curve, Audio, and an Offline Run
- Inspect environment settings
- Send an Alert only when explicitly enabled

Script: `en/7_extended_capabilities.py`

### Notebook

`en/W&B_models_intro_notebook.ipynb` covers the main features in Jupyter Notebook format.

## Environment Setup and Running Scripts

### 1. Move to the project directory

```bash
cd models_handson
```

### 2. Set environment variables

First, log in to W&B. If you are already logged in, W&B uses your saved credentials.

```bash
wandb login
```

Next, configure the destination in `.env` at the root of `models_handson`.

```env
# Optional: explicitly select the destination W&B Team
WANDB_ENTITY=your_team_name

# Optional
WANDB_PROJECT=wandb-models-handson

# For Dedicated Cloud or on-premises
WANDB_BASE_URL=https://your-instance.wandb.io

# To use a different Registry Collection
WANDB_REGISTRY_TARGET_PATH=wandb-registry-models_handson/handson
```

If `WANDB_ENTITY` is omitted, the W&B SDK automatically selects the default Entity from your login. Set it when you want to explicitly select the destination Team. If `WANDB_PROJECT` is omitted, the scripts use `wandb-models-handson`. For W&B Cloud, open the Team page and use the `<ENTITY>` portion of its URL: `https://wandb.ai/<ENTITY>`.

Load every entry from `.env` as an exported environment variable so the Python process can access it:

```bash
set -a
source .env
set +a
```

> **Important:** Running only `source .env` against a file containing `WANDB_ENTITY=...` creates a shell variable but does not export it. Python therefore cannot read it through `os.getenv("WANDB_ENTITY")`. Use `set -a` as shown above, or write each entry in `.env` as `export WANDB_ENTITY=...`.

Verify the loaded value:

```bash
printenv WANDB_ENTITY
```

If you explicitly selected a destination in `.env`, the variable was loaded correctly when this prints your Team Entity. An empty result is still valid because the W&B SDK can use its default Entity. To pin the destination, confirm that the variable name is the uppercase `WANDB_ENTITY` and that you loaded `.env` in the same terminal.

Do not commit `.env` to Git because it may contain credentials.

### 3. Install dependencies

Use Python 3.11 or later and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 4. Run the pre-course check

Before starting the hands-on, verify authentication, dependencies, and the core workflow with one command:

```bash
python test.py
```

`test.py` runs the Japanese reference implementations in this order:

1. Experiment Tracking: log Runs, Config, and Metrics
2. Tables and Rich Media: log Tables, images, and masks
3. Artifacts: create Datasets, a Model, and Lineage
4. Reports: create a draft Report summarizing the results

This is not a dry run. It creates real Runs, Artifacts, and a draft Report in the currently selected W&B Entity and Project. Before the workflow starts, verify that the printed Entity, Project, and URL point to the intended destination.

The core pre-course check is complete when `ALL CHECKS PASSED` appears. If a chapter fails, fix the displayed error and run the same command again.

Sweeps, Registry, and Extended Capabilities are not included in this check.

### 5. Run a script

To run the first chapter:

```bash
python en/1_experiment.py
```

After the script finishes, open the Run URL printed in the terminal and inspect the logged Config, Metrics, Tags, and Group in the W&B UI.

To work through the chapters in order:

```bash
python en/1_experiment.py
python en/2_table.py
python en/3_artifacts.py
python en/4_sweeps.py
python en/5_registry.py
python en/6_report.py
python en/7_extended_capabilities.py
```

To use the notebook:

```bash
jupyter lab en/W\&B_models_intro_notebook.ipynb
```

## Important Notes

- The scripts log Runs and Artifacts to W&B. Verify the target Team and Project before running them.
- `en/4_sweeps.py` runs six Sweep trials.
- `en/5_registry.py` updates a manually pre-created Registry Collection. The default Target path is `wandb-registry-models_handson/handson`. Set `WANDB_REGISTRY_TARGET_PATH` to use a different Collection.
- `en/6_report.py` saves the Report as a private draft. Review it before publishing from the W&B UI.
- `en/7_extended_capabilities.py --demo alert` sends an external notification only when `--enable-alert` is also supplied.

## Resources

- **W&B Models Documentation**: [W&B Models](https://docs.wandb.ai/models)
- **Japanese Overview**: [W&B Models / Weave](https://note.com/wandb_jp/n/n94100f3961fc)
- **Experiments**: [Track experiments](https://docs.wandb.ai/models/track)
- **Tables**: [W&B Tables](https://docs.wandb.ai/models/tables)
- **Artifacts**: [W&B Artifacts](https://docs.wandb.ai/models/artifacts)
- **Sweeps**: [W&B Sweeps](https://docs.wandb.ai/models/sweeps)
- **Registry**: [W&B Registry](https://docs.wandb.ai/models/registry)
- **Reports**: [W&B Reports](https://docs.wandb.ai/models/reports)
