public class ManyThreads {

    private static void helpAndExit() {
	System.err.println("usage: java ManyThreads <NUM THREADS>");
	System.err.println("Please provide the number of Threads you want to spawn.");
	System.exit(1);
    }

    public static void main(String[] args) {
	if ( args.length == 0) {
	    helpAndExit();
	}

	int count = 0;
	try {
	    count = Integer.parseInt(args[0]);
	} catch (NumberFormatException e) {
	    helpAndExit();
	}

	Runnable r = new Runnable() {
		public void run() {
		    while(true) {
			// Do much of nothing...
			try {
			    Thread.sleep(100000);
			} catch (Exception e) {
			}
		    }
		}
	    };
	for(int i = 0; i < count; i++) {
	    Thread t = new Thread(r);
	    System.out.println("Starting thread " + i);
	    t.start();
	}
    }
}
