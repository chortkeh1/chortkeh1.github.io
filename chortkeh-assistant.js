/*
 * دستیار پاسخگوی چرتکه — رابط کاربری اولیه
 * این فایل فقط رابط کاربری و پاسخ‌های راهنمای نمونه را فراهم می‌کند.
 * برای پاسخ هوش مصنوعی واقعی، یک backend امن باید در CHAT_ENDPOINT تنظیم شود.
 */
(() => {
  if (window.__chortkehAssistantLoaded) return;
  window.__chortkehAssistantLoaded = true;

  const CONFIG = {
    title: "دستیار هوشمند چرتکه",
    subtitle: "راهنمای خدمات حسابداری و مالی",
    phone: "09131989006",
    // پس از راه‌اندازی backend امن، نشانی endpoint را اینجا قرار دهید.
    // مثال: https://your-worker.your-account.workers.dev/chat
    CHAT_ENDPOINT: ""
  };

  const css = `
  #chortkeh-chat-launcher{position:fixed;z-index:99998;bottom:22px;right:22px;border:0;border-radius:999px;background:#0f5f5a;color:#fff;padding:14px 19px;box-shadow:0 8px 28px #0003;font:600 15px Tahoma,Arial;cursor:pointer}
  #chortkeh-chat-panel{position:fixed;z-index:99999;bottom:82px;right:22px;width:min(370px,calc(100vw - 28px));height:min(560px,calc(100vh - 115px));display:none;flex-direction:column;background:#fff;border:1px solid #d8e4e1;border-radius:18px;box-shadow:0 12px 40px #0003;overflow:hidden;font:14px/1.8 Tahoma,Arial;color:#233}
  #chortkeh-chat-panel *{box-sizing:border-box}
  #chortkeh-chat-head{background:#0f5f5a;color:#fff;padding:15px;display:flex;align-items:center;gap:10px}
  #chortkeh-chat-head .mark{background:#d4af37;color:#173d39;border-radius:50%;width:38px;height:38px;display:grid;place-items:center;font-weight:bold;font-size:20px}
  #chortkeh-chat-head .headcopy{flex:1}
  #chortkeh-chat-head strong{display:block;font-size:15px}
  #chortkeh-chat-head small{color:#dcece8}
  #chortkeh-chat-close{border:0;background:transparent;color:white;font-size:25px;cursor:pointer}
  #chortkeh-chat-messages{flex:1;overflow:auto;padding:14px;background:#f7faf9}
  .chortkeh-msg{max-width:90%;padding:10px 12px;margin:0 0 10px;border-radius:13px;white-space:pre-wrap;overflow-wrap:anywhere}
  .chortkeh-msg.bot{background:#fff;border:1px solid #e0e9e6;margin-left:auto}
  .chortkeh-msg.user{background:#dcefeb;margin-right:auto}
  #chortkeh-chat-quick{display:flex;flex-wrap:wrap;gap:6px;padding:8px 12px;background:#fff;border-top:1px solid #e5ece9}
  #chortkeh-chat-quick button{background:#fff;border:1px solid #b8d2cc;color:#0f5f5a;border-radius:18px;padding:6px 9px;font:12px Tahoma;cursor:pointer}
  #chortkeh-chat-form{display:flex;gap:7px;padding:10px;border-top:1px solid #e5ece9;background:#fff}
  #chortkeh-chat-input{min-width:0;flex:1;border:1px solid #cbdad6;border-radius:12px;padding:10px;font:14px Tahoma;direction:rtl}
  #chortkeh-chat-send{border:0;border-radius:12px;background:#0f5f5a;color:#fff;padding:0 15px;font:600 14px Tahoma;cursor:pointer}
  #chortkeh-chat-note{font-size:10px;color:#687b76;padding:0 12px 8px;background:#fff}
  @media(max-width:480px){#chortkeh-chat-launcher{right:14px;bottom:14px}#chortkeh-chat-panel{right:10px;bottom:72px;width:calc(100vw - 20px);height:min(72vh,600px)}}
  `;
  const style = document.createElement("style");
  style.textContent = css;
  document.head.appendChild(style);

  const launcher = document.createElement("button");
  launcher.id = "chortkeh-chat-launcher";
  launcher.type = "button";
  launcher.textContent = "💬 گفت‌وگو با چرتکه";
  launcher.setAttribute("aria-label", "باز کردن دستیار هوشمند چرتکه");

  const panel = document.createElement("section");
  panel.id = "chortkeh-chat-panel";
  panel.setAttribute("aria-label", CONFIG.title);
  panel.innerHTML = `
    <div id="chortkeh-chat-head">
      <div class="mark">چ</div>
      <div class="headcopy"><strong>${CONFIG.title}</strong><small>${CONFIG.subtitle}</small></div>
      <button id="chortkeh-chat-close" type="button" aria-label="بستن">×</button>
    </div>
    <div id="chortkeh-chat-messages" aria-live="polite"></div>
    <div id="chortkeh-chat-quick">
      <button type="button" data-q="services">خدمات مؤسسه</button>
      <button type="button" data-q="tax">مالیات</button>
      <button type="button" data-q="industry">شرکت‌های معدنی و صنعتی</button>
      <button type="button" data-q="contact">درخواست تماس</button>
    </div>
    <form id="chortkeh-chat-form">
      <input id="chortkeh-chat-input" maxlength="1500" autocomplete="off" placeholder="سؤال خود را بنویسید..." aria-label="متن پیام">
      <button id="chortkeh-chat-send" type="submit">ارسال</button>
    </form>
    <div id="chortkeh-chat-note">پاسخ‌های عمومی جایگزین بررسی اسناد توسط کارشناس نیستند.</div>
  `;
  document.body.append(launcher, panel);

  const messages = panel.querySelector("#chortkeh-chat-messages");
  const input = panel.querySelector("#chortkeh-chat-input");
  const form = panel.querySelector("#chortkeh-chat-form");

  function addMessage(text, who) {
    const el = document.createElement("div");
    el.className = "chortkeh-msg " + who;
    el.textContent = text;
    messages.appendChild(el);
    messages.scrollTop = messages.scrollHeight;
  }

  function showWelcome() {
    if (messages.childElementCount) return;
    addMessage("سلام! به مؤسسه حسابداری و حسابرسی چرتکه خوش آمدید.\n\nمی‌توانم درباره خدمات حسابداری، حسابرسی، مالیات، بیمه و تأمین اجتماعی، آموزش حسابداری و خدمات مالی شرکت‌های معدنی و صنعتی راهنمایی اولیه بدهم. چه کمکی از دستم برمی‌آید؟", "bot");
  }

  const faq = [
    {keys:["خدمات","حسابداری","حسابرسی","خدمت"], answer:"خدمات مؤسسه چرتکه شامل حسابداری و امور مالی، حسابرسی، خدمات مالیاتی و اظهارنامه، بیمه و تأمین اجتماعی، مشاوره مالی، آموزش حسابداری و راهنمایی درباره سیستم‌های حسابداری و انبارداری است. برای تعیین دامنه و هزینه خدمات، اطلاعات شرکت باید توسط کارشناس بررسی شود."},
    {keys:["مالیات","اظهارنامه","تبصره","ماده"], answer:"برای راهنمایی مالیاتی دقیق، نوع مؤدی (شخص حقیقی یا حقوقی)، سال مالیاتی و موضوع پرونده مهم است. قوانین و مهلت‌ها ممکن است تغییر کنند؛ بنابراین این پاسخ عمومی است و برای تصمیم یا دفاعیه نهایی باید مستندات و مقررات معتبر همان سال بررسی شود."},
    {keys:["بیمه","تامین اجتماعی","تأمین اجتماعی","لیست بیمه","حقوق"], answer:"در امور بیمه و تأمین اجتماعی می‌توانیم راهنمایی اولیه درباره لیست بیمه، حقوق و دستمزد و مسائل کارفرمایی ارائه کنیم. برای بررسی پرونده یا محاسبات، لطفاً نوع موضوع و بازه زمانی را مشخص کنید و اطلاعات هویتی یا محرمانه را در این گفت‌وگو ارسال نکنید."},
    {keys:["معدن","معدنی","صنعتی","پیمانکاری","کارخانه"], answer:"برای شرکت‌های معدنی، صنعتی و پیمانکاری، خدمات می‌تواند شامل استقرار یا بررسی سیستم حسابداری، بهای تمام‌شده، کنترل موجودی، گزارش‌های مدیریتی، مالیات و رسیدگی به اسناد باشد. نوع فعالیت و نیاز اصلی شرکت را بفرمایید تا مسیر مناسب را مشخص کنیم."},
    {keys:["آموزش","دوره","نرم افزار","نرم‌افزار"], answer:"مؤسسه در حوزه آموزش حسابداری و راهنمایی درباره سیستم‌های حسابداری، انبارداری و حضور و غیاب فعالیت دارد. لطفاً سطح آموزش یا نوع نرم‌افزار موردنظر را بنویسید تا راهنمایی دقیق‌تری بدهم."},
    {keys:["تماس","تلفن","مشاوره","همکاری","درخواست","پیشنهاد","شکایت"], answer:"برای پیگیری انسانی می‌توانید با شماره همراه مؤسسه 09131989006 تماس بگیرید. لطفاً در پیام خود فقط موضوع درخواست و زمان مناسب تماس را بنویسید. اطلاعات مالی، کد ملی، رمز عبور یا اسناد محرمانه را در این پنجره وارد نکنید."}
  ];

  function localAnswer(text) {
    const t = text.toLowerCase().replace(/ي/g,"ی").replace(/ك/g,"ک");
    for (const item of faq) if (item.keys.some(k => t.includes(k))) return item.answer;
    return "برای اینکه راهنمایی درستی بدهم، لطفاً موضوع را کمی دقیق‌تر توضیح دهید؛ مثلاً حسابداری، مالیات، بیمه، حسابرسی، آموزش یا درخواست تماس. این نسخه اولیه هنوز به موتور هوش مصنوعی متصل نیست؛ برای پرسش‌های آزاد و پاسخ‌های تخصصی باید backend امن فعال شود.";
  }

  async function answer(text) {
    if (!CONFIG.CHAT_ENDPOINT) return localAnswer(text);
    const response = await fetch(CONFIG.CHAT_ENDPOINT, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({message:text, page:location.href, language:"fa"})
    });
    if (!response.ok) throw new Error("chat endpoint error");
    const data = await response.json();
    return data.reply || "در حال حاضر امکان پاسخگویی وجود ندارد. لطفاً با مؤسسه تماس بگیرید.";
  }

  launcher.addEventListener("click", () => {
    panel.style.display = "flex";
    launcher.style.display = "none";
    showWelcome();
    input.focus();
  });
  panel.querySelector("#chortkeh-chat-close").addEventListener("click", () => {
    panel.style.display = "none";
    launcher.style.display = "block";
  });

  panel.querySelectorAll("[data-q]").forEach(btn => btn.addEventListener("click", async () => {
    const queries = {
      services:"خدمات مؤسسه چرتکه چیست؟",
      tax:"برای خدمات مالیاتی و اظهارنامه چه کمکی می‌کنید؟",
      industry:"برای شرکت‌های معدنی و صنعتی چه خدماتی دارید؟",
      contact:"می‌خواهم درخواست تماس ثبت کنم."
    };
    input.value = queries[btn.dataset.q];
    form.requestSubmit();
  }));

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const text = input.value.trim();
    if (!text) return;
    addMessage(text, "user");
    input.value = "";
    const wait = document.createElement("div");
    wait.className = "chortkeh-msg bot";
    wait.textContent = "در حال آماده‌سازی پاسخ…";
    messages.appendChild(wait);
    try {
      const reply = await answer(text);
      wait.textContent = reply;
    } catch (e) {
      wait.textContent = "در حال حاضر اتصال پاسخگویی در دسترس نیست. لطفاً با شماره 09131989006 تماس بگیرید.";
    }
    messages.scrollTop = messages.scrollHeight;
  });
})();
