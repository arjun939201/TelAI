
from app.melimi.subject import subject_inventory

info = subject_inventory()
print("Melimi Telugu subject inventory:")
print("documents:", info["documents"])
for key, value in info["by_kind"].items():
    print(f"{key}: {value}")

if info["documents"] < 3:
    print("\nWARNING: The repository contains only a small seed subject.")
    print("Copy your complete Melimi Telugu language files into melimi_telugu/")
