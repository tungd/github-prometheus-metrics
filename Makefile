deploy:
	rsync -avz --no-owner --no-group . root@sites:/var/www/code-metrics \
		--exclude=.git --exclude-from=.gitignore
	ssh root@sites cp /var/www/code-metrics/code-metrics.service /etc/systemd/system
	ssh root@sites systemctl daemon-reload
	ssh root@sites systemctl restart code-metrics

.PHONY: deploy
