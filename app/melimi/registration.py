
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from app.config import settings
from app.github_sync import commit_language_entry
from app.melimi.index import reload_index
from app.melimi.registry import reload_registry

TARGET=Path(__file__).resolve().parents[2]/"melimi_telugu/vocabulary/chat_registered.json"

def _write_local(entry):
    TARGET.parent.mkdir(parents=True,exist_ok=True)
    try: rows=json.loads(TARGET.read_text(encoding="utf-8"))
    except Exception: rows=[]
    if not isinstance(rows,list): rows=[]
    source=entry["standard_or_source"]
    rows=[x for x in rows if x.get("standard_or_source")!=source]
    rows.append(entry)
    TARGET.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def build_entry(data):
    word=str(data.get("word","")).strip(); melimi=str(data.get("melimi_equivalent","")).strip()
    if not word: raise ValueError("Source/loan word is required.")
    if not melimi: raise ValueError("Melimi Telugu word is required.")
    return {"standard_or_source":word,"melimi":melimi,
      "root":str(data.get("root","")).strip(),"meaning":str(data.get("meaning","")).strip(),
      "part_of_speech":str(data.get("part_of_speech","")).strip(),
      "formation":str(data.get("formation","")).strip(),"status":"user_verified",
      "source":"chat_interface","created_at":datetime.now(timezone.utc).isoformat()}

async def register_word(data):
    entry=build_entry(data)
    if not settings.github_auto_commit:
        _write_local(entry); reload_index(); reload_registry()
        return {"entry":entry,"committed":False,"local":True}
    result=await commit_language_entry(entry)
    _write_local(entry)
    reload_index(); reload_registry()
    return {"entry":entry,"local":True,**result}
