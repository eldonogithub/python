import sqlite3
import re
import shutil
import datetime
import string

def find_unprintable_chars(s):
    # List of unprintable characters
    unprintable = [char for char in s if char not in string.printable]
    return unprintable

def update_entities(database):
    # Create a backup of the database, and add date-timestamp suffix
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_database = database.replace(".db", f"_backup_{timestamp}.db")
    shutil.copy2(database, backup_database)  # Create a backup before modifying
    print(f"Backup created: {backup_database}")
        
    try:
        # Connect to the database and auto-commit. This will allow us to see the
        # changes we make in the database, and will also allow other programs to
        # see the changes we make.
        conn = sqlite3.connect(database, isolation_level=None, autocommit=True)
        cursor = conn.cursor()
        
        # Select all rows
        select_query = "SELECT entityid, name, etype FROM Entities"
        cursor.execute(select_query)
        rows = cursor.fetchall()
        
        # Update the column conditionally using regex or other complex logic
        for entityid, name, etype in rows:
            if entityid is None or name is None or etype is None:
                continue

            # Skip non-vessel entities which are hovercraft, small vessels, and capital ships.
            if etype != 3 and etype != 4 and etype != 5:
                # Skip non-vessel entities, which are etype 3, 4 and 5 in Empyrion 
                continue

            # Check for unprintable characters
            unprintable_chars = find_unprintable_chars(name)

            if unprintable_chars:
                print("Unprintable characters found:", unprintable_chars)
                break

            # Remove any extra leading or trailing spaces before attempting the regex match
            cleaned_name = name.strip()

            # Remove older format like 'Eldon Miner Warp 3b' or '(3b)'
            cleaned_name = re.sub(r'\s*\([^)]+\)\s*$', '', cleaned_name)  # Remove text in parentheses at the end and spaces around it.
            cleaned_name = re.sub(r'\s*\d+[a-zA-Z]+$', '', cleaned_name)  # Remove trailing number with optional letter
            cleaned_name = re.sub(r' (Mk|CV|T|HV|SV) ', ' ', cleaned_name)  # Remove older version info and obvious acronyms
            cleaned_name = re.sub(r'\.', ' ', cleaned_name)  # Remove periods
            # remove single letters before numbers at end
            cleaned_name = re.sub(r'(\w)\s*(\d)$', r'\2', cleaned_name)

            match = re.search(r'(.*)\s+(\d+)$', cleaned_name)  # Extract base name and trailing number
            if match:
                base_name, existing_number = match.groups()
                if existing_number == str(entityid):
                    continue  # Skip update if the number is already correct
                new_name = f"{base_name} {entityid}".strip()
            else:
                new_name = f"{cleaned_name} {entityid}".strip()  # Append entityid if no number at the end
            
            print(f"Updating {entityid=}, {etype=}, {name=}, {new_name=}")

            update_query = "UPDATE Entities SET name = ? WHERE entityid = ?"
            cursor.execute(update_query, (new_name, entityid))
        
        print(f"Update successful. Changes saved in {database}")
        
    except sqlite3.Error as e:
        print("SQLite error:", e)
    finally:
        conn.close()

# Example usage:
database_file = r"C:\SteamLibrary\steamapps\common\Empyrion - Galactic Survival\Saves\Games\Creative\global.db"
update_entities(database_file)
