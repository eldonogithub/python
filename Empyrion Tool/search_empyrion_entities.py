import sqlite3
import os
import glob
import argparse
import re
import sys
import logging

# Setup logging
def setup_logging(verbose):
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format='%(asctime)s.%(msecs)03d %(levelname)s %(filename)s:%(lineno)d: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

class CustomParser(argparse.ArgumentParser):
    def format_usage(self):
        return super().format_usage().replace('usage:', 'Usage:', 1)
    def format_help(self):
        return super().format_help().replace('usage:', 'Usage:', 1)

parser = CustomParser(
    usage="%(prog)s [OPTION]...",
    description=(
        "Search Empyrion save databases for entities, structures, and blueprints.\n"
        "Optionally filter by playfield (planet/sector) or game name.\n"
        "Use --help for the full manual."
    ),
    formatter_class=argparse.RawDescriptionHelpFormatter,
    add_help=True
)
parser.add_argument("--id", type=int, help="Entity ID to search for")
parser.add_argument("--name", type=str, help="Partial entity NAME to search for (case-insensitive)")
parser.add_argument("--list", action="store_true", help="List all structures")
parser.add_argument("--location", type=str, help="Filter results to a specific playfield (planet/sector) NAME")
parser.add_argument("--saves", type=str, default=r"C:\SteamLibrary\steamapps\common\Empyrion - Galactic Survival\Saves\Games", help="Root SAVES directory")
parser.add_argument("--games", type=str, help="Search only saves for games containing this name (substring match)")
parser.add_argument("--game", type=str, help="Search only saves for the game with this exact name (subdirectory of saves directory)")
parser.add_argument("--prefabs", type=str, default=r"C:\SteamLibrary\steamapps\common\Empyrion - Galactic Survival\Content\Prefabs", help="Directory containing blueprint .epb files")
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
parser.add_argument("--man", action="store_true", help="Show full manual page and exit")
parser.add_argument("--type", type=str, help="Filter by structure type: BA, CV, SV, HV, AST")
parser.add_argument("--owner", type=str, help="Find all structures owned by the given entity NAME (resolved to entityid per database)")

prog_name = os.path.basename(sys.argv[0])

def print_usage_error(message):
    print(f"{prog_name}: {message}")
    print()
    parser.print_usage()
    print(f"Try '{prog_name} --help' for more information.")
    sys.exit(1)

def is_main_save_dir(dirname):
    """
    Returns True if the directory name does NOT match the Empyrion date/time suffix pattern.
    """
    # Empyrion save backup pattern: NAMEOFGAME-YYMMDD-HHMM (optionally with more suffixes)
    # We want to EXCLUDE directories that end with -YYMMDD-HHMM (with optional extra suffixes)
    # Example: MyWorld-240801-1530, MyWorld-240801-1530-extra
    return not re.search(r'-\d{6}-\d{4}($|[-_])', dirname)

# ANSI color codes for output
txtblk = "\033[0;30m"  # Black
txtred = "\033[0;31m"  # Red
txtgrn = "\033[1;32m"  # Bold Green
txtblu = "\033[0;34m"  # Blue
txtylw = "\033[0;33m"  # Yellow
txtpur = "\033[0;35m"  # Purple
txtcyn = "\033[0;36m"  # Cyan
txtwht = "\033[0;37m"  # White
txtrst = "\033[0m"     # Text Reset

def get_bpname(cursor, entityid):
    """
    Fetch the blueprint name from the Structures table for a given entityid.
    Returns the bpname or an empty string if not found.
    """
    try:
        cursor.execute("SELECT bpname FROM Structures WHERE entityid = ?", (entityid,))
        row = cursor.fetchone()
        return row[0] if row and row[0] else ""
    except sqlite3.Error:
        return ""

def etype_to_str(etype):
    """
    Translate etype integer to a human-readable string and game abbreviation.
    """
    mapping = {
        1: ("Player", "PLAYER"),
        2: ("Base", "BA"),
        3: ("Capital Vessel", "CV"),
        4: ("Small Vessel", "SV"),
        5: ("Hover Vessel", "HV"),      # Updated: Hover Vehicle -> Hover Vessel
        6: ("Drone", "DRONE"),          # Added: Drone type if present
        7: ("Asteroid", "AST"),
        8: ("Unknown", "UNKNOWN")       # Added: fallback for unknown types
    }
    return mapping.get(etype, (str(etype), str(etype)))

def etype_abbr_to_id(abbr):
    """
    Translate game abbreviation to etype integer.
    """
    abbr_map = {
        "PLAYER": 1,
        "BA": 2,
        "CV": 3,
        "SV": 4,
        "HV": 5,
        "DRONE": 6,
        "AST": 7,
        "UNKNOWN": 8
    }
    return abbr_map.get(abbr.upper())

def get_owner_id(cursor, owner_name):
    """
    Query the Entities table for the given owner name and return the entityid.
    Returns None if not found.
    """
    cursor.execute("SELECT entityid FROM Entities WHERE name = ?", (owner_name,))
    row = cursor.fetchone()
    return row[0] if row else None

def search_entities(args):
    """
    Search for entities by entityid or partial name in all Empyrion save game databases within the given directory.
    Uses argparse.Namespace args for all options.
    """
    entity_id = args.id
    name_part = args.name
    saves_directory = args.saves
    verbose = args.verbose
    games = args.games
    game_exact = args.game
    owner_name = args.owner

    setup_logging(verbose)

    logging.debug(f"Owner name: {owner_name}")
    logging.debug(f"Arguments: {args}")

    if entity_id is None and not name_part and not args.list:
        print_usage_error("You must specify either --id, --name, or --list.")
    if not saves_directory:
        logging.debug("Invalid saves directory.")
        return

    logging.debug(f"Searching for entity id {entity_id}, name containing '{name_part}', list_all={args.list}, location={args.location} in directory: {saves_directory}")
    if not os.path.exists(saves_directory):
        logging.debug(f"Directory does not exist: {saves_directory}")
        return
    if not os.path.isdir(saves_directory):
        logging.debug(f"Not a directory: {saves_directory}")
        return

    # List all subdirectories in saves_directory and filter to only main saves
    if game_exact:
        main_save_dirs = [
            os.path.join(saves_directory, d)
            for d in os.listdir(saves_directory)
            if os.path.isdir(os.path.join(saves_directory, d)) and is_main_save_dir(d)
            and d == game_exact
        ]
    elif games:
        main_save_dirs = [
            os.path.join(saves_directory, d)
            for d in os.listdir(saves_directory)
            if os.path.isdir(os.path.join(saves_directory, d)) and is_main_save_dir(d)
            and games.lower() in d.lower()
        ]
    else:
        main_save_dirs = [
            os.path.join(saves_directory, d)
            for d in os.listdir(saves_directory)
            if os.path.isdir(os.path.join(saves_directory, d)) and is_main_save_dir(d)
        ]
    logging.debug(f"Main save directories: {[os.path.basename(d) for d in main_save_dirs]}")

    # Collect all global.db files from main save directories only
    db_files = []
    for save_dir in main_save_dirs:
        db_path = os.path.join(save_dir, "global.db")
        if os.path.isfile(db_path):
            db_files.append(db_path)
            logging.debug(f"Found database: {os.path.relpath(db_path, saves_directory)}")

    db_count = 0
    match_found = False

    blueprint_displayed = False

    all_results = []

    for db_file in db_files:
        rel_db_file = os.path.relpath(db_file, saves_directory)
        logging.debug(f"Searching in database: {rel_db_file}")
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            where_clauses = []
            params = []

            owner_id = None
            if owner_name is not None:
                logging.debug(f"Looking up owner ID for: {owner_name}")
                owner_id = get_owner_id(cursor, owner_name)
                if owner_id is None:
                    logging.debug(f"Owner '{owner_name}' not found in {rel_db_file}.")
                    conn.close()
                    continue
                where_clauses.append("e.facid = ?")
                params.append(owner_id)

            if entity_id is not None:
                where_clauses.append("e.entityid = ?")
                params.append(entity_id)
            elif name_part:
                where_clauses.append("e.name LIKE ?")
                params.append(f"%{name_part}%")
            if args.location:
                where_clauses.append("p.name = ?")
                params.append(args.location)
            if args.type:
                etype_id = etype_abbr_to_id(args.type)
                if etype_id is not None:
                    where_clauses.append("e.etype = ?")
                    params.append(etype_id)
                else:
                    print(f"{prog_name}: unknown type abbreviation '{args.type}'. Valid: BA, CV, SV, HV, AST")
                    print()
                    parser.print_usage()
                    print(f"Try '{prog_name} --help' for more information.")
                    sys.exit(1)

            # Always filter out removed entities
            where_clauses.append("e.isremoved = 0")
            where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"

            try:
                query = f"""
                    SELECT e.entityid, e.name, e.etype, p.name as playfield, s.name as starsystem, e.facid, e.facgroup, (SELECT bpname FROM Structures WHERE entityid = e.entityid)
                    FROM Entities e
                    LEFT JOIN Playfields p ON e.pfid = p.pfid
                    LEFT JOIN SolarSystems s ON p.ssid = s.ssid
                    WHERE {where_clause}
                """
                cursor.execute(query, params)
                rows = cursor.fetchall()
            except sqlite3.OperationalError:
                try:
                    query = f"SELECT entityid, name, etype, playfield, '' as starsystem, facid, facgroup, (SELECT bpname FROM Structures WHERE entityid = entityid) FROM Entities WHERE {where_clause}"
                    cursor.execute(query, params)
                    rows = cursor.fetchall()
                except sqlite3.OperationalError:
                    query = f"SELECT entityid, name, etype, '' as playfield, '' as starsystem, facid, facgroup, (SELECT bpname FROM Structures WHERE entityid = entityid) FROM Entities WHERE {where_clause}"
                    cursor.execute(query, params)
                    rows = cursor.fetchall()

            owner_names = {}
            for row in rows:
                entityid, name, etype, playfield, starsystem, facid, facgroup, bpname = row
                structure_owner_name = ""
                if facid:
                    if facid in owner_names:
                        structure_owner_name = owner_names[facid]
                    else:
                        cursor.execute("SELECT name FROM Entities WHERE entityid = ?", (facid,))
                        owner_row = cursor.fetchone()
                        structure_owner_name = owner_row[0] if owner_row and owner_row[0] else ""
                        owner_names[facid] = structure_owner_name
                all_results.append((
                    rel_db_file, bpname or "", starsystem or "", playfield or "",
                    str(entityid), structure_owner_name, etype_to_str(etype)[1], name or ""
                ))
            conn.close()
        except sqlite3.Error as e:
            logging.debug(f"Error accessing {rel_db_file}: {e}")

    # Sort results by db, bp, solarsystem, playfield, id
    # Group output by db, and sort by id ascending within each db
    from collections import defaultdict
    grouped_results = defaultdict(list)
    for r in all_results:
        grouped_results[r[0]].append(r)
    for db in grouped_results:
        grouped_results[db].sort(key=lambda r: int(r[4]) if r[4].isdigit() else r[4])

    # Calculate max widths for columns
    max_db_len = max([len("db")] + [len(r[0]) for r in all_results]) if all_results else len("db")
    max_sys_len = max([len("starsystem")] + [len(r[2]) for r in all_results]) if all_results else len("starsystem")
    max_loc_len = max([len("playfield")] + [len(r[3]) for r in all_results]) if all_results else len("playfield")
    max_bp_len = max([len("bp")] + [len(r[1]) for r in all_results]) if all_results else len("bp")
    max_id_len = max([len("id")] + [len(r[4]) for r in all_results]) if all_results else len("id")
    max_owner_len = max([len("owner")] + [len(r[5]) for r in all_results]) if all_results else len("owner")
    max_type_len = max([len("type")] + [len(r[6]) for r in all_results]) if all_results else len("type")
    max_name_len = max([len("name")] + [len(r[7]) for r in all_results]) if all_results else len("name")

    # Print header once
    header = (
        f"{'db':<{max_db_len}}  "
        f"{'starsystem':<{max_sys_len}}  "
        f"{'playfield':<{max_loc_len}}  "
        f"{'bp':<{max_bp_len}}  "
        f"{'id':<{max_id_len}}  "
        f"{'owner':<{max_owner_len}}  "
        f"{'type':<{max_type_len}}  "
        f"{'name':<{max_name_len}}"
    )
    print(header)
    print('-' * len(header))

    # Print all results grouped by db
    for db in sorted(grouped_results.keys()):
        for r in grouped_results[db]:
            print(
                f"{txtgrn}{r[0]:<{max_db_len}}{txtrst}  "
                f"{txtgrn}{r[2]:<{max_sys_len}}{txtrst}  "
                f"{txtgrn}{r[3]:<{max_loc_len}}{txtrst}  "
                f"{txtgrn}{r[1]:<{max_bp_len}}{txtrst}  "
                f"{txtgrn}{r[4]:<{max_id_len}}{txtrst}  "
                f"{txtgrn}{r[5]:<{max_owner_len}}{txtrst}  "
                f"{txtylw}{r[6]:<{max_type_len}}{txtrst}  "
                f"{txtgrn}{r[7]:<{max_name_len}}{txtrst}"
            )

    print(f"Total structures found: {len(all_results)}")
    logging.debug(f"Checked {len(db_files)} databases.")
    if not all_results:
        print("No matches found.")

if __name__ == "__main__":
    args = parser.parse_args()

    if args.man:
        print("""
NAME
    search_empyrion_entities.py - Search Empyrion save databases for entities and structures.

SYNOPSIS
    python search_empyrion_entities.py [OPTION]... 

DESCRIPTION
    Search Empyrion save game databases for entities by ID, partial NAME, or list all structures.
    Optionally filter by playfield (planet/sector) or game name.

OPTIONS
    --id ID
        Search for a specific entity ID.

    --name NAME
        Search for entities with a partial NAME match (case-insensitive).

    --list
        List all structures found (optionally filtered by --games, --game, or --location).

    --location LOCATION
        Filter results to a specific playfield (planet/sector) NAME.

    --saves DIR
        Root SAVES directory (default: C:\\SteamLibrary\\steamapps\\common\\Empyrion - Galactic Survival\\Saves\\Games).

    --games NAME
        Search only saves for games containing this name (substring match).

    --game NAME
        Search only saves for the game with this exact name (subdirectory of saves directory).

    --prefabs DIR
        Directory containing blueprint .epb files (default: C:\\SteamLibrary\\steamapps\\common\\Empyrion - Galactic Survival\\Content\\Prefabs).

    --verbose
        Enable verbose output.

    --man
        Show this full manual page and exit.

    --type TYPE
        Filter by structure type: BA, CV, SV, HV, AST.

    --owner OWNER_NAME
        Find all structures owned by the given entity NAME (resolved to entityid per database).

EXAMPLES
    List all structures in a specific game and location:
        python search_empyrion_entities.py --game MyWorld --location \"Balapru Moon Sector\" --list

    List all structures in games containing 'Creative':
        python search_empyrion_entities.py --games Creative --list

    Search for a specific entity ID:
        python search_empyrion_entities.py --id 123456

    Search for all entities with 'base' in the name:
        python search_empyrion_entities.py --name base

    List all structures:
        python search_empyrion_entities.py --list

    Search for structures of a specific type:
        python search_empyrion_entities.py --type CV

    Find all structures owned by a specific entity:
        python search_empyrion_entities.py --owner 78910
""")
        sys.exit(0)

    search_entities(args)