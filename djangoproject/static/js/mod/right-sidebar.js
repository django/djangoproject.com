function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0
    );
}

let copyBanner = document.querySelector("#billboard");

window.addEventListener("scroll", function(){
let el = document.querySelector(".my-wrap");
if(isInViewport(copyBanner) == true)
{   
    console.log("visible")
    el.style.position="absolute"
    el.style.top="20%"
    el.style.paddingRight="5%"

    if(window.matchMedia("(max-width: 1536px)").matches === true){
      console.log(125)
      el.style.left="64%"
    }else if(window.matchMedia("(max-wdith: 1745px)").matches === true){
      console.log(110)
      el.style.left="62%"
    }else if(window.matchMedia("(max-width: 1920px)").matches === true){
      console.log(100)
      el.style.left="61%" 
    }else if(window.matchMedia("(max-width: 2133px)").matches === true){
      console.log(90)
      el.style.left="60%" 
    }else{
      console.log('else');
      el.style.left="59%"
    }

}else{
    console.log("hidden")
    el.style.position="fixed"
    el.style.top="2%"
    el.style.paddingRight="5%"
    
    if(window.matchMedia("(max-width: 1536px)").matches === true){
      
      console.log(125)
      el.style.left="64%"
    }else if(window.matchMedia("(max-wdith: 1745px)").matches === true){
      
      console.log(110)
      el.style.left="62%"
    }else if(window.matchMedia("(max-width: 1920px)").matches === true){
      
      console.log(100)
      el.style.left="61%" 
    }else if(window.matchMedia("(max-width: 2133px)").matches === true){
    
      console.log(90)
      el.style.left="60%" 
    }else{
      console.log('else');
      el.style.left="59%"
    }
    
}
});
