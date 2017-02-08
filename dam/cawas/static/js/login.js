$( document ).ready(function() {
        console.log( "ready!" );
        function printMsg(){
          $(".notifications").fadeToggle("slow");
        }
        setTimeout(printMsg, 2000);
});