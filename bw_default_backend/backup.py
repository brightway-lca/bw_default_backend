from . import config
from .filesystem import safe_filename
import codecs
import datetime
import json
import tarfile
from pathlib import Path


def backup_project():
    """Backup project data directory to a ``.tar.gz`` (compressed tar archive).

    ``project`` is the name of a project.

    Backup archive is saved to the user's home directory.

    Restoration is done using ``restore_project_directory``.

    Returns the filepath of the backup archive."""
    assert config.project is not None, "Must activate a project first"

    fp = Path.home() / "brightway-project-{}-backup.{}.tar.gz".format(
        safe_filename(project.name, add_hash=False),
        datetime.datetime.now().strftime("%d-%B-%Y-%I-%M%p"),
    )
    with open(config.project.directory / ".project-name.json", "w") as f:
        json.dump({"name": project.name}, f)
    print("Creating project backup archive - this could take a few minutes...")
    with tarfile.open(fp, "w:gz") as tar:
        tar.add(config.project.directory, arcname=safe_filename(config.project.name))


# def restore_project_directory(fp):
#     """Restore backup created using ``backup_project_directory``.

#     Raises an error is the project already exists.

#     ``fp`` is the filepath of the backup archive.

#     Returns the name of the newly created project."""
#     def get_project_name(fp):
#         reader = codecs.getreader("utf-8")
#         with tarfile.open(fp, 'r|gz') as tar:
#             for member in tar:
#                 if member.name[-17:] == "project-name.json":
#                     return json.load(reader(tar.extractfile(member)))['name']
#             raise ValueError("Couldn't find project name file in archive")

#     assert os.path.isfile(fp), "Can't find file at path: {}".format(fp)
#     print("Restoring project backup archive - this could take a few minutes...")
#     project_name = get_project_name(fp)

#     with tarfile.open(fp, 'r|gz') as tar:
#         tar.extractall(projects._base_data_dir)

#     _current = projects.current
#     projects.set_current(project_name, update=False)
#     projects.set_current(_current)
#     return project_name
