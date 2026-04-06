# Issues vs Fixes Report

This document outlines the issues identified in the repository and the steps taken to resolve them.

## 1. Duplicated Code in `database/database.py`
**Issue:** The Skymovies helper block (which included the `skymovies_collection`, `already_sent`, and `mark_as_sent` functions) was duplicated three times in the `database/database.py` file. This occurred due to repetitive append operations during earlier development stages.
**Fix:** The `database/database.py` file was cleaned to keep only one instance of the Skymovies helper block, ensuring maintainability and preventing confusion.

## 2. Leftover Utility Scripts
**Issue:** A utility script named `patch_readme.py` was left in the repository directory. This was an artifact from automated patching and shouldn't be included in the final codebase.
**Fix:** Removed `patch_readme.py` (and `fix_database.py` used in this session) from the repository completely.

## 3. Accidental Build Artifacts
**Issue:** `__pycache__` directories and `.pyc` compiled files were tracked by git and included in the repository structure.
**Fix:**
- Issued `git rm -r --cached` commands to remove all `__pycache__` and `.pyc` files from version control.
- Created a comprehensive `.gitignore` file that explicitly ignores byte-compiled Python files, cache directories, and local environment folders (`.env`, `venv/`).

## 4. Missing Dev Dependencies
**Issue:** The newly implemented testing suite relies on `pytest` and `pytest-asyncio`, but these packages were not listed in `requirements.txt`. A developer setting up a clean environment would encounter `ModuleNotFoundError` when attempting to run tests.
**Fix:** Appended `pytest` and `pytest-asyncio` to the `requirements.txt` file to ensure they are installed along with the core application dependencies.

## 5. Tight HTML Coupling (Noted Limitation)
**Issue:** The scraping modules (`tamilmv.py`, `skymovies.py`, and `search.py`) are tightly coupled to the specific HTML DOM structures of their target websites. If either TamilMV or Skymovies changes their markup (e.g., class names, layout), the parsers will fail.
**Fix (Strategic):** While we cannot control the external sites, this limitation is explicitly documented in the `README.md` under the "Failure Scenarios" and "Limitations" sections. Furthermore, the unit and integration testing suite created previously serves as a canary mechanism—if the sites update, the tests (when run against live HTML) or the localized mocks will need updating, immediately highlighting what broke.
