

$( document ).ready(function() {
    var publicar = 0;

    $('#search_girls').multiselect({
        search: {
            left: '<input type="text" name="q" class="form-control" placeholder="Buscar..." />',
            right: '<input type="text" name="q" class="form-control" placeholder="Buscar..." />',
        },
        fireSearch: function(value) {
            return value.length > 1;
        }
    });


    $('#search_category').multiselect({
        search: {
            left: '<input type="text" name="q" class="form-control" placeholder="Buscar..." />',
            right: '<input type="text" name="q" class="form-control" placeholder="Buscar..." />',
        },
        fireSearch: function(value) {
            return value.length > 1;
        }
    });


    $('#search_paises').multiselect({
        search: {
            left: '<input type="text" name="q" class="form-control" placeholder="Buscar..." />',
            right: '<input type="text" name="q" class="form-control" placeholder="Buscar..." />',
        },
        fireSearch: function(value) {
            return value.length > 1;
        }
    });


 // rellena el formulario con los datos recogidos en la variable requestedData


    $("#btnsearch").click(function(){
           $("#searchForID").submit();
    });





    var asset_id = $("#asset_id").val();
    if(asset_id != null){
        changeVideo(asset_id, "#repro1");// Cambia el video de acuerdo al ID. la función está en la línea 135. Construye la url relativa del video con la variable path+ID+'.mp4'
    };

    loadVideo("#repro1");


    if(resultado=="success"){
        $("#myModal-OK").modal();
    }
    if(resultado=="error"){
        $("#myModal-ERROR").modal();
    }
    
     /* Funcion que cuenta la cantidad de idiomas selecionados, se utiliza al momento de validar la edicion de la movie */
    var countChecked = function() {
    langQ = $("input:checked" ).length;
        $('input[type=checkbox]').each(function(){
            if (this.checked) {
                langDesc.push($(this).attr("id"));
            }
        });

    };

    $("#btngrabarypublicar").click(function(){
        $("#publicar").val("1");
        publicar = 1;
        clickedToSubmit=1;
        checkAll();
    });
    
    var checkedOnce = 0; //chequea si el formulario se ha intentado enviar alguna vez
    var checkVal=0; //chequea la cantidad de errores en el formulario
    var clickedToSubmit = 0; //chequea si el botón de submit se ha presionado
    var checkText="";
    var display_runtimeJSON; //necesaria para armar el valor final que debe ir en el JSON
    var langQ = 0; //Cuenta la cantidad de idiomas elegidos por el usuario
    var langDesc = [] // recoge qué idiomas son los que se seleccionaron
    var clickedVal; // recoge el valor del ID seleccionado en la lista de movies;
    var clickedText; // recoge el nombre seleccionado en la lista de edición de movies;
    var clickedTextID; // recoge el ID nombre seleccionado en la lista de edición de movies;
    var hora;
    var minutos;
    // activar los selects con filtro
    $("#movie-select").select2({placeholder: "Despliega la lista"});
    $("#movie-edit").select2({placeholder: "Despliega la lista"});
    var $myVerifSelect = $("#canalSelect").select2();

    // activar timepicker
    //leerRuntime();



//$("#runtime").durationPicker();

$('#runtime').mask('00:00:00',{placeholder: "HH:mm:ss"});

   // completarRuntime();

    // simular exit con el botón de salir
    $("#getOut").click(function(){
           window.location.href = "/logout";
    })
    
    
    
    // Toma el ID de la movie seleccionada en la lista
    $( "#movie-select" ).change(function() {
        
        $( "#movie-select option:selected" ).each(function() {
          clickedVal= $(this).val();
            if(clickedVal!="")
            {

                $( "#movieID" ).val(clickedVal);// Agrega el ID en el input field
                changeVideo(clickedVal, "#repro1");// Cambia el video de acuerdo al ID. la función está en la línea 135. Construye la url relativa del video con la variable path+ID+'.mp4'
                
            }
        });
        
    });
    
    // Toma el nombre de la movie seleccionada en la lista
    $( "#movie-edit" ).change(function() {
        
        $( "#movie-edit option:selected" ).each(function() {
            clickedText = $(this).html();
            clickedTextID = $(this).val();
            if(clickedText!="")
            {
                $( "#movieName" ).val(clickedText);// Agrega el ID en el input field
            }
        });
        
    });
    
    // simular exit con el botó de salir
    $("#EDBtn").click(function(){
        if (clickedTextID != null){
               window.location.href = "/movies/edit/"+clickedTextID;
        }
    });
    
    // interacción del usuario al hacer click en el botón debajo de la lista de selección
    $( "#IDBtn" ).click(function(){ 
        if (clickedVal != null){
            $( "#idTit" ).html("AGREGANDO ID: "+clickedVal);// Agrega el ID en el título
            $( "#hidden1" ).show();
        }

    })
    
    //preview de imagenes cargadas por el front end
    
    $( "#ThumbHor" ).change(showPreviewImage_click);
    $( "#ThumbVer" ).change(showPreviewImage_click);
    
    // inicializar tooltips para los íconos de HELP
    $('[data-toggle="tooltip"]').tooltip(); 
    
    
    // drag and drop controles para las listas
    var adjustment;

    

    
    /*---- DATE PICKER ----*/
    $('.datePick').dcalendarpicker({
      format: 'dd-mm-yyyy'
    });

    
    
    
    // checkbox idiomas detecta lo que se chequea y muestra el módulo de idioma
    $("input[type=checkbox]").on('change', function () {
        var self = $(this);
        var showDiv = "#Module_"+self.attr("id");
        if (self.is(":checked")) {

            $(showDiv).show('slow');
            //langQ++;
            //langDesc.push(self.attr("id"));
            
        } else {

            $(showDiv).hide('fast');
            //langQ--;
            //langDesc.pop();
        }

        if(checkedOnce>0){
            checkAll();
        }
    });
    
//----------------> Helper functions
    
    function changeVideo(src, divId){// para cambiar lo que reproduce el player de acuerdo al ID de la lista.
        path="http://cdnlevel3.zolechamedia.net/" + src + "/mp4/1200/" + src +".mp4";
        var video = $(divId+' video')[0];
        video.src = path;
        video.load();
    }

    function loadVideo(divId){
        var video = $(divId+' video')[0];
        video.load();
    }
    
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
    
    /* triggers for checkALL function */
    $("#sendBut").click(function(){
        clickedToSubmit=1;
        checkAll();
    })

    $("body").mouseup(function(){
        if(checkedOnce>0 && checkVal>0 ){
            clickedToSubmit=0;
            checkAll();      
        }
    })
    
    
    function checkAll(){
        // this function checks for all form values and makes json string to post or alerts user to complete fields.

        checkVal = 0;
        var asset_Id = $('#movieID').val();
        var original_Title = $('#orginalTitle').val();
        var canal_selected = $('#canalSelect option:selected');
        var pornstars_selected = [];
        var categories_selected = [];
        var paises_selected = [];
        var director_selected = $('#director').val();
        var elenco_selected = $('#elenco').val();
        var display_runtime = $('#runtime').val();
        var year_selected = $('#releaseYear').val();


        var json_movie = {};
        var json_moviemetadatas=[];

        countChecked();
        // chequea original Title
        if(original_Title=="" || original_Title==" ")
        {
            errorMe("#orginalTitle");
            checkVal++;
        }else{
            okMe("#orginalTitle");
        }
        // chequea thumbnail horizaontal
        if(!$('#ThumbHor').val() && !$('#imgantportrait').val()){

            errorMe("#ThumbHor");
            checkVal++;
        }else{
            okMe("#ThumbHor");
        }
        
        // chequea thumbnail vertical
        if(!$('#ThumbVer').val() && !$('#imgantlandscape').val()){
            errorMe("#ThumbVer");
            checkVal++;
        }else{
            okMe("#ThumbVer");
        }



        //search_to_girls
        if ( $('#search_girls_to option').length > 0 )
        {
            okMe("#search_girls_to");
            pornstars_selected = [];
            $('#search_girls_to option').each(function(){
               var asset_id_aux = $(this).attr("value"); //val();
               if (asset_id_aux != null){
                   pornstars_selected.push(asset_id_aux);
               }
            })

        }

        //search_category_to
        if ( $('#search_category_to option').length < 1 )
        {
            errorMe("#search_category_to");
            checkVal++;
        }else{
            okMe("#search_category_to");
            categories_selected = [];
            $('#search_category_to option').each(function(){
               var asset_id_aux = $(this).attr("value"); //val();
               if (asset_id_aux != null){
                   categories_selected.push(asset_id_aux);
               }
            })

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

        }

        // chequea canal

        if ( $('#canalSelect').val()=="0" || $('#canalSelect').val()==0)
        {
            errorMe("#canalSelect");
            $(".select2-selection--single").css("border","1px #a94442 solid");
            checkVal++;
        }else{
            okMe("#canalSelect");
             $(".select2-selection--single").css("border","1px #3c763d solid");
            canal_selected=$('#canalSelect').val();
        }

         // chequea display runtime


        if(display_runtime==""||display_runtime.length < 8)
        {
            errorMe("#runtime");
            $(".durationpicker-container").css("border","1px #a94442 solid");
            checkVal++;
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
        
            function checkLangs(arr){ // itera sobre los lenguajes seleccionados buscando errores
                var lngth = arr.length;
                var lenguajescargados = 0;

                var lengactualok = 1;
                for(i=0; i<lngth; i++){
                    var lang=arr[i];
                    /* check title */
                    var titCont = $("#tit_"+lang).val();
                    if(titCont==""){
                        errorMe("#tit_"+lang);
                        checkVal++;
                        lengactualok = 0;
                    }else{
                        okMe("#tit_"+lang);

                    }
                    /* check desc */
                    var descCont = $("#short_desc_"+lang).val().trim();
                    if(descCont.length < 1){
                        errorMe("#short_desc_"+lang);
                        checkVal++;
                        lengactualok = 0;
                    }else{
                        okMe("#short_desc_"+lang);
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

                    json_moviemetadatas.push({"Moviemetadata":{"language":lang, "title":tit, "summary_short":short, "summary_long":long, "schedule_date":fechapub}});
                }
                return(myLangs);
            };
        
        
            function submitJson(){
                if(checkVal==0){



                    var myGirls=explodeArray(pornstars_selected,"girl_id");
                    var myCategories=explodeArray(categories_selected,"category_id");
                    var myCountries=explodeArray(paises_selected,"country_id");

                    var myJSON = '';
                    myJSON+='{"Movie":{';
                    myJSON+='"asset_id":"'+asset_Id+'",';
                    myJSON+='"original_title":"'+original_Title+'",';
                    myJSON+='"channel_id":"'+canal_selected+'",';
                    myJSON+='"publicar":"'+publicar+'",';

                    if (year_selected==''){
                        myJSON+='"year":null,';
                       }else{
                        myJSON+='"year":"'+year_selected+'",';
                    }

                    if (myGirls=="[]"){
                        myJSON+='"girls":null,';
                    }else{
                        myJSON+='"girls":'+myGirls+',';
                    }
                    if (elenco_selected==''){
                        myJSON+='"cast":null,';
                    }else{
                        myJSON+='"cast":"'+elenco_selected+'",';
                    }

                    if (director_selected==''){myJSON+='"directors":null,';}else{myJSON+='"directors":"'+director_selected+'",';}

                    if (myCountries=="[]"){myJSON+='"countries":null,'; }else{myJSON+='"countries":'+myCountries+',';}

                    myJSON+='"display_runtime": "'+display_runtime+'",';
                    myJSON+='"categories":'+myCategories+',';
                    myJSON+='"Moviesmetadata": [';
                    myJSON+= addMovieMetadata(langDesc);
                    myJSON+=']}}';


                    //$("#varsToJSON").val(myJSON);


                    //Setear objeto JSON
                    json_movie= {
                        "movie":{
                                "asset_id": asset_Id,
                                "original_title" : original_Title,
                                "channel_id": canal_selected,
                                "girls": pornstars_selected,
                                "categories": categories_selected,
                                "countries": paises_selected,
                                "directors": director_selected,
                                "cast": elenco_selected,
                                "display_runtime": display_runtime,
                                "year": year_selected,
                                "publicar":publicar,
                                "moviemetadatas": []
                                }
                     };
                     //json_movie.movie.moviemetadatas.push(json_moviemetadatas);
                     $.extend(json_movie.movie.moviemetadatas, json_moviemetadatas);

                    var respuesta = 0 ;
                    //Llamada ajax

                    $.ajax({
                        url: '/api/movies/edit/',
                        dataType: 'json',
                        type: 'POST',
                        contentType: "application/json; charset=utf-8",
                        data: JSON.stringify( json_movie ),
                        success: function(response){
                                //alert("Guardado Correctamente");
                                $("#movieForm").submit();
                                console.log(response);
                            },
                        error:function(request, status, error){
                            alert(request.responseText);

                        }
                    });






                  }  
            }
        
    }
    
});