import streamlit as st
import os
import subprocess
import time
import shutil

# --- Configuration ---
# --- Configuration ---
# Use absolute paths based on the script location to ensure it works
# regardless of where the command is run from.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORK_DIR_BASE = os.path.join(BASE_DIR, "client_workspaces")
MODULES_DIR_ABS = os.path.join(BASE_DIR, "modules")

st.set_page_config(page_title="Antigravity IDE", page_icon="🚀", layout="wide")

# --- Custom CSS for "Premium" Feel ---
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #c9d1d9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
    }
    .console-output {
        font-family: 'Courier New', monospace;
        background-color: #161b22;
        color: #58a6ff;
        padding: 15px;
        border-radius: 8px;
        height: 300px;
        overflow-y: scroll;
        border: 1px solid #30363d;
        white-space: pre-wrap;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if 'logs' not in st.session_state:
    st.session_state['logs'] = "Welcome to Antigravity IDE. Ready to launch.\n"

def render_logs(placeholder):
    # Escape HTML special characters if necessary, but here we just split lines
    # Using a div with scrolling
    lines = st.session_state['logs'].split('\n')
    # Keep last 1000 lines max to prevent memory bloat in browser
    if len(lines) > 1000:
        lines = lines[-1000:]
        st.session_state['logs'] = "\n".join(lines)
        
    content = "<br>".join(lines)
    placeholder.markdown(f'<div class="console-output">{content}</div>', unsafe_allow_html=True)

def run_terraform_command(command, cwd, placeholder):
    """Runs a terraform command and updates the logs."""
    log_msg = f"\n$ {command}"
    st.session_state['logs'] += f"{log_msg}\n"
    render_logs(placeholder)
    
    try:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                st.session_state['logs'] += output
                render_logs(placeholder)
                # Small sleep to yield to Streamlit rerender loop
                time.sleep(0.01) 
        
        pk = process.poll()
        if pk == 0:
            st.session_state['logs'] += "✅ Command completed successfully.\n"
        else:
            st.session_state['logs'] += f"❌ Command failed with exit code {pk}.\n"
        render_logs(placeholder)
            
    except Exception as e:
        st.session_state['logs'] += f"❌ Error: {str(e)}\n"
        render_logs(placeholder)

# --- Sidebar: Project & Modules ---
with st.sidebar:
    st.image("https://img.icons8.com/autodesk/100/aaaaaa/gravity.png", width=60) # Placeholder icon
    st.title("Antigravity IDE")
    st.markdown("---")
    
    st.subheader("Project Management")
    client_id = st.text_input("Client ID (Workspace)", value="client_alpha")
    
    st.subheader("Module Config")
    use_snowflake = st.checkbox("❄️ Snowflake Data Platform")
    use_dbt = st.checkbox("🟧 dbt Cloud Project")
    use_mwaa = st.checkbox("🍃 AWS MWAA (Airflow)")
    use_s3 = st.checkbox("🪣 AWS S3 Buckets", value=True)
    use_github = st.checkbox("🐙 GitHub Repository")

# --- Layout Containers ---
# We define containers first to control the layout order, 
# then populate them in an order that ensures variables (like log_placeholder) 
# are defined before they are used in callbacks/buttons.

top_container = st.container()
logs_container = st.container()

# --- Console Output Section (Define First, Render Bottom) ---
with logs_container:
    st.markdown("---")
    st.subheader("Console Output")
    log_placeholder = st.empty()
    render_logs(log_placeholder)

# --- Main Interface & Action Panel (Define Second, Render Top) ---
with top_container:
    st.title("Infrastructure Orchestrator")
    st.markdown(f"**Current Workspace:** `{client_id}`")

    col1, col2 = st.columns([1, 1])

    # --- Input Form ---
    with col1:
        st.subheader("Configuration Variables")
        with st.expander("Global Settings", expanded=True):
            aws_region = st.selectbox("AWS Region", ["us-east-1", "us-west-2", "eu-west-1"])
            env_tag = st.selectbox("Environment", ["dev", "staging", "prod"])

        variables = {}
        
        if use_s3:
            with st.expander("S3 Configuration", expanded=True):
                s3_bucket_prefix = st.text_input("Bucket Name Prefix", value=f"{client_id}-data-lake")
                variables['s3_bucket_name'] = f"{s3_bucket_prefix}-{env_tag}"

        if use_snowflake:
            with st.expander("Snowflake Configuration", expanded=True):
                variables['snowflake_account'] = st.text_input("Snowflake Account Name", placeholder="xy12345")

        if use_dbt:
            with st.expander("dbt Configuration", expanded=True):
                variables['dbt_project_name'] = st.text_input("dbt Project Name", value=f"{client_id}_analytics")

    # --- Action Panel ---
    with col2:
        st.subheader("Actions")
        
        client_dir = os.path.join(WORK_DIR_BASE, client_id)
        
        if st.button("Generate Terraform Config", type="primary"):
            if not os.path.exists(client_dir):
                os.makedirs(client_dir)
                st.session_state['logs'] += f"Created workspace directory: {client_dir}\n"
            else:
                st.session_state['logs'] += f"Using existing workspace: {client_dir}\n"
            render_logs(log_placeholder)

            # GENERATE main.tf
            # We use absolute paths for the module source to avoid relative path confusion
            tf_config = f"""# Auto-generated by Antigravity IDE
provider "aws" {{
  region = "{aws_region}"
}}

locals {{
  environment = "{env_tag}"
}}
"""
            if use_s3:
                tf_config += f"""
module "s3_datalake" {{
  source      = "{MODULES_DIR_ABS}/s3"
  bucket_name = var.s3_bucket_name
  environment = local.environment
}}
"""
            if use_snowflake:
                tf_config += f"""
module "snowflake" {{
  source       = "{MODULES_DIR_ABS}/snowflake"
  account_name = var.snowflake_account
}}
"""
            if use_dbt:
                tf_config += f"""
module "dbt" {{
  source       = "{MODULES_DIR_ABS}/dbt_cloud"
  project_name = var.dbt_project_name
}}
"""
            if use_mwaa:
                 tf_config += f"""
module "mwaa" {{
  source = "{MODULES_DIR_ABS}/mwaa"
}}
"""
            if use_github:
                 tf_config += f"""
module "github" {{
  source = "{MODULES_DIR_ABS}/github"
}}
"""
            
            with open(os.path.join(client_dir, "main.tf"), "w") as f:
                f.write(tf_config)
            st.session_state['logs'] += "📄 Generated main.tf\n"

            # GENERATE variables.tf
            vars_tf = ""
            if use_s3: vars_tf += 'variable "s3_bucket_name" { type = string }\n'
            if use_snowflake: vars_tf += 'variable "snowflake_account" { type = string }\n'
            if use_dbt: vars_tf += 'variable "dbt_project_name" { type = string }\n'
            
            with open(os.path.join(client_dir, "variables.tf"), "w") as f:
                f.write(vars_tf)
            st.session_state['logs'] += "📄 Generated variables.tf\n"

            # GENERATE terraform.tfvars
            tfvars = ""
            for k, v in variables.items():
                tfvars += f'{k} = "{v}"\n'
            
            with open(os.path.join(client_dir, "terraform.tfvars"), "w") as f:
                f.write(tfvars)
            st.session_state['logs'] += "📄 Generated terraform.tfvars\n"
            st.session_state['logs'] += "✅ Configuration generation complete.\n"
            render_logs(log_placeholder)

        st.markdown("---")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("Terraform Init"):
                run_terraform_command("terraform init", client_dir, log_placeholder)
        with c2:
            if st.button("Terraform Plan"):
                run_terraform_command("terraform plan", client_dir, log_placeholder)
        with c3:
            if st.button("Terraform Apply", type="primary"):
                run_terraform_command("terraform apply -auto-approve", client_dir, log_placeholder)
