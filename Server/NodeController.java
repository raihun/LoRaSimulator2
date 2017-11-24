import java.util.ArrayList;

public class NodeController {

    private ArrayList<Node> nodeList;
    private int coundId = 0;

    // コンストラクタ
    public NodeController() {
        this.nodeList = new ArrayList<Node>();
    }

    // ノード追加
    public Node addNode(int x, int y) {
        Node node = new Node(x, y);
        node.setNodeController(this);
        nodeList.add(node);
        return node;
    }

    // ノード削除
    public boolean removeNode(int x, int y) {
        // ノード数チェック
        if(nodeList.size() < 1) return false;

        // 距離確認
        ArrayList<Node> removeNodeList = new ArrayList<Node>();
        for(Node node : nodeList) {
            int[] pos = node.getPosition();
            double distance = Math.sqrt(Math.pow(x - pos[0], 2) + Math.pow(y - pos[1], 2));
            if(distance < 5.0) removeNodeList.add(node);
        }

        // 削除リストから削除
        for(Node node : removeNodeList) {
            nodeList.remove(nodeList.indexOf(node));
        }
        return true;
    }

    //　ノード取得 (All)
    public ArrayList<Node> getNodes() {
        return nodeList;
    }

    // ノード取得 (by Distance)
    public ArrayList<Node> getNodesByDistance(Node node, double distance) {
        ArrayList<Node> result = new ArrayList<Node>();
        for(Node _node : nodeList) {
            if(node == _node) continue; // 対象ノードは含めない
            if(getDistance(node, _node) <= distance) {
                result.add(_node);
            }
        }

        // 返却
        return result;
    }

    public ArrayList<Node> getNodesByPosition(int x, int y, double targetDistance) {
        // 距離確認
        ArrayList<Node> selectNodeList = new ArrayList<Node>();
        for(Node node : this.nodeList) {
          int[] pos = node.getPosition();
          double distance = Math.sqrt(Math.pow(x - pos[0], 2) + Math.pow(y - pos[1], 2));
          if(distance < targetDistance) selectNodeList.add(node);
        }
        return selectNodeList;
    }

    // ノード間の距離算出
    public double getDistance(Node nodeA, Node nodeB) {
        int[] posA = nodeA.getPosition();
        int[] posB = nodeB.getPosition();
        return Math.sqrt(Math.pow(posA[0] - posB[0], 2) + Math.pow(posA[1] - posB[1], 2));
    }

    // LoRaパラメータ面での接続可能かチェック
    public Boolean checkConnectivity(Node nodeA, Node nodeB, Boolean checkPanid) {
        Boolean result = true;

        // Bandwidth チェック
        if(nodeA.getBandwidth() != nodeB.getBandwidth()) {
            result = false;
        }
        // Spread Factor チェック
        if(nodeA.getSpreadfactor() != nodeB.getSpreadfactor()) {
            result = false;
        }
        // Channel チェック
        if(nodeA.getChannel() != nodeB.getChannel()) {
            result = false;
        }
        // PAN ID チェック
        if((nodeA.getPanid() != nodeB.getPanid()) && checkPanid) {
            result = false;
        }

        return result;
    }
}
