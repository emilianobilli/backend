$( document ).ready(function() {
    
    console.log( "ready!" );
    // inicializar tooltips para los íconos de HELP
    $('[data-toggle="tooltip"]').tooltip(); 
    var clickedVal; // recoge el valor del ID seleccionado en la lista de bloques;
    var clickedName; // recoge el valor del Nombre seleccionado en la lista de bloques;
    
    // simular exit con el botó de salir
    $("#getOut").click(function(){
           window.location.href = "index.html?logstatus=OFF";
    })
    
    // Toma el ID de la chica seleccionada en la lista
    $( "#bloque-select" ).change(function() {
        
        $( "#bloque-select option:selected" ).each(function() {
          clickedName= $(this).html();
          clickedVal= $(this).val();
            if(clickedVal!="")
            {
                console.log( "clickedID="+clickedVal ); // debug
                $( "#bloqueID" ).val(clickedVal);// Agrega el ID en el hidden field
                $( "#bloqueNAME" ).val(clickedName);// Agrega el nombre en el campo visible
                  
            }
        });
        
    });
    
    // interacción del usuario al hacer click en el botón debajo de la lista de selección
    $( "#IDBtn" ).click(function(){ 
        $( "#bloque-pickerForm" ).submit();// Envía el formulario con el id de la chica
    })
    
    // interacción del usuario al hacer click en el botón de agregar chicas
    $( "#ADBtn" ).click(function(){ 
         window.location.href = "add-bloques.html";
    })   
});