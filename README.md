# Introduction 
Python framework for databricks. A library that handles the following either clusterside of locally (using Databricks-Connect):
- Configuration
- Logging
- Azure Storage Session Connection

Examples:

Mount azure storage using a session connection and Azure AD service principal backed by scoped secrets and cluster configuration:

```
from fathom.ConnectStorage import ConnectStorage
ConnectStorage()
```

```
Connected:
-----------------------------------------------
 environment = DEV
 storage account = abfss://datalake@datalakegeneva.dfs.core.windows.net/ 
```

# Setup

Create virual environment and install dependencies for local development:

```
python3.7 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Comes configured with databricks-connect==7.1.10, see requirements.txt. To use a different version review breaking changes before hand! & delete these lines in requirements.txt.
```
databricks-connect==7.1.10
py4j==0.10.9
six==1.15.0
```

Install your required version:
```
pip install -U databricks-connect==?
pip freeze > requirements.txt
```


# Build

Build python wheel for Databricks cluster:
```
python setup.py sdist bdist_wheel
```

# Test


# Contribute

