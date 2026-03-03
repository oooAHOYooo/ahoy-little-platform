import re

file_path = "/Users/agworkywork/ahoy-little-platform/alembic/versions/62cf584f9527_add_is_hidden_to_content_models.py"

with open(file_path, "r") as f:
    text = f.read()

# Only keep the op.add_column lines for is_hidden and remove all alter_column for existing tables
import ast

def extract_add_columns(source):
    lines = source.split('\n')
    keepers = []
    
    # Simple regex approach to extract only the add_column lines we care about
    for line in lines:
        if 'add_column' in line and 'is_hidden' in line:
            keepers.append("    " + line.strip())
            
    return keepers

keepers = extract_add_columns(text)

new_upgrade = """def upgrade():
""" + "\n".join(keepers) + """
"""

new_downgrade = """def downgrade():
""" + "\n".join([line.replace('add_column', 'drop_column').replace(", sa.Column('is_hidden', sa.Boolean(), nullable=False)", ", 'is_hidden'") for line in keepers]) + """
"""

# Replace the body of upgrade and downgrade
import re
new_text = re.sub(r'def upgrade\(\):.*def downgrade\(\):', new_upgrade + '\n\ndef downgrade():', text, flags=re.DOTALL)
new_text = re.sub(r'def downgrade\(\):.*', new_downgrade, new_text, flags=re.DOTALL)

with open(file_path, "w") as f:
    f.write(new_text)

print("Migration simplified!")
