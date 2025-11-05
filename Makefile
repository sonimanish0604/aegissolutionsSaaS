# Makefile
NS_AEGIS = aegis
NS_OBS   = observability
NS_ISTIO = istio-system

PF_DIR   = .pf
SHELL    := /bin/bash

define run_pf
	@mkdir -p $(PF_DIR)
	@echo "🔌 port-forward: $(1)"
	@bash -lc 'nohup kubectl -n $(2) port-forward $(3) $(4) >/dev/null 2>&1 & echo $$! > $(PF_DIR)/$(1).pid'
endef

dev-up:
	@echo "🚀 Checking cluster..."
	@kubectl get pods -A >/dev/null
	$(call run_pf,onboarding,$(NS_AEGIS),svc/onboarding-service,8000:8080)
	$(call run_pf,pg,$(NS_AEGIS),pod/pg-postgresql-0,15432:5432)
	$(call run_pf,grafana,$(NS_OBS),svc/grafana,3000:80)
	$(call run_pf,prometheus,$(NS_OBS),svc/prometheus-kps-kube-prometheus-stack-prometheus,9090:9090)
	$(call run_pf,tempo,$(NS_OBS),svc/tempo-query-frontend,3200:3200)
	$(call run_pf,loki,$(NS_OBS),svc/loki,3100:3100)
	$(call run_pf,istio,$(NS_ISTIO),svc/istio-ingressgateway,8081:80)
	@echo "✅ Forwards up. Try:"
	@echo "   API:      http://localhost:8000/docs"
	@echo "   Postgres: localhost:15432 (Adminer/psql)"
	@echo "   Grafana:  http://localhost:3000"
	@echo "   Prom:     http://localhost:9090"
	@echo "   Tempo:    http://localhost:3200"
	@echo "   Loki:     http://localhost:3100"
	@echo "   Istio GW: http://localhost:8081"

dev-down:
	@echo "🛑 Killing port-forwards..."
	@for f in $(PF_DIR)/*.pid; do \
		[ -f $$f ] && kill -9 $$(cat $$f) 2>/dev/null || true ; \
	done
	@rm -rf $(PF_DIR)
	@echo "✅ Done."

dev-status:
	@echo "🔎 Active PIDs:" ; ls -1 $(PF_DIR)/*.pid 2>/dev/null || echo "(none)"

#usage
#make dev-up     # starts all forwards in background (survive until you run dev-down)
#make dev-status # shows which are running
#make dev-down   # stops them
#

