import java.awt.*;
import javax.swing.*;

public class Progress extends Thread {

    private static Screen screen = null;
    private boolean running = false;

    // コンストラクタ
    public Progress() {
        this.running = true;
    }

    // インスタンス
    public void setScreen(Screen screen) {
        this.screen = screen;
    }

    // スレッド操作
    public void finish() {
        running = false;
    }

    @Override
    public void run() {
        while(running) {
            try {
                screen.render();
            } catch(Exception e) {
                e.printStackTrace();
            }

            try {
                Thread.sleep(1);
            } catch(InterruptedException e) {}
        }
    }

}
