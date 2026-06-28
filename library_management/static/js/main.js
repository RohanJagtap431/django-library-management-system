const passwordInput = document.getElementById("password")
const toggleButton = document.getElementById("toggle-password")
const eyeIcon = document.getElementById("eye-icon")



toggleButton.addEventListener("click", function(){
    if (passwordInput.type === 'password'){
        passwordInput.type = 'text'
        eyeIcon.classList.replace('fa-eye', 'fa-eye-slash');
        
    }
    
    else{
        passwordInput.type = 'password'
        eyeIcon.classList.replace('fa-eye-slash', 'fa-eye');
    }
})

