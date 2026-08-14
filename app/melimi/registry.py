
import re
from functools import lru_cache
from app.melimi.index import build_index

TOKEN_RE=re.compile(r"[\u0C00-\u0C7F]+|[A-Za-z]+(?:['’-][A-Za-z]+)*")
FUNCTION_WORDS={
"నేను","నాకు","నా","నువ్వు","నీ","నీకు","మీరు","మీకు","అతను","ఆమె","వారు",
"ఇది","అది","ఇవి","అవి","ఏమి","ఏం","ఏంటి","ఎలా","ఎందుకు","ఎక్కడ","ఎప్పుడు",
"ఎవరు","ఎంత","ఎన్ని","ఒక","మరియు","లేదా","కానీ","అయితే","కూడా","మాత్రం","ఇంకా",
"ఇప్పుడు","అప్పుడు","ఇక్కడ","అక్కడ","లో","కు","కి","తో","నుండి","నుంచి","పై","కింద",
"కోసం","వల్ల","గురించి","మధ్య","లా","గా","అని","అంటే","లేదు","లేను","లేవు","కాదు",
"వద్దు","ఉంది","ఉన్న","ఉన్నారు","ఉన్నాను","ఉన్నావు","చెప్పు","చెప్పండి","రా","రండి",
"వెళ్లు","వెళ్లి","చేయి","చేయండి","అవును","సరే","హా","హాయ్","టేంకణములు"
}

def tokenize(t): return TOKEN_RE.findall(t or "")

def _values(entry, keys):
    out=[]
    for k in keys:
        v=entry.get(k)
        if isinstance(v,list): out += [str(x).strip() for x in v if str(x).strip()]
        elif isinstance(v,str) and v.strip(): out.append(v.strip())
    return out

@lru_cache(maxsize=1)
def lexical_inventory():
    registered=set(FUNCTION_WORDS)
    native=set(FUNCTION_WORDS)
    loan=set()
    standard_to_melimi={}
    melimi_to_standard={}
    forbidden_standard=set()
    for d in build_index():
        if d.kind!='vocabulary': continue
        for e in d.entries:
            mel=_values(e,("melimi","word","headword","forms","variants"))
            std=_values(e,("standard","standard_or_source","source_word"))
            status=str(e.get("status","")).lower()
            source_type=str(e.get("source_type","")).lower()
            registered.update(mel)
            if status in {"native","native_telugu","established","corpus-supported","derived-by-rule"} or source_type in {"native","native_telugu"}:
                native.update(mel); native.update(std)
            for a in std:
                for b in mel:
                    standard_to_melimi[a]=b
                    melimi_to_standard[b]=a
            if status in {"loan","loanword","borrowed","foreign"} or source_type in {"loan","loanword","borrowed","foreign"}:
                loan.update(std)
                # A loanword entry with a Melimi form is already resolved.
                if not mel:
                    forbidden_standard.update(std)
            # An established mapping is a hard lexical preference in Melimi mode.
            if mel:
                forbidden_standard.update(std)
    return {
      "registered":frozenset(registered),"native":frozenset(native),"loan":frozenset(loan),
      "standard_to_melimi":standard_to_melimi,"melimi_to_standard":melimi_to_standard,
      "forbidden_standard":frozenset(forbidden_standard)
    }

def reload_registry(): lexical_inventory.cache_clear()

def audit_response(text):
    inv=lexical_inventory(); out=[]
    for w in tokenize(text):
        is_loan=w in inv["loan"]
        gap=(w in inv["forbidden_standard"] and w not in inv["registered"])
        out.append({"word":w,"registered":w in inv["registered"],"native":w in inv["native"],
                    "loan":is_loan,"melimi_gap":gap,"clickable":is_loan or gap})
    return out

def strict_violations(text):
    inv=lexical_inventory(); violations=[]
    for w in tokenize(text):
        if w in inv["standard_to_melimi"]:
            violations.append({"standard":w,"melimi":inv["standard_to_melimi"][w]})
        elif w in inv["loan"] and w not in inv["registered"]:
            violations.append({"loan":w,"melimi":""})
    return violations

def analyze_word(word):
    inv=lexical_inventory()
    return {"word":word,"registered":word in inv["registered"],"native":word in inv["native"],
            "loan":word in inv["loan"],"melimi_equivalent":inv["standard_to_melimi"].get(word,""),
            "root_candidate":word}
