<p align="center">
  <img src="logo.png" width="800" alt="Infinity Engine Logo">
</p>

# Infinity-Scan
Professional automation tool for recursive website crawling and deep-scan directory discovery.
=======
# Infinity Engine - Recursive Deep-Scan Suite

An adaptive, recursive web directory and file discovery tool written in Python, featuring live-site crawling to build automated, custom runtime lexicons on-the-fly.

---

## 🚀 Features

- **Dynamic Lexicon Generation**: Automatically parses `robots.txt` and sweeps live HTML structures to harvest targeted site keywords.
- **Adaptive Merging**: Dynamically infuses external workspace dictionary lists (like `common.txt`) into active runtime memory.
- **Recursive Scan Engine**: Implements a high-performance `deque` BFS loop to scan multi-level directories recursively.
- **Windows Click Protection**: Programmatically disables QuickEdit Mode inside Windows Command Prompt to prevent terminal click freezes and script pausing.
- **Visual Alert Isolation**: Interactive 5-second countdown buffers and target match outputs isolated strictly in high-visibility native ANSI Red terminal formatting sequence headers.

---

## 🛠️ Installation

### 🐧 Linux / macOS
# 1. Clone the repository
git clone [https://github.com/shadowkons/Infinity-Scan.git](https://github.com/AbhiSalim/Infinity-Scan.git)

# 2. Navigate to the project directory
cd Infinity-Scan

# 3. Install required libraries
pip install -r requirements.txt

# 4. Bash
python infinity.py


### 🪟 Windows (CMD / PowerShell)
# 1. Clone the repository
git clone [https://github.com/shadowkons/Infinity-Scan.git](https://github.com/AbhiSalim/Infinity-Scan.git)

# 2. Navigate to the project directory
cd Infinity-Scan

# 3. Install required target libraries
python -m pip install -r requirements.txt

# 4. CMD
python infinity.py
>>>>>>> a4ee417 (Initial commit: Core suite working structure)
