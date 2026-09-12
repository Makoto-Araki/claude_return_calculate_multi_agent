# タスク一覧 - Kubernetes Deployment

> マルチエージェント並行実装では、`Dockerfile`・`k8s/namespace.yaml`・`k8s/deployment.yaml`の作成(項目1・3・4)は演算数に依存しないため基盤構築(Phase0)で先に行ってよい。一方、ローカルへのデプロイ・「4エンドポイントが応答することを確認する」(項目6〜8)は4演算すべてのPRがmainにマージされた後の統合確認(Phase2)で実施すること。詳細は[README.md](../../README.md)を参照。

- [ ] APIサーバー用の `Dockerfile` を作成する (Req 1)
- [ ] `calculator-api:local` イメージをローカルでビルドする (Req 1)
- [ ] `k8s/namespace.yaml` を `specs/deployment/design.md` の内容に従って作成する (Req 2)
- [ ] `k8s/deployment.yaml` を `specs/deployment/design.md` の内容に従って作成する(`namespace: calculator-api` を指定) (Req 1, 2, 3, 4, 5)
- [ ] Docker Desktopの Kubernetes に `kubectl apply -f k8s/namespace.yaml` でNamespaceを作成する (Req 2)
- [ ] `kubectl apply -f k8s/deployment.yaml` でDeploymentをデプロイする (Req 1)
- [ ] `kubectl get pods -n calculator-api` でPodが `calculator-api` Namespace上に `1` レプリカで起動していることを確認する (Req 2, 3)
- [ ] `kubectl port-forward -n calculator-api` 等でPodに接続し、4エンドポイントが応答することを確認する (Req 1)
