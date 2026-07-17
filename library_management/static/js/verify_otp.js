const inputs = document.querySelectorAll(".otp-input");
const hiddenOTP = document.getElementById("otp");

inputs.forEach((input, index) => {

    input.addEventListener("input", (e) => {

        input.value = input.value.replace(/[^0-9]/g,'');

        if(input.value && index < inputs.length-1){
            inputs[index+1].focus();
        }

        hiddenOTP.value = [...inputs].map(i=>i.value).join('');
    });

    input.addEventListener("keydown", (e)=>{
        if(e.key==="Backspace" && !input.value && index>0){
            inputs[index-1].focus();
        }
    });

});

inputs[0].addEventListener("paste",(e)=>{

    e.preventDefault();

    let data = (e.clipboardData || window.clipboardData)
        .getData("text")
        .replace(/\D/g,'');

    data.split("").slice(0,6).forEach((num,i)=>{
        inputs[i].value=num;
    });

    hiddenOTP.value = [...inputs].map(i=>i.value).join('');

    if(data.length>=6){
        inputs[5].focus();
    }
});


let timeLeft = Number(
    document.getElementById("otpTimer").dataset.time
);

const timer = setInterval(function () {

    let minutes = Math.floor(timeLeft / 60);
    let seconds = timeLeft % 60;

    document.getElementById("otpTimer").innerHTML =
        String(minutes).padStart(2, "0") + ":" +
        String(seconds).padStart(2, "0");

    if (timeLeft <= 0) {
        clearInterval(timer);

        document.getElementById("otpTimer").innerHTML = "Expired";
    }

    timeLeft--;

}, 1000);

