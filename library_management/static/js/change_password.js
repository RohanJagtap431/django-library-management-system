const passwordInput1 = document.getElementById("password1")
const toggleButton1 = document.getElementById("toggle-password1")
const eyeIcon1 = document.getElementById("eye-icon1")
const passwordInput2 = document.getElementById("password2")
const toggleButton2 = document.getElementById("toggle-password2")
const eyeIcon2 = document.getElementById("eye-icon2")
const passwordInput3 = document.getElementById("password3")
const toggleButton3 = document.getElementById("toggle-password3")
const eyeIcon3 = document.getElementById("eye-icon3")


if (toggleButton1){
    toggleButton1.addEventListener("click", function(){
    if (passwordInput1.type === 'password'){
        passwordInput1.type = 'text'
        eyeIcon1.classList.replace('fa-eye', 'fa-eye-slash');
        
    }
    
    else{
        passwordInput1.type = 'password'
        eyeIcon1.classList.replace('fa-eye-slash', 'fa-eye');
    }
})
}



if (toggleButton2){
    toggleButton2.addEventListener("click", function(){
    if (passwordInput2.type === 'password'){
        passwordInput2.type = 'text'
        eyeIcon2.classList.replace('fa-eye', 'fa-eye-slash');
        
    }
    
    else{
        passwordInput2.type = 'password'
        eyeIcon2.classList.replace('fa-eye-slash', 'fa-eye');
    }
})
}



if (toggleButton3){
    toggleButton3.addEventListener("click", function(){
    if (passwordInput3.type === 'password'){
        passwordInput3.type = 'text'
        eyeIcon3.classList.replace('fa-eye', 'fa-eye-slash');
        
    }
    
    else{
        passwordInput3.type = 'password'
        eyeIcon3.classList.replace('fa-eye-slash', 'fa-eye');
    }
})
}










