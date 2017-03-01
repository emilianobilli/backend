$( document ).ready(function() {
        console.log( "ready!" );
       
    // simular exit con el botó de salir
    $("#getOut").click(function(){
           window.location.href = "index.html?logstatus=OFF";
       })
    
    $("#glyID").click(function(){
        console.log("Id search submitted");
        var $myForm = $('#searchForID');
        if (!$myForm[0].checkValidity()) {
          // If the form is invalid, submit it. The form won't actually submit;
          // this will just cause the browser to display the native HTML5 error messages.
          $myForm.find(':submit').click()
        }else{
            $( "#searchForID" ).submit();
        }
        
    })
    
    
    
    // navega desde el selector de conenidos al value+".html" de cada option
    $("#content-select").change(function() {
        var clickedVal;
        $( "#content-select option:selected" ).each(function() {
            clickedVal= $(this).val();
            if(clickedVal!="")
            {
                var urlstring="";
                switch(clickedVal){
                    case "0":
                         urlstring = "";
                         break;
                    case "1":
                        urlstring = "/movies/add/";
                        break;
                    case "2":
                        urlstring = "/serie/add/";
                        break;
                    case "3":
                        urlstring = "/block/add/";
                        break;
                    case "4":
                        urlstring = "/girl/add/";
                        break;
                     case "5":
                        urlstring = "/category/add/";
                        break;
                }
                console.log( "clickedVal="+clickedVal );
                window.location.href = urlstring;
            }
        });
        
    });
    
    // inicializar tooltips para los íconos de HELP
    $('[data-toggle="tooltip"]').tooltip(); 
});