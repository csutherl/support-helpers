import java.lang.Thread;

/**
 * Run this with `java -Xmx10m -Xms10m OomeBytes'
 */
public class OomeBytes {
    private static final int MB = 1000000;

    public static void main(String[] args) {
	byte[] b = new byte[8*MB];
	try {
	    Thread.sleep(10000);
	} catch (Exception e) {
	    e.printStackTrace();
	}
    }
}
