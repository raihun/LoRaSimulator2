import java.awt.*;
import java.awt.event.*;
import java.util.ArrayList;
import javax.swing.*;

import java.util.Random;

public class Screen extends JPanel implements MouseListener, MouseMotionListener, ActionListener {

    private static Progress progress = null;
    private static NodeController nc = null;
    private JPanel pPaint;
    private JButton btnStart;

    public Screen() {
        setLayout(null);

        // 左側パネル
        pPaint = new JPanel();
        pPaint.addMouseListener( this );
        pPaint.addMouseMotionListener( this );
        pPaint.setBounds( 0, 0, 1000, 720 );
        pPaint.setBackground( new Color(225, 225, 225) );
        this.add( pPaint );

        // 右上パネル1
        JPanel pMenu = new JPanel();
        pMenu.setBounds( 1005, 5, 265, 40 );
        pMenu.setLayout( new GridLayout(1, 2) );
        pMenu.setBackground( new Color(175, 220, 220) );

        btnStart = new JButton("Start");
        btnStart.setFont( new Font("MS ゴシック", Font.BOLD, 18) );
        btnStart.addActionListener( this );
        pMenu.add( btnStart );

        JButton btnStop = new JButton("---");
        btnStop.setFont( new Font("MS ゴシック", Font.BOLD, 18) );
        btnStop.addActionListener( this );
        pMenu.add( btnStop );
        this.add( pMenu );

        // 右上パネル2
        JPanel pControl = new JPanel();
        pControl.setBounds( 1005, 50, 265, 40 );
        pControl.setLayout( new GridLayout(2, 2) );
        pControl.setBackground( new Color(175, 220, 220) );

        JButton btnNodeAdd = new JButton("Range");
        btnNodeAdd.setFont( new Font("MS ゴシック", Font.BOLD, 18) );
        btnNodeAdd.addActionListener( this );
        pControl.add( btnNodeAdd );

        JButton btnNodeRemove = new JButton("Line");
        btnNodeRemove.setFont( new Font("MS ゴシック", Font.BOLD, 18) );
        btnNodeRemove.addActionListener( this );
        pControl.add( btnNodeRemove );

        JButton btnNodeRoute = new JButton("---");
        btnNodeRoute.setFont( new Font("MS ゴシック", Font.BOLD, 18) );
        btnNodeRoute.addActionListener( this );
        pControl.add( btnNodeRoute );

        JButton btnNodeRequest = new JButton("---");
        btnNodeRequest.setFont( new Font("MS ゴシック", Font.BOLD, 18) );
        btnNodeRequest.addActionListener( this );
        pControl.add( btnNodeRequest );

        this.add(pControl);

        // 右下パネル
        JPanel pPacket = new JPanel();
        pPacket.setBounds( 1005, 500, 265, 40);
        pPacket.setLayout( new GridLayout(1, 1) );
        pPacket.setBackground( new Color(175, 220, 220) );

        this.add(pPacket);
    }

    // インスタンス
    public void setNodeController(NodeController nc) {
        this.nc = nc;
    }
    public void setProgress(Progress progress) {
        this.progress = progress;
    }

    public void render() {
        Image back = createImage(1000, 720);
        Graphics buffer = back.getGraphics();
        buffer.setColor( new Color(225, 225, 225) );
        buffer.fillRect( 0, 0, 1000, 720 );
        buffer.setColor( Color.black );
        renderNodes(buffer);
        getGraphics().drawImage(back, 0, 0, this);
    }

    private void renderNodes(Graphics buffer) {
        ArrayList<Node> nodeList = nc.getNodes();
        try {
            for(Node node : nodeList) {
                int[] pos = node.getPosition();

                // ノード描画
                buffer.setColor( Color.black );
                buffer.drawRect(pos[0]-2, pos[1]-2, 4, 4);

                // 通信距離描画
                int r = node.getRange();
                if(enableRange) {
                    buffer.drawOval(pos[0]-r/2, pos[1]-r/2, r, r);
                }
                /*
                // 電波描画
                if(node.isOperation()) {
                    int cnt = node.getCount();
                    buffer.drawOval(pos[0]-cnt/2, pos[1]-cnt/2, cnt, cnt);
                }

                // 線描画
                for(Node _node : nodeList) {
                    if(node == _node) continue;
                    if(nc.getDistance(node, _node) <= 100.0) {
                        int[] _pos = _node.getPosition();
                        buffer.drawLine(pos[0], pos[1], _pos[0], _pos[1]);
                    }
                }
                */

                // ノード名
                buffer.drawString(node.getOwnid(), pos[0]-10, pos[1]+20);
                // 終了
            }
        } catch(Exception e) {}
    }

    Boolean enableRange = false;
    public void actionPerformed( ActionEvent ae ) {
        String buttonName = ae.getActionCommand();
        switch(buttonName) {
            case "Start":
                progress.start();
                break;
            case "Range":
                enableRange = !enableRange;
                break;
        }
    }

    Node selectedNode = null;
    public void mousePressed( MouseEvent e ) {
        e.consume();
        ArrayList<Node> nodes = nc.getNodesByPosition(e.getX(), e.getY(), 10.0);
        if(nodes.size() <= 0) {
            return;
        }
        Node node = nodes.get(0);
        selectedNode = node;
    }
    public void mouseDragged( MouseEvent e ) {
        if(selectedNode != null) {
            selectedNode.setPosition(e.getX(), e.getY());
        }
    }
    public void mouseClicked( MouseEvent e ) {}
    public void mouseMoved( MouseEvent e ) {}
    public void mouseReleased( MouseEvent e ) {
        selectedNode = null;
    }
    public void mouseEntered( MouseEvent e ) {}
    public void mouseExited( MouseEvent e ) {}
}
