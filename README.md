This solver finds a very good solution, very close to the optimal one (as determined by Google’s OR-Tools, an open-source optimization library), but does so faster.


# Installation

First install the `uv` command-line tool by running the following command in your terminal:
```bash
# On macOS and Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows (using PowerShell):
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# With pip:
pip install uv
```

To open the project, run the following commands in your terminal:
```bash
# Install git in case you don't have it.
# On AWS Linux 
sudo yum install git
# On Ubuntu
sudo apt-get install git
# On Windows
# Download and install git from https://git-scm.com/download/win

# Make sure to replace <access-token> with your personal access token adn <bucket-name> with the name of the bucket.
git clone <repository-name>
cd <repository-name>

# Install the dependencies and run a file
uv run jss_v0.6.1.py

# Run a file with PyPy (for performance).
uv run --python pypy@3.10 jss_v0.6.1.py
```