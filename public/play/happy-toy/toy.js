// HAPPY 웹 장난감 (2026.07). TOUCH · PLAY · FEEL 세 체험.
(function(){
  const $ = s => document.querySelector(s);

  // 1) TOUCH — HELLO, HAPPY!
  const robot = $("#webRobot");
  const face = $("#robotFace");
  const robotStatus = $("#robotStatus");
  let armTimer;

  function robotHand(){
    if(!robot) return;
    clearTimeout(armTimer);
    robot.classList.add("arm-up");
    if(face) face.textContent = "•ᴗ•";
    if(robotStatus) robotStatus.textContent = "안녕! 해피가 손을 내밀었어요 🐾";
    armTimer = setTimeout(()=>{
      robot.classList.remove("arm-up");
      if(robotStatus) robotStatus.textContent = "또 손을 내밀어볼까요?";
    }, 1800);
  }

  function robotPet(){
    if(!robot) return;
    robot.classList.add("pet-happy");
    if(face) face.textContent = "⌒ᴗ⌒";
    if(robotStatus) robotStatus.textContent = "쓰담쓰담. 해피가 기분이 좋아졌어요!";
    setTimeout(()=>{
      robot.classList.remove("pet-happy");
      if(face) face.textContent = "•ᴗ•";
    }, 1400);
  }

  $("#robotHandBtn")?.addEventListener("click", robotHand);
  $("#robotPetBtn")?.addEventListener("click", robotPet);
  $("#petZone")?.addEventListener("click", robotPet);

  // 2) PLAY — POCKET HAPPY
  const dog = $("#catchDog");
  const treat = $("#treat");
  const scoreEl = $("#gameScore");
  const gameStatus = $("#gameStatus");

  let gameRunning = false;
  let score = 0;
  let dogX = 50;
  let treatX = 30;
  let treatY = -12;
  let gameFrame = 0;

  function setDogX(v){
    dogX = Math.max(10, Math.min(90, v));
    if(dog) dog.style.left = dogX + "%";
  }
  function moveDog(delta){ setDogX(dogX + delta); }

  function resetTreat(){
    treatX = 10 + Math.random()*80;
    treatY = -12;
    if(treat){
      treat.style.left = treatX + "%";
      treat.style.top = treatY + "%";
      treat.style.display = "block";
      treat.textContent = Math.random() > .25 ? "🦴" : "🍪";
    }
  }

  function stopGame(){
    gameRunning = false;
    cancelAnimationFrame(gameFrame);
    if(treat) treat.style.display = "none";
  }

  function tick(){
    if(!gameRunning) return;
    treatY += .42;
    if(treat) treat.style.top = treatY + "%";
    if(treatY > 76 && treatY < 93 && Math.abs(treatX-dogX) < 12){
      score += 1;
      if(scoreEl) scoreEl.textContent = "SCORE " + score;
      if(gameStatus) gameStatus.textContent = "냠! 잘 받았어요 🦴";
      resetTreat();
    }else if(treatY > 105){
      if(gameStatus) gameStatus.textContent = "앗, 놓쳤어요! 다음 간식!";
      resetTreat();
    }
    gameFrame = requestAnimationFrame(tick);
  }

  function startGame(){
    stopGame();
    score = 0;
    if(scoreEl) scoreEl.textContent = "SCORE 0";
    setDogX(50);
    gameRunning = true;
    resetTreat();
    if(gameStatus) gameStatus.textContent = "좌우로 움직여 간식을 받아보세요!";
    tick();
  }

  $("#gameStartBtn")?.addEventListener("click", startGame);
  $("#deviceStartBtn")?.addEventListener("click", startGame);
  ["#moveLeftBtn","#deviceLeftBtn"].forEach(s=>$(s)?.addEventListener("click",()=>moveDog(-10)));
  ["#moveRightBtn","#deviceRightBtn"].forEach(s=>$(s)?.addEventListener("click",()=>moveDog(10)));

  window.addEventListener("keydown",(e)=>{
    if(!gameRunning) return;
    if(e.key === "ArrowLeft") moveDog(-7);
    if(e.key === "ArrowRight") moveDog(7);
  });

  // 3) FEEL — A DAY WITH HAPPY
  const cameraBtn = $("#cameraBtn");
  const cameraPreview = $("#cameraPreview");
  const cameraVideo = $("#cameraVideo");
  const feelDog = $("#feelDog");
  const feelHand = $("#feelHand");
  const feelStatus = $("#feelStatus");
  const vibeIndicator = $("#vibeIndicator");
  let cameraStream = null;

  function vibrate(pattern){
    if(navigator.vibrate){
      navigator.vibrate(pattern);
      if(vibeIndicator){
        vibeIndicator.textContent = "VIBRATION!";
        setTimeout(()=>vibeIndicator.textContent="VIBRATION READY",700);
      }
    } else if(vibeIndicator){
      vibeIndicator.textContent = "VISUAL FEEDBACK";
      setTimeout(()=>vibeIndicator.textContent="VIBRATION READY",700);
    }
  }

  async function toggleCamera(){
    if(cameraStream){
      cameraStream.getTracks().forEach(t=>t.stop());
      cameraStream=null;
      cameraPreview?.classList.remove("on");
      if(cameraBtn) cameraBtn.textContent="카메라 켜기";
      if(feelStatus) feelStatus.textContent="카메라를 껐어요.";
      return;
    }
    try{
      cameraStream = await navigator.mediaDevices.getUserMedia({video:true,audio:false});
      if(cameraVideo) cameraVideo.srcObject = cameraStream;
      cameraPreview?.classList.add("on");
      if(cameraBtn) cameraBtn.textContent="카메라 끄기";
      if(feelStatus) feelStatus.textContent="카메라가 켜졌어요. 화면 안에서 해피와 놀아보세요.";
    }catch(e){
      if(feelStatus) feelStatus.textContent="카메라 권한을 사용할 수 없어요. 카메라 없이도 체험할 수 있습니다.";
    }
  }

  function feelPet(){
    feelHand?.classList.add("touching");
    feelDog?.classList.add("excited");
    vibrate([35,30,35]);
    if(feelStatus) feelStatus.textContent="쓰담쓰담. 해피가 눈앞에서 신나게 반응합니다.";
    setTimeout(()=>{
      feelHand?.classList.remove("touching");
      feelDog?.classList.remove("excited");
    },1200);
  }

  function feelBall(){
    feelDog?.classList.add("excited");
    vibrate(80);
    if(feelStatus) feelStatus.textContent="공을 던졌어요! 해피가 신나게 달려갑니다 🎾";
    feelDog?.animate([
      {left:"54%",bottom:"52px"},
      {left:"76%",bottom:"82px"},
      {left:"54%",bottom:"52px"}
    ],{duration:1700,easing:"ease-in-out"});
    setTimeout(()=>feelDog?.classList.remove("excited"),1300);
  }

  function feelWalk(){
    vibrate([50,70,50,70,80]);
    if(feelStatus) feelStatus.textContent="산책 시작! 바람과 발걸음 소리를 상상하며 같이 걸어볼까요? 🐾";
    feelDog?.animate([
      {transform:"translateX(0)"},
      {transform:"translateX(-55px)"},
      {transform:"translateX(35px)"},
      {transform:"translateX(0)"}
    ],{duration:2200,easing:"ease-in-out"});
  }

  cameraBtn?.addEventListener("click",toggleCamera);
  $("#feelPetBtn")?.addEventListener("click",feelPet);
  $("#feelBallBtn")?.addEventListener("click",feelBall);
  $("#feelWalkBtn")?.addEventListener("click",feelWalk);

  window.addEventListener("beforeunload",()=>{
    if(cameraStream) cameraStream.getTracks().forEach(t=>t.stop());
  });
})();
