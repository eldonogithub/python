# Add check for  git+https://github.com/geostar1024/epbtools.git


from epbtools.readepb import Blueprint

# Load your blueprint file
bp = Blueprint("MyBlueprint.epb")

print("Header information:")
print(bp.header)

print(f"\nTotal blocks: {bp.num_blocks}")

print("\nBlocks (type_id → position):")
for block in bp.block_data.entities:
    print(f"- ID {block.type_id} at ({block.x}, {block.y}, {block.z})")
