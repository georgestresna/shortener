kubectl argo rollouts promote api -n shortener --full

kubectl apply -k infra/apps/shortener/base

kubectl argo rollouts get rollout api -n shortener --watch