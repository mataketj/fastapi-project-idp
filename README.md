# Antigravity IDE 🚀 - Internal Developer Platform (IDP) Boilerplate

**Antigravity IDE** is a lightweight, local-first Internal Developer Platform (IDP) designed to streamline the orchestration of Terraform workflows. It provides a user-friendly Streamlit interface for Platform Engineers and Developers to define, configure, and provision data platform infrastructure without writing Terraform `main.tf` files from scratch.

This repository serves as a **boilerplate foundation** for building your own custom IDP tooling.

## 🏗️ Architecture

The application is built on a simple yet powerful stack:
-   **Frontend/Logic**: [Streamlit](https://streamlit.io/) (Python) for the UI and state management.
-   **Infrastructure Engine**: [Terraform](https://www.terraform.io/) for provisioning resources.
-   **Containerization**: Docker for ensuring a consistent runtime environment (Python + Terraform).

### Directory Structure

```plaintext
.
├── app/
│   ├── modules/                 # 🧱 pre-packaged Terraform modules (add your own here)
│   │   ├── s3/
│   │   ├── snowflake/
│   │   └── ...
│   ├── client_workspaces/       # 📂 workspace for generated configs (gitignored)
│   └── streamlit_app.py         # 🧠 Main application logic
├── Dockerfile                   # 🐳 Multi-stage build (Python + Terraform)
├── requirements.txt             # 📦 Python dependencies
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
-   **Docker Desktop** (Recommended)
-   *OR* Python 3.10+ and Terraform installed locally.

### Option A: Run with Docker (Recommended)
The Docker image encapsulates the Python environment and the Terraform binary, ensuring you have the exact versions needed.

1.  **Build the Image:**
    ```bash
    docker build -t antigravity-ide .
    ```

2.  **Run the Container:**
    We mount the generated workspaces volume so your Terraform state persists on your host machine even if the container stops.
    ```bash
    docker run -p 8501:8501 \
      -v $(pwd)/app/client_workspaces:/app/app/client_workspaces \
      antigravity-ide
    ```

3.  **Access the IDE:**
    Open your browser to `http://localhost:8501`.

### Option B: Run Locally
If you prefer running directly on your machine:

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Verify Terraform:**
    Ensure `terraform` is in your PATH.
    ```bash
    terraform -version
    ```
3.  **Launch:**
    ```bash
    streamlit run app/streamlit_app.py
    ```

---

## 📖 User Guide

1.  **Project Management**:
    -   Enter a **Client ID** (e.g., `client-alpha`). This creates a dedicated isolated workspace directory for this client's state.

2.  **Module Config**:
    -   Select the infrastructure components you need (e.g., S3, Snowflake, dbt Cloud).
    -   The UI will dynamically generate a form for the required variables based on your selection.

3.  **Provisioning Workflow**:
    -   **Generate Config**: Click to generate `main.tf`, `variables.tf`, and `terraform.tfvars` in the workspace.
    -   **Terraform Init/Plan/Apply**: Use the action buttons to execute Terraform commands. Real-time logs will appear in the console output at the bottom.

---

## 🛠️ Developer Guide (Extending the Boilerplate)

This boilerplate is designed to be easily extensible. Here is how you can customize it for your organization.

### 1. Adding a New Terraform Module
To add a new capability (e.g., an RDS database or an EKS cluster):

1.  Create a new folder in `app/modules/` (e.g., `app/modules/rds`).
2.  Add your standard Terraform files (`main.tf`, `variables.tf`, `outputs.tf`) into that folder.
3.  **Register the Module in UI (`streamlit_app.py`)**:
    -   Add a checkbox in the **Module Config** sidebar section.
    -   Add the necessary input widgets (e.g., specific instance size) in the **Input Form** section.
    -   Update the **Geneate Config** logic to append the new `module {}` block to the generated string if the checkbox is selected.

### 2. Customizing the UI
Streamlit allows for rapid UI iteration.
-   Modify `app/streamlit_app.py` to change the layout, add new pages, or include validity checks for inputs.
-   The application uses session state to maintain logs; you can expand this to store more complex state objects if needed.

### 3. Remote State Management
Currently, this boilerplate uses **local state** (`terraform.tfstate` inside `client_workspaces/`).
To move to production:
-   Update the `tf_config` generation string in `streamlit_app.py` to include a `backend "s3" {}` or `backend "remote" {}` block.
-   Inject credentials securely via environment variables passed to the Docker container (do not hardcode secrets!).

## 🤝 Contributing
1.  Fork the repository.
2.  Create a feature branch (`git checkout -b feature/amazing-module`).
3.  Commit your changes.
4.  Push to the branch and open a Pull Request.

---
*Built with ❤️ by Antigravity*
