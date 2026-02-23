#!/bin/bash
# Start backend in background
export CORS_ORIGINS="http://test.com,http://localhost:5173"
python -m uvicorn backend.main:app --port 8000 &
PID=$!
sleep 3

echo "--- Testing M1 (CORS) ---"
curl -v -X OPTIONS http://127.0.0.1:8000/rewards/ -H "Origin: http://test.com" -H "Access-Control-Request-Method: GET" 2>&1 | grep "Access-Control-Allow-Origin"

echo "--- Testing M3 (Create) ---"
REWARD_ID=$(curl -s -X POST "http://127.0.0.1:8000/rewards/" -H "Content-Type: application/json" -d '{"name": "Temp", "cost_points": 100, "description": "Delete me", "tier_level": 1}' | jq '.id')
echo "Created Reward ID: $REWARD_ID"

echo "--- Testing M3 (Update) ---"
curl -s -X PUT "http://127.0.0.1:8000/rewards/$REWARD_ID" -H "Content-Type: application/json" -d '{"name": "Temp Updated", "cost_points": 150}' | jq

echo "--- Testing M3 (Delete) ---"
curl -s -v -X DELETE "http://127.0.0.1:8000/rewards/$REWARD_ID"

kill $PID
wait $PID 2>/dev/null
echo "Tests done"
