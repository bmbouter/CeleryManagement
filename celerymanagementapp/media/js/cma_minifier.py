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
    new_file = "cma-min.js"
    subprocess.call(dirname + "/" + "uglifyjs/bin/uglifyjs -o " + dirname + "/" + new_file + " " + dirname + "/"  + "cma-master.js", shell=True)
    subprocess.call("git add " + dirname + "/"  + str(new_file), shell=True)
    os.remove(dirname + "/" + "cma-master.js")

if __name__ == "__main__":
    concatenate()
    minify()
