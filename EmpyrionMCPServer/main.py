from fastapi import FastAPI
app = FastAPI()
from fastapi import FastAPI
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Empyrion_Tool')))
import Empyrion_Tool.search_empyrion_entities as search_empyrion_entities
import Empyrion_Tool.read_blueprint as read_blueprint
import Empyrion_Tool.update_entities as update_entities

import Empyrion_Tool.copy_backup as copy_backup

# MCP integration


app = FastAPI()


from fastapi import Query
import argparse

@app.get("/search_entities")
def search_entities_endpoint(
    id: int = Query(None),
    name: str = Query(None),
    list: bool = Query(False),
    location: str = Query(None),
    saves: str = Query(r"C:\SteamLibrary\steamapps\common\Empyrion - Galactic Survival\Saves\Games"),
    games: str = Query(None),
    game: str = Query(None),
    prefabs: str = Query(r"C:\SteamLibrary\steamapps\common\Empyrion - Galactic Survival\Content\Prefabs"),
    verbose: bool = Query(False),
    man: bool = Query(False),
    type: str = Query(None),
    owner: str = Query(None),
    removed: bool = Query(False)
):
    # Build argparse.Namespace for compatibility
    args = argparse.Namespace(
        id=id,
        name=name,
        list=list,
        location=location,
        saves=saves,
        games=games,
        game=game,
        prefabs=prefabs,
        verbose=verbose,
        man=man,
        type=type,
        owner=owner,
        removed=removed
    )
    # Call the search_entities function from search_empyrion_entities.py
    result = search_empyrion_entities.search_entities(args)
    return {"result": result}

@app.get("/read_blueprint")
def read_blueprint_endpoint(bp_path: str, verbose: bool = False):
    # Call the read_blueprint function from read_blueprint.py
    result = read_blueprint.read_blueprint(bp_path, verbose)
    return {"result": result}

@app.post("/update_entities")
def update_entities_endpoint(database: dict):
    # Call the update_entities function from update_entities.py
    result = update_entities.update_entities(database)
    return {"result": result}

# Add more endpoints as needed for other tools

# Endpoint for copy_backup
from fastapi import Body
@app.post("/copy_backup")
def copy_backup_endpoint(
    src_game: str = Body(...),
    src_id: str = Body(...),
    dest_game: str = Body(...),
    dest_id: str = Body(...),
    saves: str = Body(r"C:\SteamLibrary\steamapps\common\Empyrion - Galactic Survival\Saves\Games"),
    verbose: bool = Body(False)
):
    import argparse
    args = argparse.Namespace(
        src_game=src_game,
        src_id=src_id,
        dest_game=dest_game,
        dest_id=dest_id,
        saves=saves,
        verbose=verbose
    )
    # Setup logging for verbose
    copy_backup.setup_logging(verbose)
    result = copy_backup.copy_backup(args, saves)
    return {"success": result}

# Endpoint for search_empyrion_entities (raw output)
@app.post("/search_entities_raw")
def search_entities_raw_endpoint(
    id: int = Body(None),
    name: str = Body(None),
    list: bool = Body(False),
    location: str = Body(None),
    saves: str = Body(r"C:\SteamLibrary\steamapps\common\Empyrion - Galactic Survival\Saves\Games"),
    games: str = Body(None),
    game: str = Body(None),
    prefabs: str = Body(r"C:\SteamLibrary\steamapps\common\Empyrion - Galactic Survival\Content\Prefabs"),
    verbose: bool = Body(False),
    man: bool = Body(False),
    type: str = Body(None),
    owner: str = Body(None),
    removed: bool = Body(False)
):
    import argparse
    args = argparse.Namespace(
        id=id,
        name=name,
        list=list,
        location=location,
        saves=saves,
        games=games,
        game=game,
        prefabs=prefabs,
        verbose=verbose,
        man=man,
        type=type,
        owner=owner,
        removed=removed
    )
    # Setup logging for verbose
    search_empyrion_entities.setup_logging(verbose)
    # Instead of printing, collect results
    import io, sys
    old_stdout = sys.stdout
    sys.stdout = mystdout = io.StringIO()
    search_empyrion_entities.search_entities(args)
    sys.stdout = old_stdout
    output = mystdout.getvalue()
    return {"output": output}
