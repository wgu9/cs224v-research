import json

def choose_view(profile: dict) -> str:
    if profile.get("pref") == "terse" or profile.get("hist_first_try_success",0) > 0.5:
        return "terse"
    return "guided"

def render(pattern_path: str, profile_path: str):
    pat = json.loads(open(pattern_path, "r", encoding="utf-8").read())
    prof = json.loads(open(profile_path, "r", encoding="utf-8").read())
    view = choose_view(prof)
    views = pat.get("views",{})
    return view, views.get(view,"(no content)")

if __name__ == "__main__":
    v, content = render("data/examples/patterns/pc_delimited_tail.json","data/examples/profiles.json")
    print("View:", v)
    print(content)
