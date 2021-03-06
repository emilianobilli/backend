
$( document ).ready(function() {

    var dataTable = $('#example').dataTable({"sPaginationType": "full_numbers"});

    $("#slider-select").select2({placeholder: "Despliega la lista"});
    $("#slider-edit").select2({placeholder: "Despliega la lista"});

    $('.datePick').dcalendarpicker({
      format: 'dd-mm-yyyy'
    });


    $( "#ThumbHor" ).change(showPreviewImage_click);
    $( "#ThumbVer" ).change(showPreviewImage_click);
    $( "#logo" ).change(showPreviewImage_click);

    $("#btngrabarypublicar").click(function(){
        $("#publicar").val("1");
        clickedToSubmit=1;
        checkAll();
    });

    var asset_id = $("#asset_id").val();

    $("#btnsearch").click(function(){
           $("#searchForID").submit();
    });

    if(resultado=="success"){
        $("#myModal-OK").modal();
    }
    if(resultado=="error"){
        $("#myModal-ERROR").modal();
    }
    
    $( "#ThumbHor" ).change(showPreviewImage_click);

    var countChecked = function() {
    langQ = $("input:checked" ).length;
    //langDesc = null;
        $('input[type=checkbox]').each(function(){
            if (this.checked) {
                langDesc.push($(this).attr("id"));
            }
        });

    };



    $('#search_paises').multiselect({
        search: {
            left: '<input type="text" name="q" class="form-control" placeholder="Buscar..." />',
            right: '<input type="text" name="q" class="form-control" placeholder="Buscar..." />',
        },
        fireSearch: function(value) {
            return value.length > 1;
        }
    });

    
    var checkedOnce     = 0; //chequea si el formulario se ha intentado enviar alguna vez
    var checkVal        =0; //chequea la cantidad de errores en el formulario
    var clickedToSubmit = 0; //chequea si el botón de submit se ha presionado
    var checkText       ="";
    var display_runtimeJSON; //necesaria para armar el valor final que debe ir en el JSON
    var langQ           = 0; //Cuenta la cantidad de idiomas elegidos por el usuario
    var langDesc        = [] // recoge qué idiomas son los que se seleccionaron
    var clickedVal; // recoge el valor del ID seleccionado en la lista de sliders;
    var clickedText; // recoge el nombre seleccionado en la lista de edición de sliders;
    var clickedTextID; // recoge el ID nombre seleccionado en la lista de edición de sliders;
    var hora;
    var minutos;
    var TYPESLIDER_VIDEO = "video";
    var TYPESLIDER_IMAGE = "image";

    // activar los selects con filtro
    countChecked();





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

            $( "#hidden1" ).show();

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
            //langQ++;
            //langDesc.push(self.attr("id"));
            
        } else {

            console.log("Id = " + self.attr("id") + "is Unchecked ");
            $(showDiv).hide('fast');
            //langQ--;
            //langDesc.pop();
        }
        console.log("idiomas tildados:"+langQ+", y son: "+langDesc);// cantidad de idiomas
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
        var asset_Id            =$("#slider-select option:selected").attr("value");
        var linked_url          = $('#linked_url').val();
        var typeslider_selected = $('#typeslider option:selected');
        var device_selected     = $('#devices option:selected');
        var idioma_selected     = $('#idiomaSelect').val();
        var publish_date        = $('#date_blq').val();
        var text                = $("#text").val();
        var videoname           = $("#videoname").val();
        var publicar            = $('#publicar').val();
        var paises_selected = [];


        //VAlidar si url y asset_id es vacio, error
        if ((asset_Id=="0" ||asset_Id=="" ) && (linked_url==""||linked_url==" ")){
             errorMe("#slider-select");
             errorMe("#linked_url");
             checkVal++;
        }else{
            okMe("#slider-select");
            okMe("#linked_url");
        }



        //Valida idioma
        if (idioma_selected =="0" || idioma_selected ==""){
            errorMe("#idiomaSelect");
            checkVal++;
        }else{
            okMe("#idiomaSelect");
            idioma_selected=$('#idiomaSelect').val();
        }


        //search_to_paises - No es obligatorio
        if ( $('#search_paises_to option').length > 0 )
        {
            okMe("#search_paises_to");
            paises_selected = [];
            $('#search_paises_to option').each(function(){
               var asset_id_aux = $(this).attr("value"); //val();
               if (asset_id_aux != null){
                   paises_selected.push(asset_id_aux);
               }
            })
            console.log("search_paises_to_selected:"+paises_selected);
        }


        // chequea TYPESLIDER
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

        // Validar si tipo de Slider es Video entonces es obligatorio completar el Nombre del video
        if ( $('#typeslider').val() == TYPESLIDER_VIDEO ){
            if (videoname == "" || videoname == null){
                 errorMe("#videoname");
                 checkVal++;
             }
        }else{
            okMe("#videoname");
        }

        // Validar si es Slider IMAGE, la imagen es Obligatoria
        if ( $('#typeslider').val() == TYPESLIDER_IMAGE ){
            if(!$('#ThumbHor').val() && !$('#imgantlandscape').val()){
                errorMe("#ThumbHor");
                checkVal++;
            }else{
                okMe("#ThumbHor");
            }
        }else{
            okMe("#ThumbHor");
        }






        // chequea DEVICES
        console.log("#devices"+$('#devices').val());
        if ( $('#devices').val()=="0" || $('#devices').val()==0)
        {
            errorMe("#devices");
            $(".select2-selection--single").css("border","1px #a94442 solid");
            checkVal++;
        }else{
            okMe("#devices");
             $(".select2-selection--single").css("border","1px #3c763d solid");
            device_selected=$('#devices').val();
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


            function addSliderMetadata(arr){
                var lngth = arr.length;
                var myLangs = "";

                for(i=0; i<lngth; i++){
                    var lang=arr[i];
                    var fechapub = $("#date_"+lang).val().trim();
                    myLangs += '{"Slidermetadata":';
                    myLangs += '{"language": "'+lang+'",';

                    if (text==''){
                        myLangs+='"text":null,';
                       }else{
                        myLangs+='"text":"'+text+'",';
                    }

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
                    var myCountries=explodeArray(paises_selected,"country_id");

                    var myJSON = '';
                    myJSON+='{"Slider":{';
                    myJSON+='"asset_id":"'+asset_Id+'",';
                    if (text=='' ){myJSON+='"text":"",';}else{myJSON+='"text":"'+text+'",';}
                    if (videoname=='' ){myJSON+='"videoname":"",';}else{myJSON+='"videoname":"'+videoname+'",';}
                    if (myCountries=="[]"){myJSON+='"countries":null,'; }else{myJSON+='"countries":'+myCountries+',';}

                    myJSON+='"publish_date":"'+publish_date+'",';
                    myJSON+='"language":"'+idioma_selected+'",';
                    myJSON+='"media_type":"'+typeslider_selected+'",';
                    if (linked_url==''){ myJSON+='"linked_url":"",'; }else{myJSON+='"linked_url":"'+linked_url+'",';}

                    myJSON+='"target_device_id":"'+device_selected+'",';
                    myJSON+='"publicar":"'+publicar+'",';
                    if (typeslider_selected=='' ){
                        myJSON+='"type_slider":null';
                       }else{
                        myJSON+='"type_slider":"'+typeslider_selected+'"';
                    }
                    //myJSON+='"Slidermetadatas":[';
                    //myJSON+= addSliderMetadata(langDesc);

                    //myJSON+=']}}';
                    myJSON+='}}';
                    console.log(myJSON);
                    $("#varsToJSON").val(myJSON);
                    $("#sliderForm").submit();
                  }  
            }

        
    }

    
});