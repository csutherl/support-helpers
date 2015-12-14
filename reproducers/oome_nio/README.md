# java.lang.OutOfMemoryError: Direct buffer memory

Run this with `java -XX:MaxDirectMemorySize=1k NioMemTest` to generate the OutOfMemoryError. If you run without MaxDirectMemorySize, the allocation will succedd with no command output.
