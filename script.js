
(function(){
  const cfg = window.EUNYU_CONFIG || {};
  const $ = (s, root=document) => root.querySelector(s);
  const $$ = (s, root=document) => [...root.querySelectorAll(s)];

  $$("[data-img]").forEach(el=>{
    const key = el.dataset.img;
    if(cfg.images && cfg.images[key]) el.src = cfg.images[key];
  });

  $$("[data-link]").forEach(el=>{
    const key = el.dataset.link;
    if(cfg.links && cfg.links[key]) el.href = cfg.links[key];
  });

  $$("[data-logo]").forEach(el=>{
    if(cfg.brand && cfg.brand.logo) el.src = cfg.brand.logo;
  });

  const menuBtn = $(".menu-btn");
  const navLinks = $(".nav-links");
  if(menuBtn && navLinks){
    menuBtn.addEventListener("click",()=>navLinks.classList.toggle("open"));
  }

  // Email copy
  $$("[data-copy-email]").forEach(btn=>{
    const email = (cfg.contact && cfg.contact.email) || "eunyumade01@gmail.com";
    btn.textContent = btn.dataset.label || "Email 복사";
    btn.title = email;
    btn.addEventListener("click", async (e)=>{
      e.preventDefault();
      try{
        await navigator.clipboard.writeText(email);
        const old = btn.textContent;
        btn.textContent = "복사됨 ✓";
        setTimeout(()=>btn.textContent=old, 1600);
      }catch(err){
        window.prompt("이메일 주소를 복사하세요.", email);
      }
    });
  });

  // IDEA section:
  // 별도 서버가 없으므로 DB에 저장하지 않습니다.
  // 제출하면 사용자의 기본 메일 앱을 열고 이메일 본문에 아이디어를 채워줍니다.
  const ideaForm = $("#ideaForm");
  const ideaMessage = $("#ideaMessage");
  if(ideaForm){
    ideaForm.addEventListener("submit",(e)=>{
      e.preventDefault();
      const input = $("#ideaInput");
      const value = input ? input.value.trim() : "";
      if(!value){
        if(ideaMessage) ideaMessage.textContent = "떠오르는 생각을 한 줄만 적어주세요.";
        return;
      }
      const email = (cfg.contact && cfg.contact.email) || "eunyumade01@gmail.com";
      const subject = encodeURIComponent("[은유제작소] 홈페이지에서 남긴 아이디어");
      const body = encodeURIComponent("안녕하세요, 은유제작소.\n\n이런 것을 만들어보면 재미있을 것 같아요:\n\n" + value + "\n");
      if(ideaMessage) ideaMessage.textContent = "메일 앱을 열고 있어요. 전송 버튼을 눌러야 실제로 전달됩니다.";
      window.location.href = `mailto:${email}?subject=${subject}&body=${body}`;
    });
  }
})();
