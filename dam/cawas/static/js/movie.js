
$( document ).ready(function() {


    $('#search_girls').multiselect({
        search: {
            left: '<input type="text" name="q" class="form-control" placeholder="Buscar..." />',
            right: '<input type="text" name="q" class="form-control" placeholder="Buscar..." />',
        },
        fireSearch: function(value) {
            return value.length > 3;
        }
    });


$('#search_category').multiselect({
        search: {
            left: '<input type="text" name="q" class="form-control" placeholder="Buscar..." />',
            right: '<input type="text" name="q" class="form-control" placeholder="Buscar..." />',
        },
        fireSearch: function(value) {
            return value.length > 3;
        }
    });


 // rellena el formulario con los datos recogidos en la variable requestedData


    $("#btnsearch").click(function(){
           $("#searchForID").submit();
    });




    console.log( "ready!" );
    var asset_id = $("#asset_id").val();
    if(asset_id != null){
        changeVideo(asset_id, "#repro1");// Cambia el video de acuerdo al ID. la función está en la línea 135. Construye la url relativa del video con la variable path+ID+'.mp4'
    };

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
                console.log( "clickedVal="+clickedVal ); // debug
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
    })
    
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

    $("ul.pornstarPick").sortable({
      group: 'pornstarPick',
      pullPlaceholder: false,
      // animation on drop
      onDrop: function  ($item, container, _super) {
        var $clonedItem = $('<li/>').css({height: 0});
        $item.before($clonedItem);
        $clonedItem.animate({'height': $item.height()});

        $item.animate($clonedItem.position(), function  () {
          $clonedItem.detach();
          _super($item, container);
        });
      },

      // set $item relative to cursor position
      onDragStart: function ($item, container, _super) {
        var offset = $item.offset(),
            pointer = container.rootGroup.pointer;

        adjustment = {
          left: pointer.left - offset.left,
          top: pointer.top - offset.top
        };

        _super($item, container);
      },
      onDrag: function ($item, position) {
        $item.css({
          left: position.left - adjustment.left,
          top: position.top - adjustment.top
        });
      }
    });
    
    

    
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
    
//----------------> Helper functions
    
    function changeVideo(src, divId){// para cambiar lo que reproduce el player de acuerdo al ID de la lista.
        path="http://cdnlevel3.zolechamedia.net/" + src + "/mp4/1200/" + src +".mp4";
        var video = $(divId+' video')[0];
        //http://cdnlevel3.zolechamedia.net/{asset_id}/mp4/350/{asset_id}.mp4
        video.src = path;
        console.log(video.src);
        video.load();
        //video.play();
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
        console.log("checking form...");
        checkVal = 0;
        var asset_Id = $('#movieID').val();
        var original_Title = $('#orginalTitle').val();
        var canal_selected = $('#canalSelect option:selected');
        var pornstars_selected = [];
        var categories_selected = [];
        var director_selected = $('#director').val();
        var elenco_selected = $('#elenco').val();
        var display_runtime = $('#runtime').val();
        var year_selected = $('#releaseYear').val();
        var publicar = $('#publicar').val();


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
            console.log("search_girls_to_selected:"+pornstars_selected);
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
            console.log("search_girls_to_selected:"+categories_selected);
        }







        // chequea canal
        console.log("#canalSelect"+$('#canalSelect').val());
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

/*
        if(display_runtime=="" || display_runtime=="0:,0")
        {
            errorMe("#runtime");
            $(".durationpicker-container").css("border","1px #a94442 solid");
            checkVal++;
        }else{
            console.log("display:runtime"+display_runtime);
            $(".durationpicker-container").css("border","1px #3c763d solid");
            var myStrRuntime = display_runtime;
            var myDirtyRuntime = myStrRuntime.split(",");
            display_runtimeJSON=myDirtyRuntime[0]+myDirtyRuntime[1];
            okMe("#runtime");
        }
*/

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
                }
                return(myLangs);
            };
        
        
            function submitJson(){
                if(checkVal==0){
                    var myGirls=explodeArray(pornstars_selected,"girl_id");
                    var myCategories=explodeArray(categories_selected,"category_id");
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
                    if (director_selected==''){
                        myJSON+='"directors":null,';
                       }else{
                        myJSON+='"directors":"'+director_selected+'",';
                    }
                    myJSON+='"display_runtime": "'+display_runtime+'",';
                    myJSON+='"categories":'+myCategories+',';
                    myJSON+='"Moviesmetadata": [';
                    myJSON+= addMovieMetadata(langDesc);
                    myJSON+=']}}';
                    console.log(myJSON);
                    $("#varsToJSON").val(myJSON);
                    $("#movieForm").submit();
                  }  
            }
        
    }
    
});