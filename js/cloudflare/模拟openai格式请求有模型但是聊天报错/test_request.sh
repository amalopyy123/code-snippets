curl -X POST http://127.0.0.1:4100/v1/chat/completions \
-H "Content-Type: application/json" \
-H "Authorization: Bearer sk-5fh62hpT6RfUz42jeK1FExqJyOicVO6TjRRRh1o6rDWglOlI" \
-d '{
  "model": "gpt-3.5-turbo",
  "messages": [
    {
      "role": "user",
      "content": "你好，这是一条带 Token 的测试消息"
    }
  ],
  "temperature": 0.7
}'