import os, fnmatch, sys

os.environ["DATABRICKS_API_HOST"] = sys.argv[1]
os.environ["DBUTILSTOKEN"] = sys.argv[2]

from spores.Dbfs import find_file, dbfs_upload
from spores.Clusters import clusters_create
from uuid import uuid4
from pprint import pprint

build_dir = sys.argv[3]
deploy_dir = sys.argv[4]
filename = sys.argv[5]

# deploy wheel
wheel_dir = f"{deploy_dir}/dist"
wheels = find_file('*.whl', wheel_dir)

for whl in wheels:

    whl_filename = os.path.basename(whl)

    print(f"{whl} => {deploy_dir}/{whl_filename}")
    dbfs_upload(whl, f"{deploy_dir}/{whl_filename}", True)

# deploy clusters
cluster_dir = f"{build_dir}/databricks/dist/clusters"
init_scripts_dir = f"{build_dir}/databricks/dist/init_scripts"

clusters_create(cluster_dir, delete_if_exists=True, init_script_path=init_scripts_dir)

