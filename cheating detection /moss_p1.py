import os
import subprocess 
import warnings
import shutil

project = "p2"
question_lower = "#q6"
question_upper = "#Q6"

sub = {}
for f in os.listdir("moss"):
    if f.startswith(project) and f.endswith(".ipynb"): 
        fs = f.split("_")
        fss = fs[2].split(".")
        netid = fs[1]
        if netid not in sub: 
            sub[netid] = [fss[0]]
        else:
            sub[netid].append(fss[0])
            
final = []
for i in sub: 
    final_sub = project + "_" + i + "_" + max(sub[i]) + ".ipynb"
    final.append(final_sub) 

print(final)

# for i in range(len(final)): 
#     if i % 20 == 0: 
#         print(i)
#     subprocess.run(["jupyter", "nbconvert", "--no-prompt", "--to", "script", final[i]], cwd="moss")
    
# subprocess.run(["mkdir", project], cwd="moss")
    
# for f in os.listdir("moss"):
#     if f.endswith(".py"):
#         with open("moss/" + f, "r", encoding="utf-8") as ff:
#             data = ff.read()
#             if question_lower in data:
#                 ind = data.split(question_lower)
#                 if len(ind) == 2: 
#                     with open("moss/" + f, "w") as ff:
#                         ff.write(ind[1])
#                     shutil.move("moss/" + f, "moss/" + project + "/" + f)
#             if "#Q25" in data: 
#                 ind = data.split("#Q25")
#                 if len(ind) == 2: 
#                     with open("moss/" + f, "w") as ff:
#                         ff.write(ind[1])
#                     shutil.move("moss/" + f, "moss/" + project + "/" + f)


            