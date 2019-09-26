deploy:
	rsync -avz --no-owner --no-group . root@sites:/var/www/code-metrics

.PHONY: deploy
