
(function(){
  const stage = document.getElementById("playStage");
  const dog = document.getElementById("webDog");
  const hand = document.getElementById("handPointer");
  const ball = document.getElementById("ball");
  const status = document.getElementById("playStatus");
  if(!stage || !dog || !hand || !ball) return;

  let dragging = false;
  let offset = {x:0,y:0};

  function localPoint(evt){
    const r = stage.getBoundingClientRect();
    const p = evt.touches ? evt.touches[0] : evt;
    return {x:p.clientX-r.left, y:p.clientY-r.top};
  }

  stage.addEventListener("pointermove",(e)=>{
    const p = localPoint(e);
    hand.style.left = p.x+"px"; hand.style.top = p.y+"px";
    const d = dog.getBoundingClientRect();
    const s = stage.getBoundingClientRect();
    const cx = d.left-s.left+d.width/2, cy = d.top-s.top+d.height/2;
    const near = Math.hypot(p.x-cx,p.y-cy) < 120;
    dog.classList.toggle("happy",near);
    status.textContent = near ? "쓰담쓰담! 해피가 기분이 좋아졌어요 :)" : "마우스로 해피에게 손을 가져가 보세요.";
    if(dragging){
      ball.style.left = (p.x-offset.x)+"px";
      ball.style.top = (p.y-offset.y)+"px";
      ball.style.bottom = "auto";
    }
  });

  ball.addEventListener("pointerdown",(e)=>{
    dragging=true; ball.setPointerCapture(e.pointerId);
    const r=ball.getBoundingClientRect(); const s=stage.getBoundingClientRect();
    const p=localPoint(e); offset.x=p.x-(r.left-s.left); offset.y=p.y-(r.top-s.top);
    status.textContent="공을 원하는 곳으로 옮겨 놓아보세요!";
  });
  ball.addEventListener("pointerup",(e)=>{
    dragging=false;
    const br=ball.getBoundingClientRect(), dr=dog.getBoundingClientRect();
    const dist=Math.hypot((br.left+br.width/2)-(dr.left+dr.width/2),(br.top+br.height/2)-(dr.top+dr.height/2));
    if(dist < 210){
      dog.classList.add("happy");
      status.textContent="공 발견! 해피가 신났어요 🎾";
      setTimeout(()=>dog.classList.remove("happy"),1200);
    } else status.textContent="해피가 공을 찾으러 갈 준비를 하고 있어요.";
  });

  document.querySelectorAll("[data-action]").forEach(btn=>{
    btn.addEventListener("click",()=>{
      const action=btn.dataset.action;
      if(action==="pet"){
        dog.classList.add("happy"); status.textContent="해피를 쓰다듬었어요. 꼬리가 흔들흔들!";
        setTimeout(()=>dog.classList.remove("happy"),1400);
      }
      if(action==="snack"){
        dog.classList.add("happy"); status.textContent="간식 타임! 냠냠 🦴";
        setTimeout(()=>dog.classList.remove("happy"),1400);
      }
      if(action==="walk"){
        status.textContent="산책 가자! 해피가 먼저 신나게 앞으로 나갑니다 🐾";
        dog.animate([{transform:"translate(-50%,-50%)"},{transform:"translate(-42%,-50%)"},{transform:"translate(-50%,-50%)"}],{duration:900,iterations:2});
      }
    });
  });
})();
