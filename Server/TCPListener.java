import java.util.ArrayList;
import java.util.Random;

import java.io.*;
import java.net.*;

public class TCPListener extends Thread {

    private NodeController nc;
    private ServerSocket servSock;

    public TCPListener() {
        try {
            this.servSock = new ServerSocket(25561);
        } catch(IOException e) {
            e.printStackTrace();
        }
    }

    public void setNodeController(NodeController nc) {
        this.nc = nc;
    }

    public void run() {
        while ( true ) {
            try {
                Socket sockTCP = servSock.accept();
                Node node = this.nc.addNode(10, 10);
                TCPChild child = new TCPChild( sockTCP, node );
                child.start();
            } catch ( IOException e ) {
                e.printStackTrace();
            }
        }
    }

}
