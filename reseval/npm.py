import subprocess


###############################################################################
# Npm server management

# NOTE - shell=True is often not considered best practice. This is for two
#     reasons:
#         1) It assumes the binary is the program you expect it to be. In
#            this case, npm.
#         2) If parameterized, it can run malicious code. For example,
#            f'npm run {user_input}' where
#            user_input = 'nonexistant_arg; rm -rf /'.
#     In our use case, we've asked users to install npm and we do not
#     parameterize the commands. The alternative is to set shell=False and
#     require the user to provide the path to the npm executable.
###############################################################################


def build(verbose=False):
    """Build the optimized front-end client code"""
    stdout = None if verbose else subprocess.DEVNULL
    return subprocess.Popen('npm run build', shell=True, stdout=stdout)


def install():
    """Installs an npm package in the current directory"""
    return subprocess.Popen('npm install', shell=True)


def start():
    """Start the server process"""
    return subprocess.Popen('npm run dev', shell=True)
