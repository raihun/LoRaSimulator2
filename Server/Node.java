import java.util.ArrayList;
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

    // 座標
    public void setPosition(int x, int y) {
        this.x = x;
        this.y = y;
    }
    public int[] getPosition() {
        int[] position = {x, y};
        return position;
    }

    // 各種設定
    public void setParameter(String msg) {
        bw = Integer.parseInt(msg.substring(0, 2), 16);
        sf = Integer.parseInt(msg.substring(2, 4), 16);
        ch = Integer.parseInt(msg.substring(4, 6), 16);
        pwr = Integer.parseInt(msg.substring(6, 8), 16);
        panid = msg.substring(8, 12);
        ownid = msg.substring(12, 16);
        return;
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
        // 通常パケット
        /* ------------------------------ */
        double range = this.getRange() / 2.0;
        ArrayList<Node> nodes = nc.getNodesByDistance(this, range);

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

        // 排他制御
        ArrayList<Node> lockedNodes = new ArrayList<Node>();
        for(Node node : nodes) {
            if(node.getRecvLock()) {
                node.setFailed(true);
            } else {
                node.setRecvLock(true);
                lockedNodes.add(node);
            }
        }
        setSendLock(true);
        try {
            Thread.sleep(3000);
        } catch(InterruptedException e){
            e.printStackTrace();
        }
        for(Node node : lockedNodes) {
            node.setRecvLock(false);
            node.receivePacket(msg, getPanid(), getOwnid());
        }
        setSendLock(false);
        this.child.send("OK");
        return;
    }

    // パケット受信
    public void receivePacket(String msg, String panid, String srcid) {
        if(getFailed()) {
            setFailed(false);
            return;
        }

        String payload = msg.substring(8, msg.length());
        String newMsg = "FFC9" + panid + srcid + payload;
        this.child.send(newMsg);
        return;
    }
}
