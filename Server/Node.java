import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Random;

public class Node {

    private static NodeController nc = null;
    private TCPChild child;

    private int x = 0;
    private int y = 0;

    private int bw = 0;
    private int sf = 0;
    private int ch = 1;
    private int pwr = 0;
    private String panid = "0000";
    private String ownid = "0000";

    // コンストラクタ
    public Node() {}
    public Node(int x, int y) {
        this.x = x;
        this.y = y;
    }

    // インスタンス
    public void setNodeController(NodeController nc) {
        this.nc = nc;
    }
    public void setTCPChild(TCPChild child) {
        this.child = child;
    }

    // 削除
    public void remove() {
        nc.removeNode(x, y);
    }

    /* -------------------------------------------------- */
    // 座標
    /* -------------------------------------------------- */
    // 通常座標
    public void setPosition(int x, int y) {
        this.x = x;
        this.y = y;
    }
    public int[] getPosition() {
        int[] position = {x, y};
        return position;
    }

    // 移動用
    private ArrayList<Integer> waypointX = new ArrayList<Integer>();
    private ArrayList<Integer> waypointY = new ArrayList<Integer>();

    public void addNextPosition(int x, int y) {
        this.waypointX.add(x);
        this.waypointY.add(y);
    }

    public int[] getNextPosition() {
        int[] nextPosition = new int[2];
        if(getWaypointSize() > 0) {
            nextPosition[0] = waypointX.get(0);
            nextPosition[1] = waypointY.get(0);
        } else {
            nextPosition[0] = x;
            nextPosition[1] = y;
        }
        return nextPosition;
    }

    public ArrayList<Integer> getWaypointsX() {
        return waypointX;
    }

    public ArrayList<Integer> getWaypointsY() {
        return waypointY;
    }

    public int getWaypointSize() {
        return waypointX.size();
    }

    public void removeWaypoint(int x, int y) {
        double distance;
        for(int i = 0; i < getWaypointSize(); i++) {
            distance = Math.sqrt(Math.pow(waypointX.get(i) - x, 2) + Math.pow(waypointY.get(i) - y, 2));
            if(distance < 10.0) {
                waypointX.remove(i);
                waypointY.remove(i);
            }
        }
    }

    private int cnt = 0;
    public void moveNextPosition() {
        int pos[] = getNextPosition();
        double _x = (pos[0] - x) / 10;
        double _y = (pos[1] - y) / 10;
        x += (int)_x;
        y += (int)_y;

        // 接近すると次のウェイポイントへ
        double distance = Math.sqrt(Math.pow(pos[0] - x, 2) + Math.pow(pos[1] - y, 2));
        if(distance < 15.0) {
            if(waypointX.size() > 0) {
                waypointX.add(pos[0]);
                waypointY.add(pos[1]);
                waypointX.remove(0);
                waypointY.remove(0);
            }
        }
    }

    /* -------------------------------------------------- */
    // LoRaパラメータ
    /* -------------------------------------------------- */
    public void setParameter(String msg) {
        bw = Integer.parseInt(msg.substring(0, 2), 16);
        sf = Integer.parseInt(msg.substring(2, 4), 16);
        ch = Integer.parseInt(msg.substring(4, 6), 16);
        pwr = Integer.parseInt(msg.substring(6, 8), 16);
        panid = msg.substring(8, 12);
        ownid = msg.substring(12, 16);
        return;
    }

    public int getBandwidth() {
        return bw;
    }

    public int getSpreadfactor() {
        return sf;
    }

    public int getChannel() {
        return ch;
    }

    public int getPower() {
        return pwr;
    }

    public String getPanid() {
        return panid;
    }

    public String getOwnid() {
        return ownid;
    }

    // 各種シミュレート情報
    public int getRange() {
        return (sf + pwr) * 10;
    }
    public int getSpeed() {
        int result = 1000;
        switch(bw) {
            case 3:
                result = (int)(5.2116 * Math.exp(0.5778 * sf));
                break;
            case 4:
                result = (int)(2.6071 * Math.exp(0.5778 * sf));
                break;
            case 5:
                result = (int)(1.2986 * Math.exp(0.5781 * sf));
                break;
            case 6:
                result = (int)(0.6413 * Math.exp(0.5793 * sf));
                break;
        }
        return result;
    }

    /* -------------------------------------------------- */
    // 通信関係
    /* -------------------------------------------------- */

    // 受信排他制御
    private Boolean sendLock = false;
    private Boolean recvLock = false;
    private Boolean failed = false;
    public void setSendLock(Boolean status) {
        sendLock = status;
    }
    public Boolean getSendLock() {
        return sendLock;
    }
    public void setRecvLock(Boolean status) {
        recvLock = status;
    }
    public Boolean getRecvLock() {
        return recvLock;
    }
    public void setFailed(Boolean status) {
        failed = status;
    }
    public Boolean getFailed() {
        return failed;
    }

    // パケット送信
    public void sendPacket(String msg) {
        /* ------------------------------ */
        // 設定パケット
        /* ------------------------------ */
        if(panid.equals("0000")) {
            setParameter(msg);
            return;
        }

        /* ------------------------------ */
        // 通常パケット(エラーチェック)
        /* ------------------------------ */

        // 送信長チェック
        if(msg.length() <= 8 || 58 < msg.length()) {
            this.child.send("NG 100");
            return;
        }

        // 電波状況
        if(getSendLock()) {
            // 送信異常(送信中の送信要求)
            this.child.send("NG 101");
            return;
        }
        if(getRecvLock()) {
            // 送信異常(キャリアセンス検出)
            this.child.send("NG 102");
            return;
        }

        /* ------------------------------ */
        // 通常パケット
        /* ------------------------------ */
        double range = this.getRange() / 2.0;
        ArrayList<Node> nodes = nc.getNodesByDistance(this, range);

        // 排他制御
        ArrayList<Node> lockedNodes = new ArrayList<Node>();
        for(Node node : nodes) {
            // LoRaパラメータが同一で、受信中のノードに対しては
            // 妨害電波となるため、電波混信再現のため、setFailed(true)とする
            if(nc.checkConnectivity(this, node) && node.getRecvLock()) {
                node.setFailed(true);
            }

            // LoRaパラメータが同一で、フリーのノードに対しては
            // 受信中フラグを立てる
            if(nc.checkConnectivity(this, node) && node.getRecvLock() == false){
                node.setRecvLock(true);
                lockedNodes.add(node);
            }
        }

        // 送信時間シミュレート (Band Width、Spread Factorの影響を受ける)
        setSendLock(true);
        try {
            Thread.sleep(getSpeed());
        } catch(InterruptedException e){
            e.printStackTrace();
        }
        setSendLock(false);

        // 他ノードへの送信
        for(Node node : lockedNodes) {
            node.setRecvLock(false);
            node.receivePacket(msg, getOwnid());
        }
        this.child.send("OK");
        return;
    }

    // パケット受信
    public void receivePacket(String msg, String srcid) {
        // 各種パラメータ取得
        String _panid = null;
        String _dstid = null;
        String _payload = null;
        
        if(msg.length() > 8) {
            // (8Byteを超えるパケットは、フォーマットに従っていると仮定)
            _panid = msg.substring(0, 4);
            _dstid = msg.substring(4, 8);
            _payload = msg.substring(8, msg.length());
        }

        // 通信妨害チェック
        if(getFailed()) {
            setFailed(false);
            return;
        }

        // PANIDチェック
        // (8Byteを超えるパケットは、フォーマットに従っていると仮定)
        if(msg.length() > 8) {
            if(this.panid.equals(_panid) == false) {
                return;
            }
        }

        // 宛先チェック
        // (8Byteを超えるパケットは、フォーマットに従っていると仮定)
        if(msg.length() > 8) {
            if(_dstid.equals(this.ownid) == false && _dstid.equals("FFFF") == false) {
                return;
            }
        }

        // 送信パケットを受信パケットへ変換
        // (8Byteを超えるパケットは、フォーマットに従っていると仮定)
        String newMsg;
        if(msg.length() > 8) {
            newMsg = new String("FFC9" + _panid + srcid + _payload);
        } else {
            newMsg = new String(msg);
        }

        this.child.send(newMsg);
        return;
    }
}
