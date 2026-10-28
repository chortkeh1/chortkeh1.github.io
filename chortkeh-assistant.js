
/*
 * دستیار پاسخگوی مؤسسه حسابداری و حسابرسی چرتکه
 * نسخه بازنویسی‌شده با لوگوی اصلی چرتکه
 */
(() => {
  if (window.__chortkehAssistantLoaded) return;
  window.__chortkehAssistantLoaded = true;

  const CONFIG = {
    title: "دستیار هوشمند چرتکه",
    subtitle: "راهنمای خدمات حسابداری و مالی",
    phone: "09131989006",
    CHAT_ENDPOINT: "https://chortkeh-assistant-api.xx116087.workers.dev/"
  };

  // لوگوی چرتکه، جاسازی‌شده در همین فایل
  const LOGO =
    "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD//gAQTGF2YzU4LjU0LjEwMAD/2wBDAAsICAoIBwsKCQoNDAsNERwSEQ8PESIZGhQcKSQrKigkJyctMkA3LTA9MCcnOEw5PUNFSElIKzZPVU5GVU5GVEBHSEX/2wBDAQwNDREPESESEiFFLicuRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUX/wAARCACgAKADASIAAhEBAxEB/8QAGwABAAMBAQEBAAAAAAAAAAAAAAUGBwMEAQL/xAA/EAABAwMBAwkDCgQHAAAAAAABAAIDBAURBhITIQcUMUFRUlSRkmFxcxUiMjaBobGywdEjYpPhJjVDcnSC8P/EABoBAQADAQEBAAAAAAAAAAAAAAADBAUCAQb/xAArEQACAgIABQMCBwEAAAAAAAAAAQIDBBEFEiExQRMyUSIzJDRhcYGRobH/2gAMAwEAAhEDEQA/AMiREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAUnpymhrNQ0FPUMEkMkzWvaesKMUxpP602z47VHa9Vya+Gex7olNfWuitdwpo6GnZAx8ZLg3PE59qqau3KYc3Sk+E78ypKgwpOWPFt7Z3atTegrRoK20l0vc0NdA2eNtO54a7PAgjjw96keTjT9Dc5aqsuMTZmQFrI438WlxySSOvAH3rTIqW1UL9umpaeJ5GC6ONrTjs4Kln56r5qYp713+CSqpvUmYfqalhotRVtPTRiOKN+GsHQOAUUt+qKKy1Re6ahppJH/Sc+JpJ95wsj1raaa03vZom7EEzBI1gPBpyQQPZwUmFnRu1W096/s8tqcfqK6r9o+x224aXqqmrpGSztke1r3E5ADQR1qgrTdCfU6s+LJ+QKXiEpRp3F66o5qScupmSIivkQREQBERAEREAREQBS+lPrRbfjtUQpfSv1otvx2qO77cv2Z1Huid5STm60vwz+KpaufKR/mtN8M/iqYq+B+WgdW+9lw0DcaiGqqKGGCWVs4D8xjOwR1n2cVeJYK93HcTHy/dV3kwnhpqW4vON6XsB7dnB/VXWW/MBwMBYfEJfiZcsfgt0exEIYK9vE08/kP3Wc6prZqy8OE8T4jC0Rhkgwe3P3rWzfw7gSMLNNfyxT3qGRmNowjax7zhT8Nk/W1KPg8yPaVVaXoT6oVnxZPyBZotK0Kf8ACNZ8WT8gWjxL7H8or0+4zVERaBCEREAREQBERAEREB6bdb6m618NFRx7yeZ2Gt6PtPsWh2TkyuNuulJWzVtMRDIHuYzaP2A4Vd5PKmOl1OHyEBzoXtZntx+2Vp8t9IGBlYnEcq6ufpV9mizTWpLmZB6s0JV36singqoY2xsLSHg5PHPUs4v2na3T1S2Kr2HNeCWSRnLXf3Wsm+vz1qm6/rmVNFTMJ/ib3aHuxx/RQ8PyL1ONT9pJdXHTl5Kbb7lU2yYyUsmwXDDh1OHtVo09da29V0kEhY0NiL8tb2Y9vtVMVr5PRm+zf8Z34hauZCHpSnrqkV6pPmS2crpf62huM9M0RERuwCWnP4qvVNTLVzumneXPd0lSGpxjUdd8T9AopSUQgoKSXVpHk5NtpssentFXHUUBqIXRQU4OyJJSfnHrwAtH07pKps1lnoZZ4pHyPc4OYDgZbheTSN0ih0vQiLHzGFrgO9tHKk5L8/PDKwMzJvtnKvwn/wALddcUkyiVnJddqaB0kVRTTuaM7AJBPuyFSXNLHFrgQ4HBB6itt+XS8YcT9qx68ysmvNbLF9B87yMe8rTwMm25yVvggurjDWjxIiLUK4REQBERAEREBOaPtAvWoYKd8r4o2Ayvew4cA3sPbnAWwusVCWjMkn9QrG9K3UWi9xzODiyRpidsjJ4+z34Wky11SeIbJg/yFYHFFY7Vrtou4+uVko+wUB6Jpc/7ys715ZWUEsNVDLI9jzsFr3ZwekY+9Wh1dUA8RJ6CqdrC7mrMVJh2WO23FwI6uCj4fG1XLr08nV2uR7O2gtM0l9qKie4BzqeDZaIwcbbjnpPYMLTKLTVjtcxmpKWOGQt2S4OceHZxKzHQ955jNPRlrzvyHNLWk8RnsVzlr6g9UnoKcR9d3OO2o+Pg8oUeXfkkqzSmnquSSaajjfK/i5204EnzWUars0VlvDoaYkwPaHsDjkgdn3K+uuEzRkl/oKz/AFLc/lO5lwB2Ym7A2hg9PFTcNVys1KTcdHN6io/qXnQmnYvkZlVPNJtVOXBgeQ1ozgcO3grO6w2/PGWQf9yqVpK+vktEdI1sm8pxs/NaSCM5HFTL66pJ6JPQVSyoXO+Tb8/54Jq9ci0SVbpugmppIhUTDbGMtkIIWMVtM6irZ6Z5y6GRzCe3BwtOmustNC+aQSbDBk4YVmNbUmsrZ6l3AyvLyOzJWlwxWLm5n0K+Rrp8nBERbBVCIiAIiIAiIgLTyeNhOqWSTAHdRPezPe6M/eVrT7rTtGCGkrE9L0tbWX+mitz2snJJ23fRa3HHPswtUfp6tcMiaI+3B/dfPcVhF3Jyl4LuP7SRddqc8C1iz/lCME0FPMwDeCQtyOzH9lZ36drwMh8R81Q9ZUVdSVEPOXtdCchmz1HryouH1w9eLjI7uf0MmeTMQRMrp3gb3aYzJ6Q3if8A3uWgOulM0cGtWHWq71Fple+DBa8Yew9BVitl9qLtUuhbEGlrC/O1lWM3BnZbK3wRVWxUVE0iS6Uz2kbDPJZXrlkIvTZIQAZIwXY6zkjK6VmpJqOqkgMAc5hxnb/sq9W1stfUunmOXHhgdAHYpsHCnTPnfbR5dapR5Uarop1LR6cpCA3LwXuPaclWF12pgfotVD0XbLlU2oP3jG0znHdNcCT08T7sqyO05XH/AFIvIrKyq4evLml5LFb+lEo+508jcBrR9ixK8RRw3itjhwI2zPDQOoZWp1Gnbk2B+6nhZLj5pIJGVkdSyWOplZPneteQ/PezxWlwqEU5OL+CDIfY5oiLbKgREQBERAEREBYdFXGO26gbJK4NEkbow49RPR+C0eTUJHDaWLqQtdWW3Gn51UPbTh428uJACzsvCjdL1N+Ceu3lWjUDqFxPSqjra5sqoIIcgybe2R2DGP1UTf62B1TH8nVTnR7J2i0kccqEc4uOXEknrJUeLgxg1YdWXbTifFZtDNDrzMD4d34hVlT+kLhTW66Sy1coijMLmgkE8cjsV3JTdMku+iGHuR4tQDF9rB/P+ijV773PFU3iqmgeHxvflrh18F4FJVtQjv4R5LuzT9KXyOOwU0bHAPhBY4dYOSpR+oTn6Sx5kj4zmN7mHtacKy2auoW2qQV1WW1G07ZDi4nGOH3rJyOHx25rrtliF3TRejqD5p23YaOJJPALKbpUNq7pVVDPoyyucPcSuD6iaQbL5pHDsLiVzV3Fw447bT7kVlvOERFdIgiIgCIiAIiIAiIgCIiAIiIAiIgCIiAIiIAiIgCIiA78yqvDTegpzKq8NN6CuW9k77vNN7J33eaA68yqvDTegpzKq8NN6CuW9k77vNN7J33eaA68yqvDTegpzKq8NN6CuW9k77vNN7J33eaA68yqvDTegpzKq8NN6CuW9k77vNN7J33eaA68yqvDTegpzKq8NN6CuW9k77vNfd7J33eaA6cyqvDTegpzKq8NN6CuW9k77vNfN7J33eaA68yqvDTegpzKq8NN6CuW9k77vNN7J33eaA68yqvDTegpzKq8NN6CuW9k77vNN7J33eaA68yqvDTegpzKq8NN6CuW9k77vNfN7J33eaA68yqvDTegpzKq8NN6CuW9k77vNN7J33eaA68yqvDTegpzKq8NN6CuW9k77vNfd7J33eaA6cyqvDTegpzKq8NN6CuW9k77v803snfd5oDrzKq8NN6CnMqrw03oK5b2Tvu803snfd5oD8oiIAiIgCIiAIiIAiIgCIiAIiIgCIiAIiIAiIgCIiID/9k=";

  const css = `
  #chortkeh-chat-launcher {
    position: fixed;
    z-index: 99998;
    right: 22px;
    bottom: 22px;
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
    right: 22px;
    bottom: 82px;
    width: min(370px, calc(100vw - 28px));
    height: min(560px, calc(100dvh - 115px));
    display: none;
    flex-direction: column;
    padding: 0 !important;
    margin: 0 !important;
    background: #fff;
    border: 1px solid #d8e4e1;
    border-radius: 16px;
    box-shadow: 0 12px 40px #0003;
    overflow: hidden;
    font: 14px/1.7 Tahoma, Arial, sans-serif;
    color: #233;
    direction: rtl;
    box-sizing: border-box;
  }

  #chortkeh-chat-panel *,
  #chortkeh-chat-panel *::before,
  #chortkeh-chat-panel *::after {
    box-sizing: border-box;
  }

  #chortkeh-chat-panel > * {
    margin-top: 0 !important;
  }

  #chortkeh-chat-head {
    flex: 0 0 58px;
    height: 58px;
    min-height: 58px;
    margin: 0 !important;
    padding: 5px 12px;
    display: flex;
    align-items: center;
    gap: 9px;
    overflow: hidden;
    background: #0f5f5a;
    color: #fff;
  }

  #chortkeh-chat-head .mark {
    flex: 0 0 40px;
    width: 40px;
    height: 40px;
    overflow: hidden;
    border-radius: 50%;
    border: 2px solid #e8d58b;
    background: #000;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  #chortkeh-chat-head .mark img {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  #chortkeh-chat-head .headcopy {
    flex: 1 1 auto;
    min-width: 0;
    transform: translateY(-2px);
    text-align: right;
  }

  #chortkeh-chat-head strong {
    display: block;
    font-size: 14px;
    line-height: 1.5;
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
    align-self: center;
    border: 0;
    background: transparent;
    color: white;
    font-size: 25px;
    line-height: 1;
    padding: 3px 5px;
    cursor: pointer;
  }

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

  #chortkeh-chat-quick {
    flex: 0 0 auto;
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-start;
    gap: 5px;
    padding: 6px 9px;
    margin: 0 !important;
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

  #chortkeh-chat-form {
    flex: 0 0 auto;
    display: flex;
    align-items: stretch;
    gap: 6px;
    padding: 7px 9px;
    margin: 0 !important;
    border-top: 1px solid #e5ece9;
    background: #fff;
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
    margin: 0 !important;
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
      height: min(560px, calc(100dvh - 88px));
      border-radius: 14px;
    }

    #chortkeh-chat-head {
      flex-basis: 58px;
      height: 58px;
      min-height: 58px;
    }

    #chortkeh-chat-messages {
      padding: 9px;
    }
  }

  @media (max-height: 520px) {
    #chortkeh-chat-panel {
      height: calc(100dvh - 92px);
      bottom: 72px;
    }

    #chortkeh-chat-head {
      flex-basis: 48px;
      height: 48px;
      min-height: 48px;
    }
  }
  `;

  const style = document.createElement("style");
  style.id = "chortkeh-assistant-styles";
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
  panel.setAttribute("aria-hidden", "true");

  panel.innerHTML = `
    <div id="chortkeh-chat-head">
      <div class="mark">
        <img src="${LOGO}" alt="لوگوی چرتکه">
      </div>
      <div class="headcopy">
        <strong>${CONFIG.title}</strong>
        <small>${CONFIG.subtitle}</small>
      </div>
      <button id="chortkeh-chat-close"
              type="button" aria-label="بستن">×</button>
    </div>

    <div id="chortkeh-chat-messages" aria-live="polite"></div>

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
      keys: ["بیمه", "تامین اجتماعی", "تأمین اجتماعی", "لیست بیمه", "حقوق"],
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
      keys: ["آموزش", "دوره", "نرم افزار", "نرم‌افزار", "انبارداری"],
      answer:
        "مؤسسه در حوزه آموزش حسابداری و راهنمایی درباره سیستم‌های " +
        "حسابداری، انبارداری و حضور و غیاب فعالیت دارد.\n\n" +
        "لطفاً سطح آموزش یا نوع نرم‌افزار موردنظر را بنویسید."
    },
    {
      keys: ["تماس", "تلفن", "مشاوره", "همکاری", "درخواست", "پیشنهاد", "شکایت"],
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
