# Stock Analysis Tool

## Installation
1. Clone the repository:
   ```sh
   git clone <repo_url>
   cd stock_analysis_tool
   ```
2. Install dependencies:
   ```sh
   python -m venv .stocks-analyzer
   source .stocks-analyzer/bin/activate
   pip3 install -r requirements.txt --break-system-packages
   ```

## Usage
### CLI Mode
Run the tool interactively:
```sh
python src/main.py
```

### API Mode
Start the Flask server:
```sh
python src/main.py
```
Access API endpoints at `http://localhost:5000`

### Web UI Mode
Run the Streamlit web app:
```sh
python src/main.py
```

### Deploy via Podman
Build and run the container:
```sh
podman build -t stock-analysis .
podman run -p 5000:5000 stock-analysis
```