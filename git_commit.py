import subprocess
import os
import sys

from celerymanagementapp.util import cma_minifier

def start():
    minify_js()
    success = True
    if "--no-tests" not in sys.argv:
        success = run_tests()
    if success:
        commit()
        if "--no-pull" in sys.argv:
            pull()
            if "--no-tests" not in sys.argv:
                success = run_tests()
        if "--no-push" in sys.argv and success:
            push()

def minify_js():
    minified = cma_minifier.run()
    if not minified:
        print "There was an error during minification. Skipping this test."

def run_tests():
    current_dir = os.getcwd()
    output = subprocess.Popen(["python  manage.py test celerymanagementapp"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
    if output[1].find("FAILED") != -1:
        print output[1]
        return False
    else:
        print output[1]
        return True

def pull():
    subprocess.call("git pull", shell=True)

def push():
    subprocess.call("git push", shell=True)

def commit():
    if '-m' in sys.argv:
        index = sys.argv.index('-m')
        subprocess.call("git commit -m " + sys.argv[index+1] + ' -a', shell=True)
    else:
        subprocess.call("git commit -a", shell=True)

if __name__ == "__main__":
    start()
