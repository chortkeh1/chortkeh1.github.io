/*
 * Cloudflare Worker backend for Chortkeh AI assistant.
 * Keep OPENAI_API_KEY in Cloudflare Worker Secrets. Never commit the key here.
 */
const ALLOWED_ORIGINS = new Set([
  "https://chortkeh1.github.io"
]);

const SYSTEM_INSTRUCTIONS = `
تو دستیار هوشمند مؤسسه حسابداری و حسابرسی چرتکه در کرمان هستی.
به زبان فارسی روان، دقیق، محترمانه و کاربردی پاسخ بده.
حوزه‌ها: حسابداری، حسابرسی، مالیات ایران، اظهارنامه‌ها، بیمه و تأمین اجتماعی،
حقوق و دستمزد، مشاوره مالی، آموزش و نرم‌افزارهای حسابداری، انبارداری،
و خدمات مالی شرکت‌های معدنی، صنعتی و پیمانکاری.
اگر پرسش درباره قانون یا مهلت جاری است و منبع قطعی در دسترس نیست،
عدم قطعیت را شفاف بگو و شماره ماده/بخشنامه را حدس نزن.
برای پرونده‌های مالیاتی یا حقوقی، پاسخ را راهنمایی اولیه بدان و بررسی اسناد توسط متخصص را توصیه کن.
اطلاعات محرمانه مانند رمز، اطلاعات بانکی، کد ملی یا اسناد کامل را درخواست نکن.
اگر کاربر درخواست تماس انسانی دارد، شماره مؤسسه را 09131989006 اعلام کن.
پاسخ‌ها را تا حد امکان روشن، مرحله‌بندی‌شده و متناسب با سؤال بنویس.
`;

function corsHeaders(origin) {
  return {
    "Access-Control-Allow-Origin": ALLOWED_ORIGINS.has(origin) ? origin : "null",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Vary": "Origin"
  };
}

function json(data, status, origin) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
      ...corsHeaders(origin)
    }
  });
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";

    if (request.method === "OPTIONS") {
      if (!ALLOWED_ORIGINS.has(origin)) {
        return new Response(null, { status: 403 });
      }
      return new Response(null, {
        status: 204,
        headers: corsHeaders(origin)
      });
    }

    if (!ALLOWED_ORIGINS.has(origin)) {
      return json({ error: "origin_not_allowed" }, 403, origin);
    }

    if (request.method !== "POST") {
      return json({ error: "method_not_allowed" }, 405, origin);
    }

    if (!env.OPENAI_API_KEY) {
      return json({ error: "server_not_configured" }, 500, origin);
    }

    let body;
    try {
      body = await request.json();
    } catch {
      return json({ error: "invalid_json" }, 400, origin);
    }

    const message = typeof body.message === "string" ? body.message.trim() : "";
    if (!message) {
      return json({ error: "message_required" }, 400, origin);
    }
    if (message.length > 4000) {
      return json({ error: "message_too_long" }, 413, origin);
    }

    try {
      const apiResponse = await fetch("https://api.openai.com/v1/responses", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${env.OPENAI_API_KEY}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          model: "gpt-4.1-mini",
          instructions: SYSTEM_INSTRUCTIONS,
          input: message,
          max_output_tokens: 700,
          store: false
        })
      });

      const data = await apiResponse.json();

      if (!apiResponse.ok) {
        return json({
          error: "ai_provider_error",
          message: "سرویس هوش مصنوعی در حال حاضر پاسخ نداد. کمی بعد دوباره تلاش کنید."
        }, 502, origin);
      }

      let reply = typeof data.output_text === "string" ? data.output_text : "";
      if (!reply && Array.isArray(data.output)) {
        reply = data.output
          .filter(item => item.type === "message" && Array.isArray(item.content))
          .flatMap(item => item.content)
          .filter(part => part.type === "output_text")
          .map(part => part.text || "")
          .join("\n");
      }

      if (!reply.trim()) {
        return json({ error: "empty_ai_response" }, 502, origin);
      }

      return json({ reply: reply.trim() }, 200, origin);
    } catch (error) {
      return json({
        error: "upstream_unavailable",
        message: "ارتباط با سرویس هوش مصنوعی برقرار نشد. لطفاً دوباره تلاش کنید."
      }, 502, origin);
    }
  }
};
