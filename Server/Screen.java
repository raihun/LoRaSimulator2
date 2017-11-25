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
    private JButton btnRange;
    private JButton btnLine;
    private JButton btnAddPoint;
    private JButton btnRemovePoint;
    private JButton btnMove;
    private JTextField tfCommand;

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
        pControl.setBounds( 1005, 50, 265, 60 );
        pControl.setLayout( new GridLayout(3, 2) );
        pControl.setBackground( new Color(175, 220, 220) );

        btnRange = new JButton("Range");
        btnRange.setFont( new Font("MS ゴシック", Font.BOLD, 18) );
        btnRange.setForeground(Color.RED);
        btnRange.addActionListener( this );
        pControl.add( btnRange );

        btnLine = new JButton("Line");
        btnLine.setFont( new Font("MS ゴシック", Font.BOLD, 18) );
        btnLine.setForeground(Color.RED);
        btnLine.addActionListener( this );
        pControl.add( btnLine );

        btnAddPoint = new JButton("AddPoint");
        btnAddPoint.setFont( new Font("MS ゴシック", Font.BOLD, 18) );
        btnAddPoint.setForeground(Color.BLACK);
        btnAddPoint.addActionListener( this );
        pControl.add( btnAddPoint );

        btnRemovePoint = new JButton("RemovePoint");
        btnRemovePoint.setFont( new Font("MS ゴシック", Font.BOLD, 18) );
        btnRemovePoint.setForeground(Color.BLACK);
        btnRemovePoint.addActionListener( this );
        pControl.add( btnRemovePoint );

        btnMove = new JButton("Move");
        btnMove.setFont( new Font("MS ゴシック", Font.BOLD, 18) );
        btnMove.setForeground(Color.BLACK);
        btnMove.addActionListener( this );
        pControl.add( btnMove );

        this.add(pControl);

        // 右下パネル
        JPanel pCommand = new JPanel();
        pCommand.setBounds( 1005, 610, 265, 80);
        pCommand.setLayout( new GridLayout(2, 1) );
        pCommand.setBackground( new Color(175, 220, 220) );

        tfCommand = new JTextField();
        pCommand.add( tfCommand );

        JPanel pCommandChild = new JPanel();
        pCommandChild.setLayout( new GridLayout(1, 2) );
        pCommandChild.setBackground( new Color(175, 220, 220) );

        JButton btnSend = new JButton("Send");
        btnSend.setFont( new Font("MS ゴシック", Font.BOLD, 18) );
        btnSend.addActionListener( this );
        pCommandChild.add( btnSend );

        JButton btnRecv = new JButton("Recv");
        btnRecv.setFont( new Font("MS ゴシック", Font.BOLD, 18) );
        btnRecv.addActionListener( this );
        pCommandChild.add( btnRecv );

        pCommand.add( pCommandChild );
        this.add(pCommand);
    }

    // インスタンス
    public void setNodeController(NodeController nc) {
        this.nc = nc;
    }
    public void setProgress(Progress progress) {
        this.progress = progress;
    }

    private int cnt = 0;
    public void render() {
        Image back = createImage(1000, 720);
        Graphics buffer = back.getGraphics();
        buffer.setColor( new Color(225, 225, 225) );
        buffer.fillRect( 0, 0, 1000, 720 );
        buffer.setColor( Color.black );
        renderNodes(buffer);
        getGraphics().drawImage(back, 0, 0, this);
        cnt = (cnt + 25) % Integer.MAX_VALUE;
    }

    private void renderNodes(Graphics buffer) {
        ArrayList<Node> nodeList = nc.getNodes();
        try {
            for(Node node : nodeList) {
                // ノード移動
                if(enableMove && node.getWaypointSize() > 0) {
                    node.moveNextPosition();
                }
            }
            for(Node node : nodeList) {
                int[] pos = node.getPosition();
                int[] nextPos = node.getNextPosition();
                int r = node.getRange();

                ArrayList<Integer> nextX = node.getWaypointsX();
                ArrayList<Integer> nextY = node.getWaypointsY();
                if(enableAddPoint || enableRemovePoint) {
                    for(int i = 0; i < nextX.size(); i++) {
                        buffer.setColor( Color.red );
                        buffer.fillRect(nextX.get(i)-1, nextY.get(i)-1, 2, 2);
                        buffer.drawString("" + (i + 1), nextX.get(i)-3, nextY.get(i)+15);
                    }
                }

                // ノード描画
                buffer.setColor( Color.black );
                if(node.getSendLock()) {
                    buffer.setColor( Color.orange );
                }
                if(node.getRecvLock()) {
                    buffer.setColor( Color.blue );
                }
                if(node.getFailed()) {
                    buffer.setColor( Color.red );
                }
                buffer.fillRect(pos[0]-3, pos[1]-3, 6, 6);

                // ノード選択
                buffer.setColor( Color.gray );
                if(selectNode == node) {
                    buffer.drawOval(pos[0]-10, pos[1]-10, 20, 20);
                }

                // 通信距離描画
                buffer.setColor( Color.black );
                if(enableRange) {
                    buffer.drawOval(pos[0]-r/2, pos[1]-r/2, r, r);
                }

                // 電波描画
                if(node.getSendLock()) {
                    int buf = cnt % r;
                    buffer.drawOval(pos[0]-buf/2, pos[1]-buf/2, buf, buf);
                }

                // 線描画
                if(enableLine) {
                    for(Node _node : nodeList) {
                        if(node == _node) continue;
                        int _r = node.getRange();
                        double minRange = Math.min(r/2.0, _r/2.0);
                        if(nc.getDistance(node, _node) <= minRange) {
                            int[] _pos = _node.getPosition();
                            buffer.drawLine(pos[0], pos[1], _pos[0], _pos[1]);
                        }
                    }
                }

                // ノード名
                buffer.drawString(node.getOwnid(), pos[0]-15, pos[1]+20);
            }
        } catch(Exception e) {}
    }

    private Boolean enableRange = true;
    private Boolean enableLine = true;
    private Boolean enableAddPoint = false;
    private Boolean enableRemovePoint = false;
    private Boolean enableMove = false;
    public void actionPerformed( ActionEvent ae ) {
        String buttonName = ae.getActionCommand();
        switch(buttonName) {
            case "Start":
                progress.start();
                btnStart.setEnabled(false);
                break;
            case "Range":
                enableRange = !enableRange;
                if(enableRange) {
                    btnRange.setForeground(Color.RED);
                } else {
                    btnRange.setForeground(Color.BLACK);
                }
                break;
            case "Line":
                enableLine = !enableLine;
                if(enableLine) {
                    btnLine.setForeground(Color.RED);
                } else {
                    btnLine.setForeground(Color.BLACK);
                }
                break;
            case "AddPoint":
                enableAddPoint = !enableAddPoint;
                if(enableAddPoint) {
                    btnAddPoint.setForeground(Color.RED);
                } else {
                    btnAddPoint.setForeground(Color.BLACK);
                }
                break;
            case "RemovePoint":
                enableRemovePoint = !enableRemovePoint;
                if(enableRemovePoint) {
                    btnRemovePoint.setForeground(Color.RED);
                } else {
                    btnRemovePoint.setForeground(Color.BLACK);
                }
                break;
            case "Move":
                enableMove = !enableMove;
                if(enableMove) {
                    btnMove.setForeground(Color.RED);
                } else {
                    btnMove.setForeground(Color.BLACK);
                }
                break;

            // 右下メニュー
            case "Send":
                if(selectNode == null) break;
                selectNode.sendPacket(tfCommand.getText());
                break;
            case "Recv":
                if(selectNode == null) break;
                selectNode.receivePacket(tfCommand.getText(), selectNode.getOwnid());
                break;
        }
    }

    Node selectNode = null;
    Node dragNode = null;
    public void mousePressed( MouseEvent e ) {
        e.consume();
        // ノード移動先
        if(selectNode != null && enableAddPoint) {
            selectNode.addNextPosition(e.getX(), e.getY());
        }

        // ノード削除
        if(enableRemovePoint) {
            selectNode.removeWaypoint(e.getX(), e.getY());
        }

        ArrayList<Node> nodes = nc.getNodesByPosition(e.getX(), e.getY(), 10.0);
        if(nodes.size() <= 0) {
            return;
        }
        Node node = nodes.get(0);
        dragNode = node;

        // ノード選択
        if(selectNode != node) {
            selectNode = node;
        } else {
            selectNode = null;
        }
    }
    public void mouseDragged( MouseEvent e ) {
        if(dragNode != null) {
            dragNode.setPosition(e.getX(), e.getY());
        }
    }
    public void mouseClicked( MouseEvent e ) {}
    public void mouseMoved( MouseEvent e ) {}
    public void mouseReleased( MouseEvent e ) {
        dragNode = null;
    }
    public void mouseEntered( MouseEvent e ) {}
    public void mouseExited( MouseEvent e ) {}
}

/*
    Map表示する際に必要なコード
    import java.awt.image.BufferedImage;
    import java.io.*;
    import javax.imageio.*;

    BufferedImage image = null;
	try
	{
        image = ImageIO.read(new File("map.png"));
    } catch (Exception e) {
        e.printStackTrace();
	}
    buffer.drawImage(image, 0, 0, this);
*/
