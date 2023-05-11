from pathlib import Path

json_name = 'product_register.json'

root_path = Path(__file__).parent
json_path = list(root_path.glob(json_name))
if json_path:
    json_path = json_path[0]
else:
    raise FileNotFoundError(f"Product register named \"{json_name}\" not found. Check if file exists or name is correct.")