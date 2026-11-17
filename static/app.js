const form=document.getElementById('form');
const input=document.getElementById('image');
const message=document.getElementById('message');
const preview=document.getElementById('preview');
const previewWrap=document.getElementById('previewWrap');
const result=document.getElementById('result');
const button=document.getElementById('submit');
input.addEventListener('change',()=>{
  const file=input.files[0];
  result.classList.add('hidden');
  if(!file){previewWrap.classList.add('hidden');return;}
  preview.src=URL.createObjectURL(file);
  previewWrap.classList.remove('hidden');
  message.textContent='';
});
form.addEventListener('submit',async e=>{
  e.preventDefault();
  if(!input.files[0]){message.textContent='Сначала выберите фотографию.';return;}
  button.disabled=true;button.textContent='Анализируем…';message.textContent='Первый запуск может занять больше времени: загружается модель распознавания.';
  const data=new FormData();data.append('image',input.files[0]);
  try{
    const response=await fetch('/process',{method:'POST',body:data});
    const json=await response.json();
    if(!response.ok)throw new Error(json.error||'Ошибка обработки');
    document.getElementById('resultImage').src=json.result_url+'?t='+Date.now();
    document.getElementById('occupied').textContent=json.occupied;
    result.classList.remove('hidden');message.textContent=`Готово · ${json.processing_ms} мс`;
    result.scrollIntoView({behavior:'smooth'});
  }catch(err){message.textContent=err.message;}
  finally{button.disabled=false;button.textContent='Проанализировать фотографию';}
});