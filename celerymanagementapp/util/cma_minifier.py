import subprocess
import os
import fnmatch

dirname, filename = os.path.split(os.path.abspath(__file__))
dirname = dirname + "/../media/js/"

# Represents the order in which the files will be concatenated
file_list = ["json.js", "ajax.js", "core.js", "System.js", "Chart.js", "DataParser.js", "EventBus.js", "query.js"]

def run():
    concatenate()
    return minify()

def concatenate():
    master_file = open(dirname + "cma-master.js", "w")

    for file_name in file_list:
        f = open(dirname + file_name, "r")
        master_file.write(f.read())

def minify():
    current_dir, current_filename = os.path.split(os.path.abspath(__file__))
    new_file = "cma-min.js"
    process = subprocess.Popen([current_dir + "/uglifyjs/bin/uglifyjs -o " + dirname + new_file + " " + dirname + "cma-master.js"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    
    error = process.communicate()[1]

    if error == "":
        subprocess.call("git add " + dirname + str(new_file), shell=True)
        os.remove(dirname + "cma-master.js")
        return True
    else:
        os.remove(dirname + "cma-master.js")
        return error

if __name__ == "__main__":
    run()
