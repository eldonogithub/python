import os
import zipfile

def read_blueprint(bp_path, verbose=False):
    """
    Reads an Empyrion blueprint file (.epb or zipped folder) and lists its contents.
    Prints the names of files inside the blueprint.
    """
    if not os.path.exists(bp_path):
        print(f"Blueprint file or folder does not exist: {bp_path}")
        return

    if os.path.isdir(bp_path):
        # Blueprint is a folder (unpacked)
        if verbose:
            print(f"Reading blueprint folder: {bp_path}")
        for root, dirs, files in os.walk(bp_path):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), bp_path)
                print(rel_path)
    elif bp_path.lower().endswith('.epb') or zipfile.is_zipfile(bp_path):
        # Blueprint is a .epb file (zip format)
        if verbose:
            print(f"Reading blueprint archive: {bp_path}")
        with zipfile.ZipFile(bp_path, 'r') as z:
            for name in z.namelist():
                print(name)
    else:
        print("Unknown blueprint format. Please provide a .epb file or blueprint folder.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Read and list contents of an Empyrion blueprint (.epb or folder).")
    parser.add_argument("blueprint", type=str, help="Path to blueprint file (.epb) or folder")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    read_blueprint(args.blueprint, args.verbose)