import java.awt.event.WindowEvent;
import javax.swing.JFrame;

public class Main extends JFrame {

    private static NodeController nc = new NodeController();
    private static Progress progress = new Progress();
    private static Property property = new Property();
    private static Screen screen = new Screen();
    private static TCPListener tcp = new TCPListener();

    public Main() {
        screen.setNodeController(nc);
        screen.setProgress(progress);
        screen.setProperty(property);
        progress.setScreen(screen);
        tcp.setNodeController(nc);
        tcp.start();

        property.setNodeController(nc);

        setDefaultCloseOperation( JFrame.EXIT_ON_CLOSE );
        getContentPane().add( screen );
        setSize( 1280, 720 );
        setTitle( "NO TITLE" );
        setResizable( false );
        setVisible( true );
    }

    public static void main(String[] args) {
        new Main();
    }
}
