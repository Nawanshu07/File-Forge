# 🔨 File Forge

A modern, friendly, terminal-based file management and organization assistant built in Python.

File Forge turns tedious file housekeeping into a fast, visual, and painless experience right inside your command line.

---

## ✨ Features

- **🧹 Smart File Organizer**: Automatically scans loose files and groups them into clean categorized folders (`Images`, `Documents`, `Audio`, `Videos`, `Archives`, `Code & Scripts`, `Installers`, etc.) with collision-safe renaming.
- **🔍 Fast File Search**: Recursively search by full name, partial keyword, or file extension (e.g. `.pdf`), showing size and modification date.
- **⚡ Two-Phase Duplicate Detective**:
  - Phase 1 groups files by exact byte size (skips hashing unique files).
  - Phase 2 calculates chunked MD5 hashes only for matching candidates.
  - Shows wasted disk space and offers safe 1-click cleanup while keeping original copies.
- **📂 File Operations Suite**:
  - Open file with system default application (cross-platform).
  - Copy or move files safely (with directory auto-creation).
  - Rename files with duplicate prevention.
  - Delete files with safety confirmation prompts.
  - Detailed properties table (human-readable sizes, formatted dates, permissions).
- **📊 Disk & Storage Analyzer**:
  - Visual colored usage bar for any drive (`[████████░░░░] 65% used`).
  - System drive check (`C:\`).
  - Folder breakdown highlighting top 5 largest storage-hogging files.
- **🎨 Beautiful Terminal UI**: Powered by `rich` with colored panels, formatted tables, progress spinners, and humanized dialogue.

---

## 🚀 Getting Started

### 1. Requirements
- Python 3.10+
- `rich` library

### 2. Installation

Clone this repository and install dependencies:

```bash
git clone https://github.com/Nawanshu07/File-Forge.git
cd File-Forge
pip install -r requirements.txt
```

### 3. Run File Forge

```bash
python main.py
```

---

## 🛠️ Built With

- **Python standard library** (`pathlib`, `shutil`, `hashlib`, `os`)
- **[Rich](https://github.com/Textualize/rich)** for terminal styling and formatted tables

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
