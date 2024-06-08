"""
This script creates a sample database in the tests/test_data folder from a sql creation script in
scripts/test_database_creation_scripts.
"""

from pathlib import Path

from src.model import root_dir, database

if __name__ == "__main__":

    # Prompt user to choose a sample database to create
    print("Which sample database do you want to create?")
    scripts: list[Path] = list(
        # All files in this folder should be sample database creation scripts
        (root_dir / "scripts" / "test_database_creation_scripts").iterdir()
    )
    for script in scripts:
        print(script.name[:-4])
    create_index: int = int(input(">>> ")) - 1

    # Attempt to create sample database
    creation_script_path: Path = scripts[create_index]
    new_database_path: Path = root_dir / "tests" / "test_data" / "sample_database_1.db"

    if new_database_path.exists():
        print(f"{new_database_path.absolute()} already exists.")
        exit()
    else:
        print(f"Creating new database from {new_database_path.absolute()}.")

    # Create empty database file
    database.create_new(new_database_path)

    # Read queries
    queries: list[str]
    with open(creation_script_path, "r") as script:
        queries = script.readlines()

    queries = list([query.strip() for query in queries])

    # Execute and commit queries
    con, cur = database.get_connection()
    for query in queries:
        print(query)
        cur.execute(query)
    con.commit()
