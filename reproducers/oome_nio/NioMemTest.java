import java.nio.ByteBuffer;

public class NioMemTest {
    public static void main(String[] args) {
        System.out.println("Allocating...");
        ByteBuffer b = ByteBuffer.allocateDirect(1000000);
    }
}
