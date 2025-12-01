## 1) Executive Summary

### Problem:  
Exploring a CSV file visually is generally a long-winded process of writing and troubleshooting code. For students or analysts who just want quick insight into a dataset, this setup process is slow and inconvenient. There is no simple, browser-based tool that lets a user generate clean visualizations without touching code.

### Solution:  
This project provides a fully containerized Flask-based CSV visualization application that runs with a single command. Users upload any CSV in the browser, select a variable (or pair of variables), and can easily generate histograms, bar charts, pie charts, and scatterplots. The app runs entirely inside a Docker container, ensuring reproducibility across any machine with Docker installed. This creates a simple and interactive way to explore datasets without writing code or installing Python packages.


## 2) System Overview

### Course Concept(s)
This project integrates the following key concepts from the course:
- Data Pipelines
- Flask Web API
- Containerization (Docker)
  
### Architecture Diagram

<img src="assets/architecture.png" width="300">

### Data / Services

**Data Sources**  
This project includes three example CSV datasets stored in `/datasets (csv)/`:

- `penguins.csv` — ~344 rows, <50KB  
- `movies.csv` — ~1,000 rows, <150KB  
- `insurance.csv` — ~1,338 rows, <200KB  

All datasets are standard CSV files and are publicly available educational datasets intended for non-commercial academic use. Users may also upload CSV files of their choosing from their machine through the web interface.

**Services**  
The system provides several coordinated services across the Flask backend, the visualization engine, and the containerized runtime:

---

#### 1. Flask Web Service (`app.py`)
This is the core application layer. It provides:

- **Routing and Endpoints**
  - `/health` — Returns `{"status":"ok"}` for health and container readiness checks.
  - `/home` — Main page for uploading CSV files and navigating visualizations.
  - `/histogram` — Generates a histogram of a selected numeric column.
  - `/barchart` — Produces a bar chart for a categorical column.
  - `/piechart` — Creates a pie chart for categorical distributions.
  - `/scatter` — Generates scatterplots for two numeric variables.

- **File Upload Handling**
  - Accepts uploaded CSV files from the user.
  - Validates file presence and CSV format.
  - Reads uploaded files into memory using Pandas.
  - Stores the uploaded dataset in a global DataFrame for all visualization routes.

- **Column Detection & Data Cleaning**
  - Identifies numeric vs. categorical columns.
  - Provides user-friendly dropdowns for column selection.
  - Displays error messages if invalid columns or files are chosen.
  - Validates user selections to prevent unsupported operations.


- **HTML Templating (Jinja2)**
  - Renders dynamic HTML templates located in `/templates/`.
  - Injects base64-encoded images directly into the returned HTML pages.

---

#### 2. Visualization Service (Matplotlib Engine)
This component transforms the DataFrame into generated plots:

- **Chart Rendering**
  - Histogram (continuous distributions)
  - Bar chart (categorical counts)
  - Pie chart (proportional relationships)
  - Scatterplot (numeric correlations)

- **Global Visualization Style**
  - Unified white background
  - Black edges and axes
  - Blue color palette 
  - Clean, minimal design

- **Image Encoding**
  - Converts Matplotlib figures to PNGs in memory.
  - Encodes images using base64 for HTML embedding.
  - Ensures the browser receives the plot without saving files to disk.

---

#### 3. Front-End Presentation Layer (HTML Templates)
Each visualization endpoint renders through dedicated templates:

- `home.html` — Upload form + navigation  
- `histogram.html` — Displays generated histogram  
- `bar.html` — Displays bar chart  
- `pie.html` — Displays pie chart  
- `scatter.html` — Displays scatterplot  

Templates dynamically show:
- The selected column(s)  
- The generated visualization image  
- Any error messages or invalid input notifications  

---

#### 4. Docker Runtime Environment
The entire system is packaged in a Docker container:

- **Environment Isolation**
  - Ensures Python version, packages, and runtime behavior are identical on all machines.

- **Dockerfile**
  - Installs dependencies from `requirements.txt`
  - Copies project files into the image
  - Configures Flask to run on port `8080`

- **One-Command Execution**
  - The `run.sh` script builds the image and launches the container.
  - Eliminates all environment conflicts or dependency issues.

- **Health Check Compatibility**
  - `/health` endpoint supports container orchestration readiness checks.
  - Allows quick verification that the app is running inside the container.

---

#### 5. Local Asset Service (for Documentation)
Stored example visualizations in `/assets/visualization_ex/` provide:

- Static examples for the README  
- Reference outputs for each visualization type  
- A baseline for visual verification  
  
## 3) How to Run

From the root of the repository, run:

./run.sh

This script automatically performs the following steps:

1. **Builds the Docker image**  
   Runs: docker build -t final-project-app:latest .  
   This constructs the Docker image using the project's Dockerfile.

2. **Runs the container on port 8080**  
   Runs: docker run --rm -p 8080:8080 --env-file .env.example final-project-app:latest  
   This launches the Flask application inside Docker.

3. **Performs a health check**  
   Runs: curl http://localhost:8080/health  
   If the response is {"status":"ok"}, the app is running correctly.

---

## 4) Design Decisions

### Why This Concept?
I chose to build an interactive visualization application because I thought it was a super interesting concept that solved a real world issue. Additionally, it incorporates multiple  course concepts in a clean, meaningful way, and showcases how these components fit together to create a self-contained, user-facing data tool.

### Why Flask?
Flask was the ideal choice because:

- It is lightweight and easy to understand/use.
- It supports file uploads and dynamic routing cleanly.
- It integrates seamlessly with Jinja2 and html templates.
- It was covered extensively in the course, making it the appropriate tool to demonstrate course concepts.
- Its simplicity keeps focus on visualization logic rather than framework complexity.

Potential alternatives included Django and FastAPI, but these were not covered in our course concepts, and would also have added complexity without providing meaningful benefits for a small, single-purpose app.

### Why Docker?
Docker was essential for meeting the project requirement of a single-command, reproducible run. Docker ensures:

- The application works identically on any machine.
- All dependencies are precisely defined in `requirements.txt`.
- No version mismatches, Python conflicts, or missing packages.
- Clean separation between the host system and the running application.
- A professional development workflow consistent with modern software engineering.

While Apptainer was also an option, the project is intended to run locally rather than on an HPC cluster, so Docker was the right fit.

### Tradeoffs

**Simplicity vs. Flexibility**  
A basic Flask app is simple and easy to maintain, but less interactive than a JavaScript-based dashboard. The focus of this project is clarity and reproducibility over feature-rich UI.

**Static Plots vs. Interactive Plots**  
Matplotlib produces static images. Tools like Plotly could create interactive plots, but they introduce heavier dependencies and additional complexity.

**Single-File Structure vs. Modular Architecture**  
Keeping most logic in `app.py` makes the project easier to understand but less modular. A larger project would break visualization logic into separate modules.

**Local Runtime vs. Cloud Deployment**  
Running locally ensures predictable behavior and avoids cloud configuration overhead. Deployment to a cloud service would improve accessibility but is outside the project scope.

### Security and Privacy Considerations
This project does not handle sensitive information. Uploaded CSVs remain in memory and are never written to disk. No user accounts, authentication, or data storage mechanisms are used.

Environment variables are defined in `.env.example` to ensure that no secrets are committed to the repository, fulfilling best practices for configuration management—even if this project does not require sensitive keys.

### Operational Considerations (Ops)
- Minimal logs are produced to avoid cluttering the console.
- The `/health` endpoint provides a simple readiness probe.
- The application is intended for single-user local usage and is not optimized for scaling.
- The visualization engine expects moderately sized CSVs (under a few MB). Extremely large datasets may impact performance or memory.
- The Docker container uses a lightweight Python base image to reduce build size and improve portability.

## 5) Results & Evaluation

This project successfully demonstrates a fully containerized, browser-based CSV visualization workflow. The application performs reliably across all 4 visualization types, handles user-uploaded CSVs, and produces consistent, clean visual output.

### Functionality Verification
The following core functionalities were tested and verified:

- **CSV Uploading:** Users can upload any properly formatted CSV file through the `/home` interface.
  
- **Data Cleaning:** The app automatically trims column names, converts numeric columns, filters invalid or missing values, and normalizes categorical data to ensure all visualizations render correctly without errors.

- **Column Detection:** The app correctly identifies available columns and presents them in dropdown menus.

- **Visualization Generation:** All four visualization types work consistently:
  - Histograms (numeric variables)
  - Scatterplots (two numeric variables)
  - Bar charts (categorical variable counts)
  - Pie charts (categorical distribution)

- **Base64 Image Rendering:** All charts render correctly in-browser via base64-encoded PNG images embedded in HTML templates.

- **Error Handling:** Invalid inputs (empty uploads, missing variable selection, incorrect column types) produce clear on-page error messages.

### Example Outputs

#### Histogram
<img src="assets/visualizations/histogram.png" width="300">

#### Bar Chart
<img src="assets/visualizations/barchart.png" width="300">

#### Pie Chart
<img src="assets/visualizations/piechart.png" width="300">

#### Scatterplot
<img src="assets/visualizations/scatterplot.png" width="300">

Each example confirms consistent styling, correct scaling, proper axis labeling, and accurate representation of the underlying data.

### Health Check Evaluation
A dedicated `/health` endpoint is included for validation and reproducibility. When the container is running:

curl http://localhost:8080/health returns:{"status":"ok"}

This confirms that:
- The Flask server is active
- Routes are loaded
- The environment is configured correctly

This health check satisfies the rubric requirement for operational readiness and container self-verification.

### Performance Notes
- All supported datasets (and typical CSVs under a few MB) load instantly.
- Matplotlib renders images quickly due to lightweight figure generation and simplified styling.
- Docker container runs efficiently using the Python slim base image.

### Validation Summary
Overall, the application functions exactly as intended:
- Reliable CSV ingestion
- Accurate visualizations
- Clean rendering
- Successful containerization
- Consistent behavior across machines

The app meets and exceeds all core grading criteria for functionality, containerization, and reproducibility.

## 6) What’s Next

Several improvements are planned to make the application more robust, flexible, and user-friendly:

- **More Comprehensive Data Cleaning:**  
  Expand the current cleaning pipeline to handle a wider range of real-world CSV irregularities, including mixed data types, inconsistent delimiters, unexpected encodings, nested headers, and non-tabular rows. The goal is to make the app resilient enough to process virtually any CSV file without manual preprocessing.

- **Smarter Visualization Labeling:**  
  Improve figure titles, axis labels, and category names by automatically formatting labels, detecting units, and generating more descriptive chart text. This will produce cleaner, more readable visualizations and reduce the need for users to rename columns in their datasets.

- **Advanced Visualization Options:**  
  Add optional controls such as custom color schemes, adjustable bin sizes, axis scaling, and summary statistics overlays.

- **Enhanced User Feedback:**  
  Provide more detailed warnings or suggestions when the uploaded CSV contains problematic data, helping users understand how their dataset is being cleaned or transformed.

These enhancements would make the application even more general-purpose and able to handle a broader variety of CSV formats and visualization needs.

## 7) Links

Github repository:



