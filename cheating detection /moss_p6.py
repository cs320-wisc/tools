import os
import subprocess 
import warnings
import shutil
import sys

project = "p6"
question_lower = "#q15"
question_upper = "#Q15"

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

def unzip_files():    
    for i in range(len(final)): 
        if i % 20 == 0: 
            print(i)
        subprocess.run(["unzip", "-q", final[i], "-d", final[i][:-6]], cwd="moss")

def ipynb_to_py(): 
    for i in range(len(final)): 
        if i % 20 == 0: 
            print(i)
        subprocess.run(["jupyter", "nbconvert", "--no-prompt", "--to", "script", final[i]], cwd="moss")

def collect(): 
    subprocess.run(["mkdir", project], cwd="moss")
    
#     for f in final:
#         file = f[:-6]
#         py = "moss/" + file + ".py"
#         new_py = "moss/" + project + "/" + file + ".py"

#         if file in os.listdir("moss"):
#             if file.endswith(".py"): 
#                 with open(py, "r", encoding="utf-8") as ff:
#                     data = ff.read()
#                     if question_lower in data:
#                         ind = data.split(question_lower)
#                         if len(ind) == 2: 
#                             with open(py, "w") as ff:
#                                 ind = ind[1].split("\n")
#                                 ff.write("\n".join(ind[:-5]))
#                             shutil.copy(py, new_py)
#                     if question_upper in data: 
#                         ind = data.split(question_upper)
#                         if len(ind) == 2: 
#                             with open(py, "w") as ff:
#                                 ind = ind[1].split("\n")
#                                 ff.write("\n".join(ind[:-5]))
#                             shutil.copy(py, new_py)
    for file in os.listdir("moss"):
        if file.endswith(".py"):
            py = "moss/" + file
            new_py = "moss/" + project + "/" + file
            with open(py, "r", encoding="utf-8") as f:
                data = f.read()
                if question_lower in data:
                    ind = data.split("tracts.geojson")
                    if len(ind) == 2: 
                        shutil.copy(py, new_py)
                        with open(new_py, "w") as ff:
#                             ind = ind[1].split("\n")
                            ff.write(ind[1])
                        
#                 if question_upper in data: 
#                     ind = data.split(question_upper)
#                     if len(ind) == 2: 
#                         shutil.copy(py, new_py)
#                         with open(new_py, "w") as ff:
#                             ind = ind[1].split("\n")
#                             ff.write("\n".join(ind[5:]))

def main(): 
    if sys.argv[1] == "unzip_files":
        unzip_files()
    elif sys.argv[1] == "ipynb_to_py": 
        ipynb_to_py()
    elif sys.argv[1] == "collect":
        collect()
    elif sys.argv[1] == "all": 
        unzip_files()
        ipynb_to_py()
        collect()
             
if __name__ == '__main__':
     main()