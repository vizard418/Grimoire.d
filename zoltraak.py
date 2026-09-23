#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys

class Zoltraak:
    """Clase principal para parsear un proyecto"""

    EXTENSION_MAP = {
        "python": {".py", ".requirements", ".toml", ".ini", ".cfg"},
        "python3": {".py", ".requirements", ".toml", ".ini", ".cfg"},
        "html": {".html", ".htm"},
        "css": {".css", ".scss", ".sass"},
        "js": {".js", ".ts", ".jsx", ".tsx"},
        "json": {".json"},
        "md": {".md"},
        "sql": {".sql"}
    }

    IGNORE_DIRS = {
        "__pycache__", ".git", "node_modules", "venv",
        ".venv", "env", "dist", "build", ".idea", ".vscode"
    }

    IGNORE_FILES = {
        ".DS_Store", "package-lock.json", "yarn.lock",
        "poetry.lock", "__init__.py"
    }

    def __init__(self, root_dir, active_flags):
        self.root_path = os.path.abspath(root_dir)
        self.active_flags = active_flags
        self.allowed_extensions = self._resolve_extensions()
        self._validate_directory()

    def _validate_directory(self):
        """Verifica que el directorio exista."""
        if not os.path.exists(self.root_path):
            print(f"Error: El directorio '{self.root_path}' no existe.", file=sys.stderr)
            sys.exit(1)

    def _resolve_extensions(self):
        """Combina las extensiones segun los flags activados."""
        if not self.active_flags:
            return None

        extensions = set()
        for flag in self.active_flags:
            if flag in self.EXTENSION_MAP:
                extensions.update(self.EXTENSION_MAP[flag])
        return extensions

    def _should_ignore(self, name, is_dir=False):
        """Determina si un directorio o archivo debe ser ignorado."""
        if is_dir:
            return name in self.IGNORE_DIRS or name.startswith(".")
        return name in self.IGNORE_FILES

    def _is_extension_allowed(self, filename):
        """Verifica si la extension esta permitida."""
        if not self.allowed_extensions:
            return True
        ext = os.path.splitext(filename)[1].lower()
        return ext in self.allowed_extensions

    def print_tree(self):
        """Imprime la estructura de arbol del proyecto."""
        print("--- ESTRUCTURA DEL DIRECTORIO ---")
        for dirpath, dirnames, filenames in os.walk(self.root_path):
            dirnames[:] = [
                d for d in sorted(dirnames) if not self._should_ignore(d, is_dir=True)
            ]

            rel_path = os.path.relpath(dirpath, self.root_path)
            indent_level = 0 if rel_path == "." else rel_path.count(os.sep) + 1
            indent = "  " * indent_level

            if rel_path != ".":
                print(f"{indent}[{os.path.basename(dirpath)}]")

            for filename in sorted(filenames):
                if self._should_ignore(filename, is_dir=False):
                    continue
                if not self._is_extension_allowed(filename):
                    continue
                print(f"{indent}  - {filename}")

    def print_files_content(self):
        """Imprime el contenido de los archivos filtrados."""
        print("\n--- CONTENIDO DE LOS ARCHIVOS ---\n")
        for dirpath, dirnames, filenames in os.walk(self.root_path):
            dirnames[:] = [
                d for d in sorted(dirnames) if not self._should_ignore(d, is_dir=True)
            ]

            for filename in sorted(filenames):
                if self._should_ignore(filename, is_dir=False):
                    continue
                if not self._is_extension_allowed(filename):
                    continue

                file_path = os.path.join(dirpath, filename)
                rel_file_path = os.path.relpath(file_path, self.root_path)
                ext = os.path.splitext(filename)[1].lower()

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    print(f"File: {rel_file_path}")
                    print("```" + (ext.lstrip(".") or "text"))
                    print(content)
                    print("```\n")
                except (UnicodeDecodeError, PermissionError):
                    continue

    def generate(self):
        """Ejecuta el proceso completo."""
        print(f"=== CONTEXTO DEL PROYECTO: {self.root_path} ===\n")
        self.print_tree()
        self.print_files_content()

def parse_arguments():
    """Configura y parsea los argumentos."""
    parser = argparse.ArgumentParser(prog='Zoltraak', description='Parsea archivos y genera contexto.')
    parser.add_argument("directory", type=str, help="Ruta del directorio")

    for flag in Zoltraak.EXTENSION_MAP.keys():
        parser.add_argument(f"--{flag}", action="store_true", help=f"Incluir archivos de {flag}")

    return parser.parse_args()

def main():
    args = parse_arguments()
    active_flags = [
        flag for flag in Zoltraak.EXTENSION_MAP.keys()
        if getattr(args, flag, False)
    ]

    parser_obj = Zoltraak(args.directory, active_flags)
    parser_obj.generate()

if __name__ == "__main__":
    main()
