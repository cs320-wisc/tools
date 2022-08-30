import os
import shutil

project = "p3"

# for f in os.listdir("moss"): 
#     if f.startswith(project) and f.endswith(".ipynb"): 
#         os.rename("moss/" + f, "moss/" + f[:-5] + "py")

sub = {}
for f in os.listdir("moss"):
    if f.startswith(project) and f.endswith(".py"):
        fs = f.split("_")
        fss = fs[2].split(".")
        netid = fs[1]
        if netid not in sub: 
            sub[netid] = [fss[0]]
        else:
            sub[netid].append(fss[0])
            
final = []
for i in sub: 
    final_sub = project + "_" + i + "_" + max(sub[i]) + ".py"
    final.append(final_sub)

split_line = "def reveal_secrets"

for f in final:
    py = "moss/" + f
    new_py = "moss/" + project + "/" + f

    with open(py, "r", encoding="utf-8") as ff:
        data = ff.read()
        if split_line in data:
            first_split = data.split(split_line)
            if len(first_split) == 2:
                after_first = first_split[1]
                if "def" in first_split[1]: 
                    after_first = first_split[1].split("def")[0]
                after_first = split_line + after_first
                
                with open(py, "w") as ff:
                    ff.write(after_first)
                shutil.copy(py, new_py)
