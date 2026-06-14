export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // 处理跨域 (CORS) 预检请求
    if (request.method === "OPTIONS") {
      return handleCORS();
    }

    // 路由：获取模型列表 (GET /v1/models)
    if (request.method === "GET" && url.pathname.endsWith("/v1/models")) {
      return new Response(JSON.stringify(dummyModels), {
        status: 200,
        headers: {
          "Content-Type": "application/json",
          ...corsHeaders
        }
      });
    }

    // 路由：聊天请求 (POST /v1/chat/completions)
    if (request.method === "POST" && url.pathname.endsWith("/v1/chat/completions")) {
      
      // --- 新增：Log 请求参数 ---
      try {
        // 克隆请求以读取 Body（如果是为了转发请求，建议先 clone，这里直接读取也可以）
        const requestData = await request.json();
        console.log("收到聊天请求参数:", JSON.stringify(requestData, null, 2));
      } catch (err) {
        console.log("读取请求体失败或 Body 为空:", err.message);
      }
      // -----------------------

      // 模拟 New API 常见的 502 上游错误
      const errorResponse = {
        error: {
          message: "上游服务器超时或连接失败 (Simulated New API Error)",
          type: "new_api_error",
          param: "upstream_service",
          code: "bad_gateway"
        }
      };

      return new Response(JSON.stringify(errorResponse), {
        status: 502, // 模拟 502 错误
        headers: {
          "Content-Type": "application/json",
          ...corsHeaders
        }
      });
    }

    // 其他路径返回 404
    return new Response(JSON.stringify({ error: "Not Found" }), { 
      status: 404,
      headers: { "Content-Type": "application/json", ...corsHeaders }
    });
  }
};

// --- 配置数据 ---

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
};

function handleCORS() {
  return new Response(null, {
    status: 204,
    headers: corsHeaders
  });
}

const dummyModels = {
  "object": "list",
  "data": [
    {
      "id": "gpt-3.5-turbo",
      "object": "model",
      "created": 1677610602,
      "owned_by": "openai"
    },
    {
      "id": "gpt-4",
      "object": "model",
      "created": 1687882411,
      "owned_by": "openai"
    },
    {
      "id": "claude-3-sonnet",
      "object": "model",
      "created": 1710000000,
      "owned_by": "anthropic"
    }
  ]
};