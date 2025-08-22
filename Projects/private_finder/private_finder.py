import os
import shutil
import ast
import astor


def find_and_copy_original():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
    for entry in os.listdir(parent_dir):
        folder_path = os.path.join(parent_dir, entry)
        if os.path.isdir(folder_path):
            private_py_path = os.path.join(folder_path, "private.py")
            if os.path.isfile(private_py_path):
                dest_folder = os.path.join(current_dir, entry)
                os.makedirs(dest_folder, exist_ok=True)
                dest_file = os.path.join(dest_folder, "private.py")
                shutil.copy2(private_py_path, dest_file)


def clear_variables_in_code(code):
    class ClearAssigns(ast.NodeTransformer):
        def visit_Assign(self, node):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    node.value = ast.Constant(value=None)
            return node

    tree = ast.parse(code)
    tree = ClearAssigns().visit(tree)
    ast.fix_missing_locations(tree)
    return astor.to_source(tree)


def find_and_copy_cleared():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    for entry in os.listdir(current_dir):
        folder_path = os.path.join(current_dir, entry)
        if os.path.isdir(folder_path):
            private_py_path = os.path.join(folder_path, "private.py")
            if os.path.isfile(private_py_path):
                with open(private_py_path, "r", encoding="utf-8") as f:
                    code = f.read()
                cleared_code = clear_variables_in_code(code)
                dest_folder = os.path.join(current_dir, entry)
                os.makedirs(dest_folder, exist_ok=True)
                dest_file = os.path.join(dest_folder, "private.py")
                with open(dest_file, "w", encoding="utf-8") as f:
                    f.write(cleared_code)


find_and_copy_cleared()
