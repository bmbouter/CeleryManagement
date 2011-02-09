import subprocess
import os
import fnmatch

dirname, filename = os.path.split(os.path.abspath(__file__))

# Represents the order in which the files will be concatenated
file_list = ["json.js", "ajax.js", "core.js", "System.js", "Chart.js", "DataParser.js", "EventBus.js", "query.js"]

def concatenate():
    master_file = open(dirname + "/" + "cma-master.js", "w")

    for file_name in file_list:
        f = open(dirname + "/" + file_name, "r")
        master_file.write(f.read())

def minify():
    current_dir = os.listdir(dirname)
    try:
        min_file = fnmatch.filter(current_dir, "cma-min.*.js")[0]
    except IndexError:
        min_file = "cma-min.0.js"
    version = min_file.split(".")
    version = int(version[1]) + 1
    new_file = "cma-min." + str(version) + ".js"
    subprocess.call(dirname + "/" + "uglifyjs/bin/uglifyjs -o " + dirname + "/" + new_file + " " + dirname + "/"  + "cma-master.js", shell=True)
    try:
        os.remove(dirname + "/" + min_file)
    except OSError:
        pass
    subprocess.call("git add " + dirname + "/"  + str(new_file), shell=True)

if __name__ == "__main__":
    concatenate()
    minify()
