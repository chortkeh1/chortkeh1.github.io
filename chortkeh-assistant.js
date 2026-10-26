
/*
 * دستیار پاسخگوی مؤسسه حسابداری و حسابرسی چرتکه
 * نسخه اصلاح‌شده رابط کاربری
 */
(() => {
  if (window.__chortkehAssistantLoaded) return;
  window.__chortkehAssistantLoaded = true;

  const CONFIG = {
    title: "دستیار هوشمند چرتکه",
    subtitle: "راهنمای خدمات حسابداری و مالی",
    phone: "09131989006",
    CHAT_ENDPOINT: ""
  };

  const css = `
  #chortkeh-chat-launcher {
    position: fixed;
    z-index: 99998;
    bottom: 22px;
    right: 22px;
    border: 0;
    border-radius: 999px;
    background: #0f5f5a;
    color: #fff;
    padding: 12px 17px;
    box-shadow: 0 8px 28px #0003;
    font: 600 15px Tahoma, Arial, sans-serif;
    cursor: pointer;
  }

  #chortkeh-chat-panel {
    position: fixed;
    z-index: 99999;
    bottom: 82px;
    right: 22px;
    width: min(370px, calc(100vw - 28px));
    height: min(560px, calc(100vh - 115px));
    display: none;
    flex-direction: column;
    background: #fff;
    border: 1px solid #d8e4e1;
    border-radius: 16px;
    box-shadow: 0 12px 40px #0003;
    overflow: hidden;
    font: 14px/1.7 Tahoma, Arial, sans-serif;
    color: #233;
    direction: rtl;
  }

  #chortkeh-chat-panel *,
  #chortkeh-chat-panel *::before,
  #chortkeh-chat-panel *::after {
    box-sizing: border-box;
  }

  /* هدر و عنوان */
  #chortkeh-chat-head {
    flex: 0 0 auto;
    height: 58px;
    min-height: 58px;
    background: #0f5f5a;
    color: #fff;
    padding: 5px 12px;
    display: flex;
    align-items: center;
    gap: 9px;
    overflow: hidden;
  }

  /* آواتار تصویری خانم */
  #chortkeh-chat-head .mark {
    flex: 0 0 38px;
    width: 38px;
    height: 38px;
    border-radius: 50%;
    overflow: hidden;
    background: #d4af37;
    border: 2px solid #e8d58b;
    display: grid;
    place-items: center;
  }

  #chortkeh-chat-head .mark svg {
    display: block;
    width: 100%;
    height: 100%;
  }

  /* عنوان کمی بالاتر قرار می‌گیرد */
  #chortkeh-chat-head .headcopy {
    flex: 1;
    min-width: 0;
    transform: translateY(-7px);
  }

  #chortkeh-chat-head strong {
    display: block;
    font-size: 14px;
    line-height: 1.6;
    white-space: nowrap;
  }

  #chortkeh-chat-head small {
    display: block;
    color: #dcece8;
    font-size: 11px;
    line-height: 1.5;
    white-space: nowrap;
  }

  #chortkeh-chat-close {
    flex: 0 0 auto;
    border: 0;
    background: transparent;
    color: white;
    font-size: 25px;
    line-height: 1;
    padding: 3px 5px;
    cursor: pointer;
    align-self: flex-start;
  }

  /* بخش پیام‌ها بیشترین فضای ممکن را می‌گیرد */
  #chortkeh-chat-messages {
    flex: 1 1 0;
    min-height: 0;
    overflow-y: auto;
    overscroll-behavior: contain;
    padding: 10px;
    background: #f7faf9;
    direction: rtl;
  }

  .chortkeh-msg {
    max-width: 100%;
    padding: 9px 11px;
    margin: 0 0 8px;
    border-radius: 12px;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    line-height: 1.9;
    font-size: 13px;
  }

  .chortkeh-msg.bot {
    background: #fff;
    border: 1px solid #e0e9e6;
  }

  .chortkeh-msg.user {
    background: #dcefeb;
  }

  /* دکمه‌های راهنما */
  #chortkeh-chat-quick {
    flex: 0 0 auto;
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    padding: 6px 9px;
    background: #fff;
    border-top: 1px solid #e5ece9;
  }

  #chortkeh-chat-quick button {
    background: #fff;
    border: 1px solid #b8d2cc;
    color: #0f5f5a;
    border-radius: 16px;
    padding: 5px 8px;
    font: 11px Tahoma, Arial, sans-serif;
    line-height: 1.5;
    cursor: pointer;
  }

  /* قسمت ارسال پیام کمی پایین‌تر تنظیم می‌شود */
  #chortkeh-chat-form {
    flex: 0 0 auto;
    display: flex;
    align-items: stretch;
    gap: 6px;
    padding: 7px 9px 7px;
    border-top: 1px solid #e5ece9;
    background: #fff;
    position: relative;
    top: 3px;
  }

  #chortkeh-chat-input {
    min-width: 0;
    width: 0;
    flex: 1 1 auto;
    border: 1px solid #cbdad6;
    border-radius: 10px;
    padding: 9px;
    font: 13px Tahoma, Arial, sans-serif;
    direction: rtl;
    outline-color: #0f5f5a;
  }

  #chortkeh-chat-send {
    flex: 0 0 auto;
    border: 0;
    border-radius: 10px;
    background: #0f5f5a;
    color: #fff;
    padding: 0 12px;
    font: 600 13px Tahoma, Arial, sans-serif;
    cursor: pointer;
  }

  #chortkeh-chat-send:disabled {
    opacity: 0.6;
    cursor: wait;
  }

  #chortkeh-chat-note {
    flex: 0 0 auto;
    font-size: 9px;
    line-height: 1.5;
    color: #687b76;
    padding: 4px 10px 5px;
    background: #fff;
  }

  #chortkeh-chat-panel button:focus-visible,
  #chortkeh-chat-panel input:focus-visible,
  #chortkeh-chat-launcher:focus-visible {
    outline: 2px solid #d4af37;
    outline-offset: 2px;
  }

  @media (max-width: 480px) {
    #chortkeh-chat-launcher {
      right: 14px;
      bottom: 14px;
    }

    #chortkeh-chat-panel {
      right: 10px;
      bottom: 72px;
      width: calc(100vw - 20px);
      height: min(560px, calc(100vh - 88px));
      height: min(560px, calc(100dvh - 88px));
      border-radius: 14px;
    }

    #chortkeh-chat-head {
      height: 58px;
      min-height: 58px;
    }

    #chortkeh-chat-messages {
      padding: 9px;
    }
  }

  @media (max-height: 520px) {
    #chortkeh-chat-panel {
      height: calc(100vh - 92px);
      height: calc(100dvh - 92px);
      bottom: 72px;
    }

    #chortkeh-chat-head {
      height: 48px;
      min-height: 48px;
    }
  }
  `;

  const style = document.createElement("style");
  style.textContent = css;
  document.head.appendChild(style);

  const launcher = document.createElement("button");
  launcher.id = "chortkeh-chat-launcher";
  launcher.type = "button";
  launcher.textContent = "💬 گفت‌وگو با چرتکه";
  launcher.setAttribute(
    "aria-label",
    "باز کردن دستیار هوشمند چرتکه"
  );

  const panel = document.createElement("section");
  panel.id = "chortkeh-chat-panel";
  panel.setAttribute("aria-label", CONFIG.title);
  panel.setAttribute("aria-hidden", "true");

  panel.innerHTML = `
    <div id="chortkeh-chat-head">
      <div class="mark" role="img" aria-label="آواتار دستیار خانم">
        <svg viewBox="0 0 100 100"
             xmlns="http://www.w3.org/2000/svg"
             aria-hidden="true">
          <defs>
            <clipPath id="chortkeh-avatar-clip">
              <circle cx="50" cy="50" r="49"/>
            </clipPath>
            <linearGradient id="chortkeh-avatar-bg"
                            x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stop-color="#f7e8c1"/>
              <stop offset="100%" stop-color="#d4af37"/>
            </linearGradient>
          </defs>
          <g clip-path="url(#chortkeh-avatar-clip)">
            <rect width="100" height="100"
                  fill="url(#chortkeh-avatar-bg)"/>
            <path d="M19 103 L22 79 Q26 68 39 65
                     L61 65 Q76 68 80 80 L83 103"
                  fill="#0f5f5a"/>
            <path d="M35 61 L35 73 Q50 86 65 73
                     L65 61" fill="#e8b18e"/>
            <path d="M27 43 Q20 11 50 10
                     Q80 11 74 48 L70 63
                     Q64 78 50 79 Q35 77 29 61 Z"
                  fill="#49332e"/>
            <path d="M32 40 Q33 22 50 22
                     Q68 22 69 43 L66 55
                     Q62 67 50 69 Q38 67 34 55 Z"
                  fill="#f0bd98"/>
            <path d="M29 43 Q23 21 39 13
                     Q56 2 71 18 Q81 29 73 49
                     L68 37 Q61 31 58 24
                     Q49 35 33 35 L32 52 Z"
                  fill="#49332e"/>
            <path d="M40 43 Q45 40 48 43"
                  fill="none" stroke="#49332e"
                  stroke-width="2.5" stroke-linecap="round"/>
            <path d="M54 43 Q59 40 63 43"
                  fill="none" stroke="#49332e"
                  stroke-width="2.5" stroke-linecap="round"/>
            <circle cx="44" cy="47" r="2"
                    fill="#302723"/>
            <circle cx="59" cy="47" r="2"
                    fill="#302723"/>
            <path d="M48 54 Q51 57 54 54"
                  fill="none" stroke="#bd806c"
                  stroke-width="1.8" stroke-linecap="round"/>
            <path d="M43 61 Q50 66 58 61"
                  fill="none" stroke="#a54e4c"
                  stroke-width="2.4" stroke-linecap="round"/>
            <path d="M40 72 L50 82 L60 72"
                  fill="#fff"/>
            <path d="M40 72 L50 82 L60 72 L65 100 L35 100 Z"
                  fill="#0f5f5a"/>
          </g>
        </svg>
      </div>
      <div class="headcopy">
        <strong>${CONFIG.title}</strong>
        <small>${CONFIG.subtitle}</small>
      </div>
      <button id="chortkeh-chat-close"
              type="button" aria-label="بستن">×</button>
    </div>

    <div id="chortkeh-chat-messages"
         aria-live="polite"></div>

    <div id="chortkeh-chat-quick">
      <button type="button" data-q="services">خدمات مؤسسه</button>
      <button type="button" data-q="tax">مالیات</button>
      <button type="button" data-q="industry">شرکت‌های معدنی و صنعتی</button>
      <button type="button" data-q="contact">درخواست تماس</button>
    </div>

    <form id="chortkeh-chat-form">
      <input id="chortkeh-chat-input"
             maxlength="1500"
             autocomplete="off"
             placeholder="سؤال خود را بنویسید..."
             aria-label="متن پیام">
      <button id="chortkeh-chat-send" type="submit">ارسال</button>
    </form>

    <div id="chortkeh-chat-note">
      پاسخ‌های عمومی جایگزین بررسی اسناد توسط کارشناس نیستند.
    </div>
  `;

  document.body.append(launcher, panel);

  const messages = panel.querySelector("#chortkeh-chat-messages");
  const input = panel.querySelector("#chortkeh-chat-input");
  const form = panel.querySelector("#chortkeh-chat-form");
  const sendButton = panel.querySelector("#chortkeh-chat-send");

  function addMessage(text, who) {
    const el = document.createElement("div");
    el.className = "chortkeh-msg " + who;
    el.textContent = text;
    messages.appendChild(el);
    messages.scrollTop = messages.scrollHeight;
    return el;
  }

  function showWelcome() {
    if (messages.childElementCount) return;

    addMessage(
      "سلام! به مؤسسه حسابداری و حسابرسی چرتکه خوش آمدید.\n\n" +
      "می‌توانم درباره خدمات حسابداری، حسابرسی، مالیات، " +
      "بیمه و تأمین اجتماعی، آموزش حسابداری و خدمات مالی " +
      "شرکت‌های معدنی و صنعتی راهنمایی اولیه بدهم.\n\n" +
      "چه کمکی از دستم برمی‌آید؟",
      "bot"
    );
  }

  const faq = [
    {
      keys: ["خدمات", "حسابداری", "حسابرسی", "خدمت"],
      answer:
        "خدمات مؤسسه چرتکه شامل حسابداری و امور مالی، حسابرسی، " +
        "خدمات مالیاتی و اظهارنامه، بیمه و تأمین اجتماعی، " +
        "مشاوره مالی، آموزش حسابداری و راهنمایی درباره سیستم‌های " +
        "حسابداری و انبارداری است.\n\n" +
        "برای تعیین دامنه خدمات، اطلاعات شرکت باید توسط کارشناس بررسی شود."
    },
    {
      keys: ["مالیات", "اظهارنامه", "تبصره", "ماده"],
      answer:
        "برای راهنمایی مالیاتی دقیق، نوع مؤدی (شخص حقیقی یا حقوقی)، " +
        "سال مالیاتی و موضوع پرونده مهم است.\n\n" +
        "قوانین و مهلت‌ها ممکن است تغییر کنند؛ برای تصمیم یا دفاعیه نهایی، " +
        "اسناد و مقررات معتبر همان سال باید بررسی شوند."
    },
    {
      keys: [
        "بیمه", "تامین اجتماعی", "تأمین اجتماعی",
        "لیست بیمه", "حقوق"
      ],
      answer:
        "در امور بیمه و تأمین اجتماعی می‌توانیم راهنمایی اولیه " +
        "درباره لیست بیمه، حقوق و دستمزد و مسائل کارفرمایی ارائه کنیم.\n\n" +
        "برای بررسی دقیق‌تر، موضوع و بازه زمانی را مشخص کنید. " +
        "اطلاعات هویتی یا محرمانه را در این گفت‌وگو ارسال نکنید."
    },
    {
      keys: ["معدن", "معدنی", "صنعتی", "پیمانکاری", "کارخانه"],
      answer:
        "برای شرکت‌های معدنی، صنعتی و پیمانکاری، خدمات می‌تواند شامل " +
        "استقرار یا بررسی سیستم حسابداری، بهای تمام‌شده، کنترل موجودی، " +
        "گزارش‌های مدیریتی، مالیات و رسیدگی به اسناد باشد.\n\n" +
        "نوع فعالیت و نیاز اصلی شرکت را بفرمایید تا مسیر مناسب مشخص شود."
    },
    {
      keys: ["آموزش", "دوره", "نرم افزار", "نرم‌افزار"],
      answer:
        "مؤسسه در حوزه آموزش حسابداری و راهنمایی درباره سیستم‌های " +
        "حسابداری، انبارداری و حضور و غیاب فعالیت دارد.\n\n" +
        "لطفاً سطح آموزش یا نوع نرم‌افزار موردنظر را بنویسید."
    },
    {
      keys: [
        "تماس", "تلفن", "مشاوره", "همکاری",
        "درخواست", "پیشنهاد", "شکایت"
      ],
      answer:
        "برای پیگیری انسانی می‌توانید با شماره همراه مؤسسه " +
        CONFIG.phone + " تماس بگیرید.\n\n" +
        "موضوع درخواست و زمان مناسب تماس را مشخص کنید. " +
        "اطلاعات مالی، کد ملی، رمز عبور یا اسناد محرمانه را ارسال نکنید."
    }
  ];

  function localAnswer(text) {
    const t = text.toLowerCase()
      .replace(/ي/g, "ی")
      .replace(/ك/g, "ک");

    for (const item of faq) {
      if (item.keys.some(k => t.includes(k))) {
        return item.answer;
      }
    }

    return (
      "برای اینکه راهنمایی درستی بدهم، لطفاً موضوع را کمی دقیق‌تر " +
      "توضیح دهید؛ مثلاً حسابداری، مالیات، بیمه، حسابرسی، آموزش " +
      "یا درخواست تماس.\n\n" +
      "این نسخه از پاسخ‌های راهنمای آماده استفاده می‌کند. " +
      "برای پاسخ‌گویی هوشمند به پرسش‌های آزاد، باید backend امن فعال شود."
    );
  }

  async function answer(text) {
    if (!CONFIG.CHAT_ENDPOINT) {
      return localAnswer(text);
    }

    const response = await fetch(CONFIG.CHAT_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        page: location.href,
        language: "fa"
      })
    });

    if (!response.ok) {
      throw new Error("chat endpoint error");
    }

    const data = await response.json();
    return data.reply ||
      "در حال حاضر امکان پاسخ‌گویی وجود ندارد. لطفاً با مؤسسه تماس بگیرید.";
  }

  function openPanel() {
    panel.style.display = "flex";
    panel.setAttribute("aria-hidden", "false");
    launcher.style.display = "none";
    showWelcome();
    input.focus();
  }

  function closePanel() {
    panel.style.display = "none";
    panel.setAttribute("aria-hidden", "true");
    launcher.style.display = "block";
    launcher.focus();
  }

  launcher.addEventListener("click", openPanel);

  panel.querySelector("#chortkeh-chat-close")
    .addEventListener("click", closePanel);

  panel.querySelectorAll("[data-q]").forEach(btn => {
    btn.addEventListener("click", () => {
      const queries = {
        services: "خدمات مؤسسه چرتکه چیست؟",
        tax: "برای خدمات مالیاتی و اظهارنامه چه کمکی می‌کنید؟",
        industry: "برای شرکت‌های معدنی و صنعتی چه خدماتی دارید؟",
        contact: "می‌خواهم درخواست تماس ثبت کنم."
      };

      input.value = queries[btn.dataset.q] || "";
      form.requestSubmit();
    });
  });

  form.addEventListener("submit", async event => {
    event.preventDefault();

    const text = input.value.trim();
    if (!text) return;

    addMessage(text, "user");
    input.value = "";
    input.disabled = true;
    sendButton.disabled = true;

    const wait = addMessage("در حال آماده‌سازی پاسخ…", "bot");

    try {
      const reply = await answer(text);
      wait.textContent = reply;
    } catch (error) {
      wait.textContent =
        "در حال حاضر اتصال پاسخ‌گویی در دسترس نیست. " +
        "لطفاً با شماره " + CONFIG.phone + " تماس بگیرید.";
    } finally {
      input.disabled = false;
      sendButton.disabled = false;
      messages.scrollTop = messages.scrollHeight;
      input.focus();
    }
  });
})();
