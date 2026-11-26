import json

def save_json(path,data):
    with open(path,"w") as f:
        return json.dump(data,f,indent=4,ensure_ascii=False)

def save_simple(path,data):
    with open(path,"w") as f:
        for i in data:
            f.write(i)