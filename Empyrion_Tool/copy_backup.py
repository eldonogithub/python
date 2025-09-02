import os
import shutil
import argparse
import sqlite3
import logging
from empyrion_common import get_backup_path, get_entity_type, etype_to_abbr

# Logging setup
def setup_logging(verbose):
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format='%(asctime)s.%(msecs)03d %(levelname)s %(filename)s:%(lineno)d: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def copy_backup(args, saves_root):
    src_path = get_backup_path(saves_root, args.src_game, args.src_id)
    dest_path = get_backup_path(saves_root, args.dest_game, args.dest_id)
    logging.debug(f"Source path: {src_path}")
    logging.debug(f"Destination path: {dest_path}")
    # Check entity types in their respective databases
    src_type = get_entity_type(saves_root, args.src_game, args.src_id)
    dest_type = get_entity_type(saves_root, args.dest_game, args.dest_id)
    logging.debug(f"Source entity type: {src_type}")
    logging.debug(f"Destination entity type: {dest_type}")
    if src_type is None:
        logging.error(f"Source entity ID {args.src_id} not found in {args.src_game} database.")
        print(f"Source entity ID {args.src_id} not found in {args.src_game} database.")
        return False
    if dest_type is None:
        logging.error(f"Destination entity ID {args.dest_id} not found in {args.dest_game} database.")
        print(f"Destination entity ID {args.dest_id} not found in {args.dest_game} database.")
        return False
    if src_type != dest_type:
        logging.error(f"Entity type mismatch. Source ID {args.src_id} type: {etype_to_abbr(src_type)}, Destination ID {args.dest_id} type: {etype_to_abbr(dest_type)}")
        print(f"Error: Entity type mismatch. Source ID {args.src_id} type: {etype_to_abbr(src_type)}, Destination ID {args.dest_id} type: {etype_to_abbr(dest_type)}")
        return False
    if not os.path.isfile(src_path):
        logging.error(f"Source backup.ebp not found: {src_path}")
        print(f"Source backup.ebp not found: {src_path}")
        return False
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    shutil.copy2(src_path, dest_path)
    logging.info(f"Copied {src_path} to {dest_path} (type: {etype_to_abbr(src_type)})")
    print(f"Copied {src_path} to {dest_path} (type: {etype_to_abbr(src_type)})")
    return True

def main():
    parser = argparse.ArgumentParser(description="Copy Empyrion backup.ebp between games/entities.")
    parser.add_argument('--src-game', required=True, help='Source game name')
    parser.add_argument('--src-id', required=True, help='Source entity ID')
    parser.add_argument('--dest-game', required=True, help='Destination game name')
    parser.add_argument('--dest-id', required=True, help='Destination entity ID')
    parser.add_argument('--saves', default=r"C:\SteamLibrary\steamapps\common\Empyrion - Galactic Survival\Saves\Games", help='Path to saves folder (default: C:\\SteamLibrary\\steamapps\\common\\Empyrion - Galactic Survival\\Saves\\Games)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()

    setup_logging(args.verbose)
    logging.debug(f"Arguments: {args}")
    copy_backup(args, args.saves)

if __name__ == "__main__":
    main()
