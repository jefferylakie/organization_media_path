# An automated tool for organizing image and video storage paths.

## ✨ Key Features
- Auto-sorting: Automatically creates YYYY/mm folder structures within the source directory and moves media files to their corresponding dates.
- Filename Preservation: Keeps original filenames intact (ensures compatibility with iPhone Live Photos).
- Duplicate Handling: Skips files with duplicate names and displays the source file path for reference.

## 🚀 Usage

1. Initialize the environment
Requirements: Python 3.12 or higher.
```
git clone git@github.com:jefferylakie/organization_media_path.git
cd organization_media_path
python -m venv .venv
```

2. Activate the virtual environment:

Windows:
`.venv\\Script\\activate`

macOS / Linux:
`source .venv/bin/activate`

3. Install and Run:
```
pip install -r requirements.txt
python main.py
```
