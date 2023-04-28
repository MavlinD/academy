#!/bin/bash
set -euo pipefail

ENVIRONMENT_NAME=${CI_ENVIRONMENT_NAME:-'не определено'}

for CHAT_ID in $TELEGRAM_CHAT_ID_DEPLOY
do
    curl -F "text="$'\U00002728'" - Проект \`$CI_PROJECT_NAME\` окружение \`$ENVIRONMENT_NAME\` перезагружается.
Автор комита $CI_COMMIT_AUTHOR." "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage?chat_id=$CHAT_ID&parse_mode=markdown"

done
