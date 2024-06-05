# FMEAApp

FMEAApp is a comprehensive Failure Modes and Effects Analysis (FMEA) tool designed to streamline your risk management processes. This application offers a user-friendly interface with dynamic screens and an intuitive top app bar, ensuring ease of use and productivity.

## Features

- **Dynamic Screen Management**: Effortlessly switch between different analysis tables with our screen manager.
- **Top App Bar**: Access commonly used functions with ease using icon-based buttons for home, open file, save as, undo, redo, next screen, and previous screen.
- **Editable Tables**: Interactive FMEA tables with editable cells for Severity, Occurrence, Detection, and action plans.
- **Automated RPN Calculation**: Automatic calculation and color-coded visualization of Risk Priority Numbers (RPN).
- **File Operations**: Seamlessly open, save, and manage FMEA tables in various formats including text, JSON, XML, and SQL.
- **Database Connectivity**: Ready for integration with databases to store and retrieve FMEA data.

## Installation

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/Dromation/FMEAApp.git
    cd FMEAApp
    ```

2. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Run the Application**:
    ```bash
    python fmea_app.py
    ```

## Building the Executable

To build the executable using PyInstaller, follow these steps:

1. **Increase Recursion Limit and Build**:
    ```bash
    python build.py
    ```

## Requirements

- Python 3.6 or higher
- PIL (Pillow)
- Tkinter
- PyInstaller

## Known Issues
Platform Specific: Some features may not work as expected on non-Windows platforms.
Icon Paths: Ensure that all icon paths are correctly set relative to the project directory.

## Contributing
We welcome contributions! Please fork this repository and submit pull requests with your improvements and bug fixes.

## License
This project is licensed under the GPL 3.0 License. See the LICENSE file for details.

## Contact
For questions or suggestions, please open an issue on GitHub.

## Branch Information

We recently merged a new branch `beta` with several enhancements and bug fixes. Coders looking to contribute or explore the latest features should check out the `beta` branch.

To switch to the `beta` branch:
```bash
git checkout beta

