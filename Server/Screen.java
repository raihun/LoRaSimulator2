import java.awt.*;
import java.awt.event.*;
import java.util.ArrayList;
import javax.swing.*;

import java.util.Random;

public class Screen extends JPanel implements MouseListener, MouseMotionListener, ActionListener {

    private static Progress progress = null;
    private static Property property = null;
    private static NodeController nc = null;
    private JPanel pPaint;
    private JButton btnStart;
    private JButton btnRange;
    private JButton btnLine;
    private JButton btnAddPoint;
    private JButton btnRemovePoint;
    private JButton btnMove;
    private JLabel labelOwnid;
    private JTextField tfBandwidth;
    private JTextField tfSpreadfactor;
    private JTextField tfChannel;
    private JTextField tfPower;
    private JTextField tfCommand;
    private JButton btnAutoPosition;

    public Screen() {
        setLayout(null);

        // 左側パネル
        pPaint = new JPanel();
        pPaint.addMouseListener( this );
        pPaint.addMouseMotionListener( this );
        pPaint.setBounds( 0, 0, 1000, 720 );
        pPaint.setBackground( new Color(225, 225, 225) );
        this.add( pPaint );

        // 右第1パネル
        JPanel pMenu = new JPanel();
        pMenu.setBounds( 1005, 5, 265, 35 );
        pMenu.setLayout( new GridLayout(1, 2) );
        pMenu.setBackground( new Color(175, 220, 220) );

        btnStart = new JButton("Start");
        btnStart.setFont( new Font("MS ゴシック", Font.BOLD, 16) );
        btnStart.addActionListener( this );
        pMenu.add( btnStart );

        JButton btnStop = new JButton("---");
        btnStop.setFont( new Font("MS ゴシック", Font.BOLD, 16) );
        btnStop.addActionListener( this );
        pMenu.add( btnStop );
        this.add( pMenu );

        // 右第2パネル
        JPanel pControl = new JPanel();
        pControl.setBounds( 1005, 50, 265, 60 );
        pControl.setLayout( new GridLayout(3, 2) );
        pControl.setBackground( new Color(175, 220, 220) );

        btnRange = new JButton("Range");
        btnRange.setFont( new Font("MS ゴシック", Font.BOLD, 16) );
        btnRange.setForeground(Color.RED);
        btnRange.addActionListener( this );
        pControl.add( btnRange );

        btnLine = new JButton("Line");
        btnLine.setFont( new Font("MS ゴシック", Font.BOLD, 16) );
        btnLine.setForeground(Color.RED);
        btnLine.addActionListener( this );
        pControl.add( btnLine );

        btnAddPoint = new JButton("AddPoint");
        btnAddPoint.setFont( new Font("MS ゴシック", Font.BOLD, 16) );
        btnAddPoint.setForeground(Color.BLACK);
        btnAddPoint.addActionListener( this );
        pControl.add( btnAddPoint );

        btnRemovePoint = new JButton("RemovePoint");
        btnRemovePoint.setFont( new Font("MS ゴシック", Font.BOLD, 16) );
        btnRemovePoint.setForeground(Color.BLACK);
        btnRemovePoint.addActionListener( this );
        pControl.add( btnRemovePoint );

        btnMove = new JButton("Move");
        btnMove.setFont( new Font("MS ゴシック", Font.BOLD, 16) );
        btnMove.setForeground(Color.BLACK);
        btnMove.addActionListener( this );
        pControl.add( btnMove );

        this.add(pControl);

        // 右第3パネル
        JPanel pNodeControl = new JPanel();
        pNodeControl.setBounds( 1005, 120, 265, 120);
        pNodeControl.setLayout( new GridLayout(6, 2) );
        pNodeControl.setBackground( new Color(175, 220, 220) );

        JLabel _labelOwnid = new JLabel("Own ID");
        _labelOwnid.setFont( new Font("MS ゴシック", Font.BOLD, 16) );
        pNodeControl.add( _labelOwnid );
        labelOwnid = new JLabel("----");
        labelOwnid.setFont( new Font("MS ゴシック", Font.BOLD, 16) );
        pNodeControl.add( labelOwnid );

        JLabel labelBandwidth = new JLabel("Band Width");
        labelBandwidth.setFont( new Font("MS ゴシック", Font.BOLD, 16) );
        pNodeControl.add( labelBandwidth );
        tfBandwidth = new JTextField();
        tfBandwidth.setText("3, 4, 5, 6");
        pNodeControl.add( tfBandwidth );

        JLabel labelSpreadfactor = new JLabel("Spread Factor");
        labelSpreadfactor.setFont( new Font("MS ゴシック", Font.BOLD, 16) );
        pNodeControl.add( labelSpreadfactor );
        tfSpreadfactor = new JTextField();
        tfSpreadfactor.setText("7-12");
        pNodeControl.add( tfSpreadfactor );

        JLabel labelChannel = new JLabel("Channel");
        labelChannel.setFont( new Font("MS ゴシック", Font.BOLD, 16) );
        pNodeControl.add( labelChannel );
        tfChannel = new JTextField();
        tfChannel.setText("1-15, 1-7, 1-5");
        pNodeControl.add( tfChannel );

        JLabel labelPower = new JLabel("Power");
        labelPower.setFont( new Font("MS ゴシック", Font.BOLD, 16) );
        pNodeControl.add( labelPower );
        tfPower = new JTextField();
        tfPower.setText("-4 - 13[dBm]");
        pNodeControl.add( tfPower );

        JButton btnDummy = new JButton("---");
        btnDummy.setFont( new Font("MS ゴシック", Font.BOLD, 16) );
        btnDummy.addActionListener( this );
        pNodeControl.add( btnDummy );

        JButton btnSet = new JButton("Set");
        btnSet.setFont( new Font("MS ゴシック", Font.BOLD, 16) );
        btnSet.addActionListener( this );
        pNodeControl.add( btnSet );

        this.add(pNodeControl);

        // 右第4パネル
        JPanel pPosition = new JPanel();
        pPosition.setBounds( 1005, 250, 265, 20);
        pPosition.setLayout( new GridLayout(1, 2) );
        pPosition.setBackground( new Color(175, 220, 220) );

        btnAutoPosition = new JButton("AutoPos");
        btnAutoPosition.setFont( new Font("MS ゴシック", Font.BOLD, 16) );
        btnAutoPosition.setForeground(Color.RED);
        btnAutoPosition.addActionListener( this );
        pPosition.add( btnAutoPosition );
        JButton btnSavePosition = new JButton("SavePos");
        btnSavePosition.setFont( new Font("MS ゴシック", Font.BOLD, 16) );
        btnSavePosition.addActionListener( this );
        pPosition.add( btnSavePosition );

        this.add(pPosition);

        // 右第5パネル
        JPanel pCommand = new JPanel();
        pCommand.setBounds( 1005, 610, 265, 80);
        pCommand.setLayout( new GridLayout(2, 1) );
        pCommand.setBackground( new Color(175, 220, 220) );

        tfCommand = new JTextField();
        tfCommand.setText("0001FFFF000A000B5F00HELLO");
        pCommand.add( tfCommand );

        JPanel pCommandChild = new JPanel();
        pCommandChild.setLayout( new GridLayout(1, 2) );
        pCommandChild.setBackground( new Color(175, 220, 220) );

        JButton btnSend = new JButton("Send");
        btnSend.setFont( new Font("MS ゴシック", Font.BOLD, 16) );
        btnSend.addActionListener( this );
        pCommandChild.add( btnSend );

        JButton btnRecv = new JButton("Recv");
        btnRecv.setFont( new Font("MS ゴシック", Font.BOLD, 16) );
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
    public void setProperty(Property property) {
        this.property = property;
    }

    private int cnt = 0;
    public void render() {
        // グラフィック関連
        Image back = createImage(1000, 720);
        Graphics buffer = back.getGraphics();
        buffer.setColor( new Color(225, 225, 225) );
        buffer.fillRect( 0, 0, 1000, 720 );
        buffer.setColor( Color.black );
        renderNodes(buffer);
        getGraphics().drawImage(back, 0, 0, this);

        // システム関連
        cnt = (cnt + 25) % Integer.MAX_VALUE;
        if(enableAutoPosition) {
            property.loadPosition();
        }
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
                        if(
                            nc.getDistance(node, _node) <= minRange &&
                            nc.checkConnectivity(node, _node)
                        ) {
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
    private Boolean enableAutoPosition = true;
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

                    // RemovePointの無効化
                    if(enableRemovePoint) {
                        btnRemovePoint.setForeground(Color.BLACK);
                        enableRemovePoint = false;
                    }
                } else {
                    btnAddPoint.setForeground(Color.BLACK);
                }
                break;
            case "RemovePoint":
                enableRemovePoint = !enableRemovePoint;
                if(enableRemovePoint) {
                    btnRemovePoint.setForeground(Color.RED);

                    // AddPointの無効化
                    if(enableAddPoint) {
                        btnAddPoint.setForeground(Color.BLACK);
                        enableAddPoint = false;
                    }
                } else {
                    btnRemovePoint.setForeground(Color.BLACK);
                }
                break;
            case "Move":
                if(!enableAutoPosition) {
                    enableMove = !enableMove;
                }
                if(enableMove) {
                    btnMove.setForeground(Color.RED);
                } else {
                    btnMove.setForeground(Color.BLACK);
                }
                break;

            // 右第3パネル メニュー
            case "Set":
                if(selectNode == null) break;
                // パラメータセット
                selectNode.setBandwidth(Integer.parseInt(tfBandwidth.getText()));
                selectNode.setSpreadfactor(Integer.parseInt(tfSpreadfactor.getText()));
                selectNode.setChannel(Integer.parseInt(tfChannel.getText()));
                selectNode.setPower(Integer.parseInt(tfPower.getText()));

                // パラメータ再描画
                labelOwnid.setText(selectNode.getOwnid());
                tfBandwidth.setText(String.valueOf(selectNode.getBandwidth()));
                tfSpreadfactor.setText(String.valueOf(selectNode.getSpreadfactor()));
                tfChannel.setText(String.valueOf(selectNode.getChannel()));
                tfPower.setText(String.valueOf(selectNode.getPower()));
                break;

            // 右第4パネル メニュー
            case "AutoPos":
                if(!enableMove) {
                    enableAutoPosition = !enableAutoPosition;
                }
                if(enableAutoPosition) {
                    btnAutoPosition.setForeground(Color.RED);
                } else {
                    btnAutoPosition.setForeground(Color.BLACK);
                }
                break;
            case "SavePos":
                property.savePosition();
                break;

            // 右第5パネル メニュー
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
        // Waypoint 追加
        if(selectNode != null && enableAddPoint) {
            selectNode.addNextPosition(e.getX(), e.getY());
        }

        // Waypoint 削除
        if(enableRemovePoint) {
            selectNode.removeWaypoint(e.getX(), e.getY());
        }

        ArrayList<Node> nodes = nc.getNodesByPosition(e.getX(), e.getY(), 10.0);
        if(nodes.size() <= 0) {
            return;
        }
        Node node = nodes.get(0);
        dragNode = node;

        // ノード 選択/解除
        if(selectNode != node) {
            // ノード 選択
            selectNode = node;

            // ノード情報 表示
            labelOwnid.setText(selectNode.getOwnid());
            tfBandwidth.setText(String.valueOf(selectNode.getBandwidth()));
            tfSpreadfactor.setText(String.valueOf(selectNode.getSpreadfactor()));
            tfChannel.setText(String.valueOf(selectNode.getChannel()));
            tfPower.setText(String.valueOf(selectNode.getPower()));
        } else {
            // ノード 選択解除
            selectNode = null;

            // ノード情報 クリア
            labelOwnid.setText("----");
            tfBandwidth.setText("3, 4, 5, 6");
            tfSpreadfactor.setText("7-12");
            tfChannel.setText("1-15, 1-7, 1-5");
            tfPower.setText("-4 - 13[dBm]");
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
