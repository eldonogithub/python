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
