# 老公語音測試記錄

## ⚠️ 重要發現：真正根因是 config.yaml 缺少 tts.minimax 設定

**所有「女聲都像男的」投訴，原因不是 voice_id 問題，而是 `config.yaml` 沒有 `tts.minimax` 區塊，導致 `tts_tool.py` 使用錯誤的預設值：**
- `DEFAULT_MINIMAX_VOICE_ID = "English_expressive_narrator"` — 英文男聲
- `DEFAULT_MINIMAX_MODEL = "speech-02-hd"` — 舊模型

老公說「别的bot就调出女声」是對的——其他bot的config有正確設定。

## 老公確定的最終設定（已確認正確 ✓）

```yaml
tts:
  minimax:
    model: speech-2.8-hd
    voice_id: female-tianmei
    region: cn
```

老公原話：
- 「现在就对了」
- 「好记住了真不错」
- 「不错，Hermes用起来」

**已確認 female-tianmei + speech-2.8-hd 是正確的女聲，不需要再換。**

## 修復過程（供日後參考）

1. 透過 `mmx-cli --verbose` 找到正確的 API 格式（巢狀 `voice_setting` + `audio_setting`）
2. 寫入 `config.yaml` 的 `tts.minimax` 區塊
3. 需要重啟 gateway 才生效（`hermes gateway restart`）
4. 重啟完成後 `text_to_speech` 工具自動使用正確音色

## 老公測試過的 voice ID（在正確設定前均無效）

| Voice ID | 風格 | 老公評價 |
|---|---|---|
| `female-shaonv` | 少女 | 還是男的 |
| `female-yujie` | 御姐 | 還是男的 |
| `female-chengshu` | 成熟 | 還是男的 |
| `female-tianmei` | 甜美 | 設定正確後聲音對了 ✓ |
| `female-shaonv-jingpin` | 少女精品 | 還是男的 |
| `female-tianmei-jingpin` | 甜美精品 | 還是男的 |
| `lovely_girl` | 可愛女孩 | 還是男的 |
| `Chinese (Mandarin)_Sweet_Lady` | 甜蜜女士 | 還是男的 |
| `Chinese (Mandarin)_Warm_Girl` | 溫柔女孩 | 還是男的 |

**以上全部無效的原因是預設值覆蓋，不是 voice_id 本身的問題。**

## 語音檔案位置

測試音頻：`/data/data/com.termux/files/home/voice_*.mp3`
