#!/usr/bin/env python3
import importlib, argparse
from fastapi import FastAPI

def load_app(app_path: str) -> FastAPI:
    mod_name, obj_name = app_path.split(":")
    mod = importlib.import_module(mod_name)
    return getattr(mod, obj_name)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--app", default="app.main:app")
    args = p.parse_args()
    app = load_app(args.app)

    mutating = []
    for r in app.routes:
        methods = getattr(r, "methods", set())
        path = getattr(r, "path", "")
        if methods and path:
            if {"POST","PUT","PATCH","DELETE"} & methods:
                mutating.append((sorted(methods), path))

    print("# Mutating routes (audited via global middleware):")
    for methods, path in sorted(mutating, key=lambda x: x[1]):
        print(f"{','.join(methods):10s}  {path}")

if __name__ == "__main__":
    main()