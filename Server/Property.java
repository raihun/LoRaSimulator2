import java.io.IOException;
import java.io.File;
import java.io.FileOutputStream;
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.Locale;
import java.util.MissingResourceException;
import java.util.Properties;
import java.util.ResourceBundle;

public class Property {

    private String filename = "position";
    private String fullname = "position.properties";
    private static NodeController nc;

    public void setNodeController(NodeController nc) {
        this.nc = nc;
    }

    public void savePosition() {
        Properties properties = new Properties();

        // 現在の座標を保存
        ArrayList<Node> nodeList = nc.getNodes();
        for(Node node : nodeList) {
            int[] pos = node.getPosition();
            String value = String.format("%d,%d", pos[0], pos[1]);
            try {
                properties.setProperty(node.getOwnid(), value);
                properties.store(new FileOutputStream(fullname), "Node Position");
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    public void loadPosition() {
        // ファイル存在チェック
        File file = new File(fullname);
        if (!file.exists()){
            return;
        }

        // 取得
        ResourceBundle rb = null;
        try {
            rb = ResourceBundle.getBundle(
                filename,
                new ResourceBundle.Control() {
                    public long getTimeToLive(String baseName, Locale locale) {
                        return 3000;  // 3秒ごとにファイルを再ロード
                	}
                }
            );
        } catch (MissingResourceException e) {
            e.printStackTrace();
            return;
        }

        // ポジションセット
        ArrayList<Node> nodeList = nc.getNodes();

        Enumeration <String>enu = rb.getKeys();
        while(enu.hasMoreElements()) {
            String key = enu.nextElement();
            for(Node node : nodeList) {
                String ownid = node.getOwnid();
                if(ownid.equals(key)) {
                    String value = rb.getString(key);
                    String[] pos = value.split(",");
                    int x = Integer.parseInt(pos[0]);
                    int y = Integer.parseInt(pos[1]);
                    node.setPosition(x, y);
                    break;
                }

            }
        }

        // 終了
        rb = null;
    }
}
