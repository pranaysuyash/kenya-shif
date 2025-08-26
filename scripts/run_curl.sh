#!/usr/bin/env bash
set -euo pipefail
MODEL="gpt-5-mini"
if [ -z "${OPENAI_API_KEY:-}" ]; then echo "Missing OPENAI_API_KEY"; exit 1; fi
# Contradictions
curl -sS https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer ${OPENAI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"model\": \"${MODEL}\", \"temperature\": 0.2, \"messages\": [{\"role\": \"user\", \"content\": $(jq -Rs '.' < prompts/contradictions.txt) }]}" \
  | tee outputs/ai_contradictions.json >/dev/null
# Gaps
curl -sS https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer ${OPENAI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"model\": \"${MODEL}\", \"temperature\": 0.2, \"messages\": [{\"role\": \"user\", \"content\": $(jq -Rs '.' < prompts/gaps.txt) }]}" \
  | tee outputs/ai_gaps.json >/dev/null
