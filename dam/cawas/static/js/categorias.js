$( document ).ready(function() {

    //$('#example').DataTable();

    var dataTable = $('#example').dataTable({"sPaginationType": "full_numbers"});

    console.log( "ready!" );
    // inicializar tooltips para los íconos de HELP
    $('[data-toggle="tooltip"]').tooltip(); 
    
    var checkedOnce = 0; //chequea si el formulario se ha intentado enviar alguna vez
    var checkVal=0; //chequea la cantidad de errores en el formulario
    var clickedToSubmit = 0; //chequea si el botón de submit se ha presionado
    var checkText="";
    var display_runtimeJSON; //necesaria para armar el valor final que debe ir en el JSON
    var langQ = 0; //Cuenta la cantidad de idiomas elegidos por el usuario
    var langDesc = [] // recoge qué idiomas son los que se seleccionaron
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
    $("#categoria-select").select2({placeholder: "Despliega la lista"});

    $("#btnsearch").click(function(){
           $("#searchForID").submit();
    });
    // simular exit con el botón de salir
    $("#getOut").click(function(){
           window.location.href = "/logout";
    });

    // simular exit con el botó de salir
    $("#EDBtn").click(function(){
           window.location.href = "/categories/edit/"+clickedTextID;
    });



    // Toma el ID de la chica seleccionada en la lista
   // Toma el nombre de la movie seleccionada en la lista
    $( "#categoria-select" ).change(function() {

        $( "#categoria-select option:selected" ).each(function() {
            clickedTextID = $(this).val();
            if(clickedTextID >0 )
            {
                $("#categoryNAME").val(clickedTextID);// Agrega el ID en el input field
                $("#categoryID").val(clickedTextID);// Agrega el ID en el input field
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


    // checkbox idiomas detecta lo que se chequea y muestra el módulo de idioma
    $("input[type=checkbox]").on('change', function () {
        var self = $(this);
        var showDiv = "#Module_"+self.attr("id");
        if (self.is(":checked")) {
            console.log("checkbox  id =" + self.attr("id") + "is checked ");
            $(showDiv).show('slow');
            langQ++;
            langDesc.push(self.attr("id"));
            
        } else {
            console.log("Id = " + self.attr("id") + "is Unchecked ");
            $(showDiv).hide('fast');
            langQ--;
            langDesc.pop();
        }
        console.log("idiomas tildados:"+langQ+", y son:"+langDesc);// cantidad de idiomas
        if(checkedOnce>0){
            checkAll();
        }
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
        var asset_Id = $('#categoriaID').val();
        var original_name = $('#orginalName').val();

        var publicar = $('#publicar').val();
        
        countChecked();
        // chequea original Name
        if(original_name=="" || original_name==" ")
        {
            errorMe("#orginalName");
            checkVal++;
        }else{
            okMe("#orginalName");
        }


        // chequea thumbnail horizaontal
        if(!$('#ThumbHor').val() && !$('#imgantlandscape').val()){
            errorMe("#ThumbHor");
            checkVal++;
        }else{
            okMe("#ThumbHor");
        }

        // chequea thumbnail vertical
        if(!$('#ThumbVer').val() && !$('#imgantportrait').val()){
            errorMe("#ThumbVer");
            checkVal++;
        }else{
            okMe("#ThumbVer");
        }



        // chequeo de idiomas (tit_; desc_; date_)
        if(langQ==0){
            errorMe("#pickLang");
            checkVal++;
        }else{
            okMe("#pickLang");
            checkLangs(langDesc);
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
        
                
        
        
        // helper subfunctions
        
        
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
        
            function explodeArray(arr, indexname){
                var lngth = arr.length;
                var stringIt = '[';
                for(i=0; i<lngth; i++){
                    stringIt +='{"'+indexname+'":"'+arr[i]+'"}';
                    if(i<lngth-1){
                        stringIt += ',';
                    }
                }
                stringIt += ']';
                return(stringIt);
            }
        
            function checkLangs(arr){
                var lngth = arr.length;
                for(i=0; i<lngth; i++){
                    var lang=arr[i];

                    var descCont = $("#name_"+lang).val().trim();
                    if(descCont.length < 1){
                        errorMe("#name_"+lang);
                        checkVal++;
                    }else{
                        okMe("#name_"+lang);
                    }
                    
                }
            }
        
            function addCategoryMetadata(arr){
                var lngth = arr.length;
                var myLangs = "";
                
                for(i=0; i<lngth; i++){
                    var lang=arr[i];
                    var fechapub = $("#date_"+lang).val().trim();
                    var name = $("#name_"+lang).val().trim();

                    myLangs += '{"Categorymetadata":';
                    myLangs += '{"language": "'+lang+'",';
                    myLangs += '"name": "'+name+'",';
                    myLangs += '"date":"'+fechapub+'"';

                    myLangs += '}}';
                    if(i<lngth-1){
                        myLangs += ',';
                    }
                }
                return(myLangs);
            };
        
        
            function submitJson(){
                if(checkVal==0){

                    var myJSON = '';
                    myJSON+='{"Category":{';
                    myJSON+='"original_name":"'+original_name+'",';
                    myJSON+='"publicar":"'+publicar+'",';
                    myJSON+='"Categorymetadatas": [';
                    myJSON+= addCategoryMetadata(langDesc);
                    myJSON+=']}}';
                    console.log(myJSON);
                    $("#varsToJSON").val(myJSON);
                    $("#categoryForm").submit();
                  }  
            }
        
    }
    
});