"""
# How to Package the Application into a Windows Executable

This guide provides step-by-step instructions on how to bundle the AI-Powered Text Summarizer into a single, standalone `.exe` file for Windows using PyInstaller.

## Prerequisites

Before you begin, ensure you have completed the following:

1.  **Project Setup**: The complete project structure and all Python files are in place.
2.  **Dependencies Installed**: You have installed all the project dependencies by running:
    ```bash
    pip install -r requirements.txt
    ```
3.  **PyInstaller Installed**: You have installed PyInstaller, which is the packaging tool.
    ```bash
    pip install pyinstaller
    ```
4.  **Application Icon**: An icon file named `icon.ico` must be present in the `assets/icons/` directory. This is specified in the `spec.spec` file and will be used as the icon for the final executable.

## The `spec.spec` File

We have already created a `spec.spec` file for you. This is a PyInstaller specification file that provides all the necessary configurations for building the application correctly. It tells PyInstaller:

-   Which script is the main entry point (`main.py`).
-   Which additional data files and folders to include (like our `assets` directory).
-   Which hidden imports are needed for libraries like `sumy` and `transformers` to work correctly.
-   To build a windowed, GUI-only application (no console window).
-   The name and icon for the final executable.

Using a `.spec` file is the most reliable way to build complex applications with PyInstaller.

## Building the Executable

Follow these steps to build the application:

1.  **Open a Terminal or Command Prompt**:
    Navigate to the root directory of the project, where the `spec.spec` file is located.
    ```bash
    cd path/to/your/AI-Powered-Text-Summarizer
    ```

2.  **Run the PyInstaller Command**:
    Execute PyInstaller, pointing it to the `.spec` file. This is the only command you need to run.
    ```bash
    pyinstaller spec.spec
    ```

3.  **Wait for the Build to Complete**:
    PyInstaller will now analyze the project, gather all dependencies, and build the executable. This process can take several minutes, especially the first time, as it bundles Python, PyQt6, and all the AI/NLP libraries into a single package.

    You will see a lot of output in your terminal as PyInstaller works. This is normal.

## Locating the Final Application

Once the build process is finished without errors, you will find two new directories in your project folder:

-   `build/`: Contains temporary working files used by PyInstaller.
-   `dist/`: This is where you will find the final, distributable application.

Inside the `dist/` directory, you will find a folder named `AI-Powered-Text-Summarizer`. Open this folder.

Inside, you will see `AI-Powered-Text-Summarizer.exe` along with several other files and folders (`.dll`s, etc.). This `.exe` file is your standalone desktop application!

**To run the application, simply double-click `AI-Powered-Text-Summarizer.exe`.**

You can zip the entire `dist/AI-Powered-Text-Summarizer` folder and distribute it to other Windows users. They will be able to run the application without needing to install Python or any dependencies.

---

That's it! You have successfully packaged your Python application into a professional, distributable Windows executable.
"""
