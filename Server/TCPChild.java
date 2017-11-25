import java.io.*;
import java.net.*;

public class TCPChild extends Thread {

    private Socket sockTCP;
    private Node node;

    public TCPChild( Socket sock, Node node ) {
        this.sockTCP = sock;
        this.node = node;
        this.node.setTCPChild(this);
    }

    public void send( String msg ) {
        try {
            OutputStream os = sockTCP.getOutputStream();
            byte[] data = msg.getBytes();
            os.write( data );
            os.flush();
        } catch ( IOException e ) {
            e.printStackTrace();
        }
    }

    public void run() {
        try {
            InputStream is = sockTCP.getInputStream();
            int size;
            byte[] buf = new byte[1024];
            while( (size = is.read(buf, 0, buf.length)) != -1 ) {
                String sBuf = new String( buf );
                node.sendPacket( sBuf.substring(0, size) );
            }
            sockTCP.close();
            node.remove();
        } catch ( IOException e ) {
            e.printStackTrace();
        }
    }

}
