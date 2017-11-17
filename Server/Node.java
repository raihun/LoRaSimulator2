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

    public String getOwnid() {
        return ownid;
    }

    // 各種シミュレート情報
    public int getRange() {
        return (sf + pwr) * 10;
    }

    // パケット送信
    public void sendPacket(String msg) {
        // 初期設定
        if(panid.equals("0000")) {
            setParameter(msg);
            return;
        }

        // 通常パケット
        this.child.send("OK");
        double range = this.getRange() / 2.0;
        ArrayList<Node> nodes = nc.getNodesByDistance(this, range);
        for(Node node : nodes) {
            node.receivePacket(msg);
        }
        return;
    }

    // パケット受信
    public void receivePacket(String msg) {
        this.child.send(msg);
        return;
    }
}
