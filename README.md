# LoRaSimulator2
ES920LR関連ライブラリ &amp; シミュレータ  

## 実行方法
- ノード側
    - LoraSimulator2ディレクトリで、python3 main.py <ノードID>  
    もしくは、make  
    ハードウェアを使う場合は、config.ini の simulator=falseに。  
    シミュレータを使う場合は、先にサーバを立ち上げ、simulator=trueに。  
- サーバ側
    - javac *.java -> java Main  
    もしくは、make  

## 動作確認環境
- Python3系
- Python3系プラグイン
    - pyserial
- Java 8
    - Java SE Development Kit (1.8.0_141)
