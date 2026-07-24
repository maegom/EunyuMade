
(function(){
  const cfg = window.EUNYU_CONFIG || {};
  const $ = (s, root=document) => root.querySelector(s);
  const $$ = (s, root=document) => [...root.querySelectorAll(s)];

  // Apply config-driven images/links.
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
  if(menuBtn && navLinks) menuBtn.addEventListener("click",()=>navLinks.classList.toggle("open"));

  const ideaForm = $("#ideaForm");
  const ideaMessage = $("#ideaMessage");
  if(ideaForm){
    ideaForm.addEventListener("submit",(e)=>{
      e.preventDefault();
      const value = $("#ideaInput").value.trim();
      ideaMessage.textContent = value ? "좋은 생각이에요. ✦ 다음 만들기의 씨앗으로 남겨둘게요." : "떠오르는 생각을 한 줄만 적어주세요.";
      if(value) $("#ideaInput").value = "";
    });
  }
})();
