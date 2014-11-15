# Create Small Docker Images of Dynamically Linked Binaries

*For the impatient:*
`docker run perarneng/fortune` (3.831 MB)


There have been some blog posts about people generating very small docker images from statically linked binaries. I wanted to see if i could do the same with dynamically linked binaries. Theory: as long as you provide the files that a process need it will run. 

To find out about what files a program uses we can start it with `strace`. This gives us the runtime view of the files it i needs. To find all the shared libraries that its dynamically linked with we can use the `ldd` tool.

First we need to find a suitable program. For this example i choose `fortune` that prints a fortune cookie to the commandline. The reason for that was that it is a dynamically linked binary and it also reads from files.

If we capture all the files that the program depends on we can create a docker image with only those files. This is all done within an existing Debian image. The resulting image will be based on the `scratch` base docker image. The size of the fortune image is less than 4Mb, compared to the debain image that weighs in on 85.1 MB.


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

### Step 5: Create an archive of the files
```shell
root:/# cat fortune.lst | zip -@ fortune.zip
```
I want to have a `tar.gz` but have not yet found out how to do that and include the symbolic links as pysical files. That's wy i run it through zip first and unpack it in a separate folder. Then run tar and compress it to a file called `fortune.tar.gz`. The reason why i want it as a `tar.gz` is that it works best with dockers `ADD` command.
```shell
root:/# mkdir fortune_tmp ; cd fortune_tmp; unzip ../fortune.zip
root:/# tar cvfz ../fortune.tar.gz * ; cd .. ; rm -rf fortune_tmp
root:/# tar tvfz fortune.tar.gz 
drwxr-xr-x root/root         0 2014-11-15 18:56 etc/
-rw-r--r-- root/root      9021 2014-11-15 16:33 etc/ld.so.cache
drwxr-xr-x root/root         0 2014-11-15 18:56 lib/
drwxr-xr-x root/root         0 2014-11-15 18:56 lib/x86_64-linux-gnu/
-rwxr-xr-x root/root   1603600 2014-10-16 22:45 lib/x86_64-linux-gnu/libc.so.6
drwxr-xr-x root/root         0 2014-11-15 18:56 lib64/
-rwxr-xr-x root/root    136936 2014-10-16 22:45 lib64/ld-linux-x86-64.so.2
drwxr-xr-x root/root         0 2014-11-15 18:56 usr/
drwxr-xr-x root/root         0 2014-11-15 18:56 usr/games/
-rwxr-xr-x root/root     22240 2009-10-01 05:47 usr/games/fortune
drwxr-xr-x root/root         0 2014-11-15 18:56 usr/share/
drwxr-xr-x root/root         0 2014-11-15 18:56 usr/share/games/
drwxr-xr-x root/root         0 2014-11-15 15:56 usr/share/games/fortunes/
-rw-r--r-- root/root       540 2009-10-01 05:47 usr/share/games/fortunes/riddles.dat
-rw-r--r-- root/root     24516 2009-10-01 05:47 usr/share/games/fortunes/fortunes
-rw-r--r-- root/root     53589 2009-10-01 05:47 usr/share/games/fortunes/literature.u8
-rw-r--r-- root/root      1752 2009-10-01 05:47 usr/share/games/fortunes/fortunes.dat
-rw-r--r-- root/root     24516 2009-10-01 05:47 usr/share/games/fortunes/fortunes.u8
-rw-r--r-- root/root      1076 2009-10-01 05:47 usr/share/games/fortunes/literature.dat
-rw-r--r-- root/root     20294 2009-10-01 05:47 usr/share/games/fortunes/riddles
-rw-r--r-- root/root     53589 2009-10-01 05:47 usr/share/games/fortunes/literature
-rw-r--r-- root/root     20294 2009-10-01 05:47 usr/share/games/fortunes/riddles.u8
drwxr-xr-x root/root         0 2014-11-15 18:56 usr/lib/
drwxr-xr-x root/root         0 2014-11-15 18:56 usr/lib/x86_64-linux-gnu/
-rw-r--r-- root/root   1859144 2012-06-06 11:38 usr/lib/x86_64-linux-gnu/librecode.so.0
```
### Step 6: Copy the files out of the running container
```shell
$ docker cp 5d9ffe1ba9ee:/fortune.tar.gz .
```
### Step 7: Create the Dockerfile file
```Dockerfile
FROM scratch
ADD fortune.tar.gz /
CMD ["/usr/games/fortune"]
```
### Step 8: Build the image
```shell
$ docker build -t fortune .
```
**MAKE SURE THAT THE DIRECTORY ONLY CONTAINS:** `fortune.tar.gz` and `Dockerfile`

### Step 9: Run the image
```shell
$ docker run fortune 
Expect the worst, it's the least you can do.
```

## Final Notes
The resulting image is about 4Mb large and is much better than close to 100Mb that the debian image is. Since `strace` is analysing the runtime it might happen that all paths have not been executed and all files have not been opened. So its a little bit risky analysing output from strace. You shoud probably know what the program uses and mostly depend on ldd and manually include any other files.

The docker repo is located here: https://registry.hub.docker.com/u/perarneng/fortune/


