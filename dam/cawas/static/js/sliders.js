
$( document ).ready(function() {

     $("#slider-select").select2({placeholder: "Despliega la lista"});
    $("#slider-edit").select2({placeholder: "Despliega la lista"});

  $('.datePick').dcalendarpicker({
      format: 'dd-mm-yyyy'
    });

    /*
    console.log( "ready!" );
    var asset_id = $("#asset_id").val();


    if(resultado=="success"){
        $("#myModal-OK").modal();
    }
    if(resultado=="error"){
        $("#myModal-ERROR").modal();
    }
    

    var countChecked = function() {
    langQ = $("input:checked" ).length;
        $('input[type=checkbox]').each(function(){
            if (this.checked) {
                langDesc.push($(this).attr("id"));
            }
        });

    };


    
    var checkedOnce = 0; //chequea si el formulario se ha intentado enviar alguna vez
    var checkVal=0; //chequea la cantidad de errores en el formulario
    var clickedToSubmit = 0; //chequea si el botón de submit se ha presionado
    var checkText="";
    var display_runtimeJSON; //necesaria para armar el valor final que debe ir en el JSON
    var langQ = 0; //Cuenta la cantidad de idiomas elegidos por el usuario
    var langDesc = [] // recoge qué idiomas son los que se seleccionaron
    var clickedVal; // recoge el valor del ID seleccionado en la lista de sliders;
    var clickedText; // recoge el nombre seleccionado en la lista de edición de sliders;
    var clickedTextID; // recoge el ID nombre seleccionado en la lista de edición de sliders;
    var hora;
    var minutos;
    // activar los selects con filtro






    // simular exit con el botón de salir
    $("#getOut").click(function(){
           window.location.href = "/logout";
    })
    
    
    
    // Toma el ID de la slider seleccionada en la lista
    $( "#slider-select" ).change(function() {
        
        $( "#slider-select option:selected" ).each(function() {
          clickedVal= $(this).val();
            if(clickedVal!="")
            {
                console.log( "clickedVal="+clickedVal ); // debug
                $( "#sliderID" ).val(clickedVal);// Agrega el ID en el input field

            }
        });
        
    });

    // Toma el nombre de la slider seleccionada en la lista
    $( "#slider-edit" ).change(function() {
        
        $( "#slider-edit option:selected" ).each(function() {
            clickedText = $(this).html();
            clickedTextID = $(this).val();
            if(clickedText!="")
            {
                $( "#sliderName" ).val(clickedText);// Agrega el ID en el input field
            }
        });
        
    });

    // simular exit con el botó de salir
    $("#EDBtn").click(function(){
        if (clickedTextID != null){
               window.location.href = "/sliders/edit/"+clickedTextID;
        }
    });
    
    // interacción del usuario al hacer click en el botón debajo de la lista de selección
    $( "#IDBtn" ).click(function(){ 
        if (clickedVal != null){
            $( "#idTit" ).html("AGREGANDO ID: "+clickedVal);// Agrega el ID en el título
            $( "#hidden1" ).show();
        }

    });

    
    // inicializar tooltips para los íconos de HELP
    $('[data-toggle="tooltip"]').tooltip(); 
    
    
    // drag and drop controles para las listas
    var adjustment;



    
    
    
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

//----------------> Helper functions

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
    
    
    //year check
    function maxLengthCheck(object)
      {
        if (object.value.length > 4)
          object.value = object.value.slice(0, 4)
      }
    

    $("#sendBut").click(function(){
        clickedToSubmit=1;
        checkAll();
    });
    
    $("body").mouseup(function(){
        if(checkedOnce>0 && checkVal>0 ){
            clickedToSubmit=0;
            checkAll();      
        }
    });
    

    function checkAll(){
        // this function checks for all form values and makes json string to post or alerts user to complete fields.
        console.log("checking form...");
        checkVal = 0;
        var asset_Id = $('#sliderID').val();
        var url = $('#url').val();
        var typeslider_selected = $('#typeslider option:selected');

        countChecked();
        // chequea original Title
        if(url=="" || url==" ")
        {
            errorMe("#url");
            checkVal++;
        }else{
            okMe("#url");
        }
        
        // chequea canal
        console.log("#typeslider"+$('#typeslider').val());

        if ( $('#typeslider').val()=="0" || $('#typeslider').val()==0)
        {
            errorMe("#typeslider");
            $(".select2-selection--single").css("border","1px #a94442 solid");
            checkVal++;
        }else{
            okMe("#typeslider");
             $(".select2-selection--single").css("border","1px #3c763d solid");
            typeslider_selected=$('#typeslider').val();
        }


        // chequeo de idiomas (tit_; desc_; date_)
        if(langQ==0){
            errorMe("#pickLang");
            checkVal++;
        }else{
            okMe("#pickLang");
            checkLangs(langDesc);
        }

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




            function checkLangs(arr){ // itera sobre los lenguajes seleccionados buscando errores
                var lngth = arr.length;
                var lenguajescargados = 0;

                var lengactualok = 1;
                for(i=0; i<lngth; i++){
                    var lang=arr[i];

                    var titCont = $("#tit_"+lang).val();
                    if(titCont==""){
                        errorMe("#tit_"+lang);
                        checkVal++;
                        lengactualok = 0;
                    }else{
                        okMe("#tit_"+lang);

                    }

                    var descCont = $("#short_desc_"+lang).val().trim();
                    if(descCont.length < 1){
                        errorMe("#short_desc_"+lang);
                        checkVal++;
                        lengactualok = 0;
                    }else{
                        okMe("#short_desc_"+lang);
                    }
                    // check date
                    var dateCont = $("#date_"+lang).val();
                    if(dateCont==""){
                        errorMe("#date_"+lang);
                        checkVal++;
                        lengactualok = 0;
                    }else{
                        okMe("#date_"+lang);
                    }


                    if (lengactualok == 1){
                        lenguajescargados = lenguajescargados + 1 ;
                    }


                    if (lenguajescargados > 0 && lengactualok > 1){
                        checkVal = 0;
                    }

                }
            }

            function addMovieMetadata(arr){
                var lngth = arr.length;
                var myLangs = "";
                
                for(i=0; i<lngth; i++){
                    var lang=arr[i];

                    var tit = $("#tit_"+lang).val();
                    var short = $("#short_desc_"+lang).val().trim().substring(0,50)+"...";
                    var long = $("#short_desc_"+lang).val().trim();
                    var fechapub = $("#date_"+lang).val().trim();
                    myLangs += '{"Moviemetadata":';
                    myLangs += '{"language": "'+lang+'",';
                    myLangs += '"title": "'+tit+'",';
                    myLangs += '"summary_short": "'+short+'",';
                    myLangs += '"summary_long":"'+long+'",';
					myLangs += '"schedule_date":"'+fechapub+'"';
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
                    myJSON+='{"Slider":{';
                    myJSON+='"asset_id":"'+asset_Id+'",';
                    myJSON+='"url":"'+original_Title+'",';
                    if (typeslider_selected=='' ||typeslider_selected='0' ){
                        myJSON+='"type_slider":null,';
                       }else{
                        myJSON+='"type_slider":"'+typeslider_selected+'",';
                    }
                    myJSON+='"Slidersmetadata": [';
                    myJSON+= addSliderMetadata(langDesc);
                    myJSON+=']}}';
                    console.log(myJSON);
                    $("#varsToJSON").val(myJSON);
                    $("#sliderForm").submit();
                  }  
            }
        
    }
    */
    
});