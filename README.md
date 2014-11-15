# Create Small Docker Images of Dynamically Linked Binaries

There have been some blog posts about people generating very small docker images from statically linked binaries. I wanted to see if i could do the same with dynamically linked binaries. Theory: as long as you provide the files that a process need it will run. 

To find out about what files a program uses we can start it with `strace`. This gives us the runtime view of the files it i needs. To find all the shared libraries that its dynamically linked with we can use the `ldd` tool.

First we need to find a suitable program. For this example i choose `fortune` that prints a fortune cookie to the commandline. The reason for that was that it is a dynamically linked binary and it also reads from files.

If we capture all the files that the program depends on we can create a docker image with only those files. This is all done within an existing Debian image. The resulting image will be based on the `scratch` base docker image.

*Note: This is done in a docker image and thats why i run as root*

### Step 1: Install the program
`$ apt-get install fortune`

### Step 2: Run the program with strace
```shell
root:/# strace -f -o fortune.strace.out /usr/games/fortune 
Never be led astray onto the path of virtue.
```
This will create a trace file called `fortune.strace.out`. The `-f` option tells strace to follow any child processes.

### Step 3: Check for any dynamically linked libraries
```shell
root:/# ldd /usr/games/fortune > fortune.ldd.out
```

### Step 4: Generate a unified list of files
```shell
root:/# ./filefilter.py fortune.strace.out fortune.ldd.out > fortune.file.lst
```
The `filefilter.py` script that is also contained in this repository will parse the output from strace and ldd and output a single list of path's to files that the program has dependencies on.


