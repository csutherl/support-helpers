# java.lang.OutOfMemoryError: unable to create new native thread

Run this with `java ManyThreads <NUM_THREADS>` to try and generate an OutOfMemoryError. It's best to run this program with a test user of some sort and set the user's `ulimit -u` very low. For example:

```
# su - testuser
# ulimit -u 24
# javac ManyThreads.java
# java ManyThreads 30 <-- Throws OutOfMemoryError.
```
