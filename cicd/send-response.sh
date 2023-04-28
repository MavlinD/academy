#!/bin/bash
set -euo pipefail

# env
ENVIRONMENT_NAME=${CI_ENVIRONMENT_NAME:-'не определено'}
# echo $ENVIRONMENT_NAME
# exit
for CHAT_ID in $TELEGRAM_CHAT_ID_ERR
do
    curl -F "text="$'\U0000203C'" - Конвейер проекта \`$CI_PROJECT_NAME\` окружение \`$ENVIRONMENT_NAME\` потерпел неудачу.
Автор комита $CI_COMMIT_AUTHOR." "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage?chat_id=$CHAT_ID&parse_mode=markdown"

done
