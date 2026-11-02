kubectl argo rollouts promote api -n shortener --full
kubectl argo rollouts abort api -n shortener

kubectl apply -k infra/apps/shortener/base

kubectl argo rollouts get rollout api -n shortener --watch

kubectl port-forward -n monitoring svc/prometheus-server 9090:80 --address 0.0.0.0

kubectl port-forward -n monitoring svc/grafana 3000:80 --address 0.0.0.0

