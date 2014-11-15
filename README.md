Create Small Docker Images of Dynamically Linked Binaries

There have been some blog posts about people generating very small docker images from statically linked binaries. I wanted to see if i could do the same with dynamically linked binaries. Theory: as long as you provide the files that a process need it will run. 

To find out about what files a program uses we can start it with `strace`. This gives us the runtime view of the files it i needs. To find all the shared libraries that its dynamically linked with we can use the `ldd` tool.

First we need to find a suitable program. For this example i 
