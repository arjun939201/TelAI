const chatContainer=document.getElementById("chatContainer");
const welcome=document.getElementById("welcome");
const chatForm=document.getElementById("chatForm");
const messageInput=document.getElementById("messageInput");
const sendButton=document.getElementById("sendButton");
const clearButton=document.getElementById("clearButton");
const mobileNewChat=document.getElementById("mobileNewChat");
const standardMode=document.getElementById("standardMode");
const melimiMode=document.getElementById("melimiMode");
const modelName=document.getElementById("modelName");

let mode="melimi",history=[],isSending=false;

function setMode(newMode){
    mode=newMode;
    standardMode.classList.toggle("active",mode==="standard");
    melimiMode.classList.toggle("active",mode==="melimi");
    modelName.textContent=mode==="melimi"?"మేలిమి తెలుగు AI":"తెలుగు AI";
    messageInput.placeholder=mode==="melimi"?"మేలిమి తెలుగులో అడుగు...":"తెలుగులో అడుగు...";
}
standardMode.addEventListener("click",()=>setMode("standard"));
melimiMode.addEventListener("click",()=>setMode("melimi"));

function escapeHtml(v){return String(v).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]));}
function renderMelimiText(text,audit){
 const map=new Map((audit||[]).map(x=>[x.word,x]));
 return String(text).split(/([\u0C00-\u0C7F]+|[A-Za-z]+(?:['’-][A-Za-z]+)*)/g).map(part=>{
  const x=map.get(part); if(!x)return escapeHtml(part);
  const cls=x.clickable?"word-token unregistered":"word-token";
  const title=x.loan?"Loan/foreign word — click to teach Melimi":(x.melimi_gap?"Melimi equivalent needed — click to teach":"Melimi word");
  return `<span class="${cls}" data-word="${escapeHtml(part)}" title="${title}">${escapeHtml(part)}</span>`;
 }).join("");
}
function addMessage(text,role,melimi=false,audit=[]){
 const wrapper=document.createElement("div");wrapper.className=`message ${role}`;
 if(role==="assistant"&&melimi)wrapper.classList.add("melimi");
 const content=document.createElement("div");content.className="message-content";
 content.innerHTML=role==="assistant"&&melimi?renderMelimiText(text,audit):escapeHtml(text);
 wrapper.appendChild(content);chatContainer.appendChild(wrapper);scrollToBottom();
}

function showTyping(){
    const wrapper=document.createElement("div");
    wrapper.id="typingIndicator";wrapper.className="typing-message";
    wrapper.innerHTML='<div class="typing"><span></span><span></span><span></span></div>';
    chatContainer.appendChild(wrapper);scrollToBottom();
}
function removeTyping(){document.getElementById("typingIndicator")?.remove()}
function addError(text){
    const wrapper=document.createElement("div");wrapper.className="error-message";
    const error=document.createElement("div");error.className="error";error.textContent=text;
    wrapper.appendChild(error);chatContainer.appendChild(wrapper);scrollToBottom();
}
function scrollToBottom(){requestAnimationFrame(()=>chatContainer.scrollTop=chatContainer.scrollHeight)}
function resizeInput(){messageInput.style.height="auto";messageInput.style.height=`${Math.min(messageInput.scrollHeight,160)}px`}
messageInput.addEventListener("input",resizeInput);

async function sendMessage(){
    if(isSending)return;
    const text=messageInput.value.trim();if(!text)return;
    isSending=true;sendButton.disabled=true;messageInput.value="";resizeInput();
    if(welcome)welcome.style.display="none";
    addMessage(text,"user");
    const previousHistory=[...history];
    showTyping();
    try{
        const response=await fetch("/chat",{method:"POST",headers:{"Content-Type":"application/json"},
            body:JSON.stringify({message:text,mode,history:previousHistory})});
        const data=await response.json().catch(()=>({}));
        removeTyping();
        if(!response.ok){addError(data.detail||`సర్వర్ లోపం: ${response.status}`);return}
        if(!data.reply){addError("AI నుండి సమాధానం రాలేదు.");return}
        addMessage(data.reply,"assistant",mode==="melimi",data.word_audit||[]);
        history.push({role:"user",content:text});
        history.push({role:"assistant",content:data.reply});
    }catch(error){
        removeTyping();console.error("TeluAI error:",error);
        addError("సర్వర్‌ను చేరుకోలేకపోయాము. మళ్లీ ప్రయత్నించు.");
    }finally{isSending=false;sendButton.disabled=false;messageInput.focus()}
}
chatForm.addEventListener("submit",e=>{e.preventDefault();sendMessage()});
messageInput.addEventListener("keydown",e=>{if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();sendMessage()}});
document.querySelectorAll(".suggestion").forEach(button=>button.addEventListener("click",()=>{
    const text=button.dataset.message;if(!text)return;messageInput.value=text;resizeInput();sendMessage();
}));
function newChat(){
    history=[];
    chatContainer.querySelectorAll(".message,.error-message,.typing-message").forEach(x=>x.remove());
    if(welcome)welcome.style.display="";
    messageInput.value="";resizeInput();messageInput.focus();
}
clearButton.addEventListener("click",newChat);
mobileNewChat.addEventListener("click",newChat);
setMode("melimi");resizeInput();messageInput.focus();



function modalElements(){return {modal:document.getElementById("wordModal"),word:document.getElementById("selectedWord"),status:document.getElementById("wordStatus"),root:document.getElementById("wordRoot"),meaning:document.getElementById("wordMeaning"),pos:document.getElementById("wordPos"),melimi:document.getElementById("wordMelimi"),formation:document.getElementById("wordFormation"),result:document.getElementById("wordResult"),register:document.getElementById("registerWord")}}
function closeWordModal(){const x=modalElements();x.modal?.classList.add("hidden")}
async function openWordModal(word=""){
 const x=modalElements();if(!x.modal)return;
 x.word.textContent=word||"కొత్త మేలిమి పదం";x.root.value=word||"";x.meaning.value="";x.pos.value="";x.melimi.value="";x.formation.value="";x.result.textContent="";x.register.disabled=false;
 x.status.textContent=word?"Loan/foreign word or Melimi gap — enter the verified Melimi Telugu form.":"Add a user-verified Melimi Telugu word.";x.status.style.color="#d9a441";x.modal.classList.remove("hidden");
 if(word){try{const r=await fetch("/melimi/word/"+encodeURIComponent(word));const d=await r.json();if(d.melimi_equivalent)x.melimi.value=d.melimi_equivalent;if(d.root_candidate)x.root.value=d.root_candidate;if(d.loan)x.status.textContent="Known loan/foreign word — supply its Melimi Telugu equivalent.";}catch(e){}}
 setTimeout(()=>x.melimi.focus(),50)
}
document.addEventListener("click",e=>{const token=e.target.closest?.(".word-token.unregistered");if(token){e.preventDefault();e.stopPropagation();openWordModal(token.dataset.word||token.textContent.trim())}})
document.getElementById("addWordButton")?.addEventListener("click",()=>openWordModal())
document.getElementById("closeWordModal")?.addEventListener("click",closeWordModal)
document.getElementById("cancelWord")?.addEventListener("click",closeWordModal)
document.getElementById("wordModalBackdrop")?.addEventListener("click",closeWordModal)
document.addEventListener("keydown",e=>{if(e.key==="Escape")closeWordModal()})
document.getElementById("registerWord")?.addEventListener("click",async()=>{
 const x=modalElements();const source=x.root.value.trim()||x.word.textContent.trim();const melimi=x.melimi.value.trim();
 if(!source||source==="కొత్త మేలిమి పదం"){x.result.style.color="#ef7777";x.result.textContent="Enter the source/loan word.";return}
 if(!melimi){x.result.style.color="#ef7777";x.result.textContent="Enter the Melimi Telugu word.";x.melimi.focus();return}
 x.register.disabled=true;x.result.style.color="#aaa";x.result.textContent="Saving to GitHub…";
 try{const r=await fetch("/melimi/register",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({word:source,root:x.root.value.trim(),meaning:x.meaning.value.trim(),part_of_speech:x.pos.value.trim(),melimi_equivalent:melimi,formation:x.formation.value.trim()})});const d=await r.json();if(!r.ok)throw Error(d.detail||"GitHub registration failed");
   x.result.style.color="#8ed9a0";x.result.textContent=d.commit_url?"Saved to GitHub and added to the Melimi subject.":"Saved locally.";setTimeout(closeWordModal,900)
 }catch(e){x.result.style.color="#ef7777";x.result.textContent=e.message||"Could not save the word."}finally{x.register.disabled=false}
})
