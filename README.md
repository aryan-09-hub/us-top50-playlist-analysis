# United States Top 50 Playlist Performance and Song Popularity Trend Analysis

An interactive Streamlit project for analyzing song rankings, chart longevity, artist appearances, and supplied popularity scores in the United States Top 50 playlist dataset.

## Project objectives

- Inspect and clean chart observations while preserving the raw source.
- Calculate days observed on chart, average and best rank, rank volatility, popularity trends, and artist performance.
- Explore ranking changes and available song, artist, explicit status, album type, duration, and track-count fields.
- Present findings in a Streamlit dashboard and concise research deliverables.

The initial data inspection found 27,800 rows and 10 columns in the supplied CSV. The app drops 10 exact duplicate rows in memory and excludes the malformed March 1, 2025 snapshot from ranking analyses. Read `reports/data_quality_report.md` for details and `reports/research_paper.md` for definitions and findings.

## Project structure

```text
.
├── app.py
├── .streamlit/config.toml   # Dark obsidian and emerald theme
├── data/
│   ├── raw/                 # Original input data; excluded from Git
│   └── processed/           # Cleaned outputs; excluded from Git
├── notebooks/initial_eda.ipynb
├── reports/
│   ├── data_quality_report.md
│   ├── executive_summary.md
│   └── research_paper.md
├── src/
│   ├── analysis.py
│   └── data_cleaning.py
├── tests/
├── requirements.txt
└── README.md
```

The preferred local dataset path is `data/raw/Atlantic_United_States.csv`; the original root-level file is unchanged. If that path is absent, the loader falls back to the tracked root-level `Atlantic_United_States.csv`. To use another CSV, set `PLAYLIST_DATA_PATH` to its path or pass a path to `load_dataset()` / `load_and_clean()`. The full methodology audit and item-by-item implementation checklist is in [`reports/methodology_checklist.md`](reports/methodology_checklist.md).

## Setup (Windows PowerShell)

Run these commands in the VS Code integrated terminal from the project folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
code .
```

If PowerShell blocks activation, use the environment's Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Use the notebook inside Visual Studio Code

1. Open this project folder in Visual Studio Code.
2. Install the recommended **Python** and **Jupyter** extensions from Microsoft when prompted.
3. Open `notebooks/initial_eda.ipynb` in the editor.
4. Select the `.venv` Python kernel in the notebook toolbar. If prompted, choose **Python Environments** and select `.venv\Scripts\python.exe`.
5. Run cells individually with **Run Cell**, or choose **Run All**.

The notebook uses the default `data/raw/` path, with the same root-file fallback as the dashboard. The `ipykernel` dependency lets VS Code run notebook cells in the selected virtual environment; a separate JupyterLab window is not needed.

## Run tests

```powershell
python -m pytest
```

## Launch the interactive dashboard

```powershell
streamlit run app.py
```

The left sidebar contains navigation and global filters. The analysis sections are Overview dashboard, Playlist trends, Song explorer, Artist analytics, Popularity analysis, Content attributes, and Data quality & methodology. Date, artist, song, chart position, and album type filters apply across sections. The first time you change `.streamlit/config.toml`, restart Streamlit for the theme settings to take effect.

To point the app at a different CSV for the current PowerShell session:

```powershell
$env:PLAYLIST_DATA_PATH = "C:\path\to\your\dataset.csv"
streamlit run app.py
```

## Deployment

For Streamlit Community Cloud, push the project to GitHub, open your Community Cloud workspace, choose **Create app**, and select the repository, branch, and `app.py` entrypoint. Keep `requirements.txt` in the repository root and `.streamlit/config.toml` in place. Follow the [official deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy).

The app needs the CSV at runtime. This checkout currently tracks `Atlantic_United_States.csv` at the repository root, so a clone can use the loader fallback if that file remains in the deployed branch. Confirm you have permission to redistribute the dataset before pushing or deploying it. If you remove it from the repository, provide the CSV through an authorized deployment method and configure its runtime path; a local `PLAYLIST_DATA_PATH` setting does not upload or mount a file in the cloud environment.

Keep analysis code in `src/`, exploration in `notebooks/`, generated data in `data/processed/`, and written findings in `reports/`. Do not commit private or large source datasets unless the repository explicitly requires them.
