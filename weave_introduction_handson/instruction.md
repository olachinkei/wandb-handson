# 以下のファイルをupdateしたい
/Users/keisuke/Project/wandb-handson/weave_introduction_handson/weave_intro_notebook.ipynb

# 変更ポイント
- 推論をOpenAIからW&B Inferenceにしたい
    - サンプルコード: https://docs.wandb.ai/guides/inference/examples/ にある
    - model idはopenai/gpt-oss-20bにして
    - USE_AZURE_OPENAI = os.getenv("USE_AZURE_OPENAI", "false").lower() == "true" とか使わない
    - 推論に使うAPIはWANDB_API_KEY_PUBLIC_CLOUDとして
    - なお、Public cloudを使っている人は、WANDB_API_KEYと同じで良いというコメントを追加して
- 全て日本語にして (英語の方がわかりやすかったら英語のままで良いScoreとか)