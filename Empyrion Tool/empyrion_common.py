def etype_abbr_to_id(abbr):
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
import os
import sqlite3

def get_backup_path(saves_root, game, entity_id):
    """Return the path to backup.epb for a given game and entity."""
    return os.path.join(saves_root, game, 'Shared', entity_id, 'backup.epb')

etype_map = {
    1: "PLAYER",
    2: "BA",
    3: "CV",
    4: "SV",
    5: "HV",
    6: "DRONE",
    7: "AST",
    8: "UNKNOWN"
}

def etype_to_abbr(etype):
    return etype_map.get(etype, str(etype))

def get_entity_type(saves_root, game, entity_id):
    """Return the etype for the given entityid from the global.db in the specified game."""
    db_path = os.path.join(saves_root, game, 'global.db')
    if not os.path.isfile(db_path):
        return None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT etype FROM Entities WHERE entityid = ?", (entity_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception:
        return None
