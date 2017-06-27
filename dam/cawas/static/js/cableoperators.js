$( document ).ready(function() {
    var dataTable = $('#example').dataTable({"sPaginationType": "full_numbers"});

    console.log( "ready!" );
    // inicializar tooltips para los íconos de HELP
    $('[data-toggle="tooltip"]').tooltip(); 
    
    var checkedOnce = 0; //chequea si el formulario se ha intentado enviar alguna vez
    var checkVal=0; //chequea la cantidad de errores en el formulario
    var clickedToSubmit = 0; //chequea si el botón de submit se ha presionado
    var checkText="";
    var display_runtimeJSON; //necesaria para armar el valor final que debe ir en el JSON


    var clickedVal; // recoge el valor del ID seleccionado en la lista de chcas;
    var clickedName; // recoge el valor del Nombre seleccionado en la lista de chcas;

    var countChecked = function() {
    langQ = $("input:checked" ).length;
        $('input[type=checkbox]').each(function(){
            if (this.checked) {
                langDesc.push($(this).attr("id"));
            }
        });

    };
    // activar los selects con filtro
    $("#cableoperator-select").select2({placeholder: "Despliega la lista"});
    $("#pais").select2({placeholder: "Seleccionar Pais"});


    $("#btnsearch").click(function(){
           $("#searchForID").submit();
    });
    // simular exit con el botón de salir
    $("#getOut").click(function(){
           window.location.href = "/logout";
    });

    // simular exit con el botó de salir
    $("#EDBtn").click(function(){
           window.location.href = "/cableoperators/edit/"+clickedTextID;
    });



    // Toma el ID de la chica seleccionada en la lista
   // Toma el nombre de la movie seleccionada en la lista
    $( "#cableoperator-select" ).change(function() {

        $( "#cableoperator-select option:selected" ).each(function() {
            clickedTextID = $(this).val();
            if(clickedTextID >0 )
            {
                $("#cableoperatorNAME").val(clickedTextID);// Agrega el ID en el input field
                $("#cableoperatorID").val(clickedTextID);// Agrega el ID en el input field
            }
        });

    });
    
    // interacción del usuario al hacer click en el botón debajo de la lista de selección
    $( "#IDBtn" ).click(function(){
        $( "#chica-pickerForm" ).submit();// Envía el formulario con el id de la chica
    })
    
    // interacción del usuario al hacer click en el botón de agregar chicas
    $( "#ADBtn" ).click(function(){
             $( "#hidden1" ).show();
    });


    // interacción del usuario al hacer click en el botón cancelar
    $( "#CancelBtn" ).click(function(){ 
         $( "#hidden1" ).hide();
    });
    
    
    //preview de imagenes cargadas por el front end
    $( "#ThumbHor" ).change(showPreviewImage_click);
    $( "#ThumbVer" ).change(showPreviewImage_click);
    
     
    function showPreviewImage_click(e) {
            var $input = $(this);
            var inputFiles = this.files;
            if(inputFiles == undefined || inputFiles.length == 0) return;
            var inputFile = inputFiles[0];

            var reader = new FileReader();
            reader.onload = function(event) {
                $input.parent().find('img').attr("src", event.target.result);
            };
            reader.onerror = function(event) {
                alert("ERROR: " + event.target.error.code);
            };
            reader.readAsDataURL(inputFile);
    }
    
    /*---- DATE PICKER ----*/
    $('.datePick').dcalendarpicker({
      format: 'dd-mm-yyyy'
    });



    
    
    /* triggers for checkALL function */
    $("#sendBut").click(function(){
        clickedToSubmit=1;
        checkAll();
    });

    $("#btngrabarypublicar").click(function(){

        $("#publicar").val("1");
        clickedToSubmit=1;
        checkAll();
    });
    
    $("body").mouseup(function(){
        if(checkedOnce>0 && checkVal>0 ){
            clickedToSubmit=0;
            checkAll();      
        }
    })
    
    
    function checkAll(){
        // this function checks for all form values and makes json string to post or alerts user to complete fields.
        console.log("checking form...");
        checkVal = 0;
        var asset_Id = $('#cableoperatorID').val();
        var nombre = $('#nombre').val();
        var site = $('#site').val();
        var phone = $('#phone').val();
        var paisSelect = $('#pais').val();
        var publicar = $('#publicar').val();

        
        //Valida Pais
        if (paisSelect =="0" || paisSelect ==""){
            errorMe("#pais");
            checkVal++;
        }else{
            okMe("#pais");
            paisSelect=$('#pais').val();
        }

        // chequea Nombre
        if(nombre=="" || nombre==" ")
        {
            errorMe("#nombre");
            checkVal++;
        }else{
            okMe("#nombre");
        }

        // chequea site
        if(site=="" || site==" ")
        {
            errorMe("#site");
            checkVal++;
        }else{
            okMe("#site");
        }



        // chequea thumbnail horizaontal
        if(!$('#ThumbHor').val() && !$('#imgantlandscape').val()){
            errorMe("#ThumbHor");
            checkVal++;
        }else{
            okMe("#ThumbHor");
        }



                
        /* -----------  Sending Routine -----------*/
        
        if(checkVal>0){
            if(checkedOnce<1){// envía por primera vez y tiene error
                $("#myModal2").modal();
            }
            console.log("checkVal:"+checkVal);
        }else{
            if(checkedOnce<1){// envía por primera vez y NO tiene error
                submitJson();
            }else{// se ha verificado más de una vez y ahora no tiene error
                if(clickedToSubmit==1)// sólo se envía si se ha oprimido el botón de submit;
                    {
                        submitJson();
                    }
            }
        }
        
        checkedOnce++;
        
                

        
            function errorMe(theField){
                if ($(theField).parent().hasClass('has-success')){
                    $(theField).parent().removeClass('has-success');
                }
                
                if($(theField).next(".glyphicon").hasClass('glyphicon-ok')){
                    $(theField).next(".glyphicon").removeClass('glyphicon-ok');
                }
                $(theField).parent().addClass('has-error');
                $(theField).next(".glyphicon").addClass('glyphicon-remove');
                if(theField=="#canalSelect"){
                    console.log("canalSelect selected");
                    $("#channelSelect").children(".select2-selection--single").css("display","none");
                        //.css("border","1px #ff0000 solid!important");
                }
                
            }
        
            function okMe(theField){
                if ($(theField).parent().hasClass('has-error')){
                    $(theField).parent().removeClass('has-error');
                }
                
                if($(theField).next(".glyphicon").hasClass('glyphicon-remove')){
                    $(theField).next(".glyphicon").removeClass('glyphicon-remove');
                }
                $(theField).parent().addClass("has-success");
                $(theField).next(".glyphicon").addClass("glyphicon-ok");
                
            }
        



        
        
            function submitJson(){
                if(checkVal==0){
                    var myJSON = '';
                    myJSON+='{"cableoperator":{';
                    myJSON+='"name":"'+nombre+'",';
                    myJSON+='"site":"'+site+'",';
                    myJSON+='"phone":"'+phone+'",';
                    myJSON+='"country_id":"'+paisSelect+'",';
                    myJSON+='"publicar":"'+publicar+'"';
                    myJSON+='}}';
                    console.log(myJSON);
                    $("#varsToJSON").val(myJSON);
                    $("#cableoperatorForm").submit();
                  }  
            }
        
    }
    
});