$( document ).ready(function() {
    
    console.log( "ready!" );
    
    if(resultado=="success"){
        $("#myModal-OK").modal();
    }
    if(resultado=="error"){
        $("#myModal-ERROR").modal();
    }
    
     $("#btnsearch").click(function(){
           $("#searchForID").submit();
    });

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
    
    // activar los selects con filtro
    
    $("#serie-edit").select2({placeholder: "Despliega la lista"});
    var $myVerifSelect = $("#canalSelect").select2();
    
    
    
    // simular exit con el botón de salir
    $("#getOut").click(function(){
           window.location.href = "/logout";
    })
    
    
    
        
    // Toma el nombre de la movie seleccionada en la lista
    $( "#serie-edit" ).change(function() {
        
        $( "#serie-edit option:selected" ).each(function() {
            clickedText = $(this).html();
            clickedTextID = $(this).val();
            if(clickedText!="")
            {
                $( "#serieName" ).val(clickedText);// Agrega el ID en el input field
                               
            }
        });
        
    });
    
    // simular exit con el botón de salir
    $("#EDBtn").click(function(){
           //window.location.href = "series-edit.html?ID="+clickedTextID;
           window.location.href = "/series/edit/"+clickedTextID;
    })
    
    // interacción del usuario al hacer click en el botón debajo de la lista de selección
    $( "#IDBtn" ).click(function(){ 
        $( "#idTit" ).html("AGREGANDO ID: "+clickedVal);// Agrega el ID en el título
        $( "#hidden1" ).show();
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
    
    
    /**/
    $("ul.generoPick").sortable({
      group: 'generoPick',
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
    
    
    /*---- DATE PICKER 
    $('.datePick').dcalendarpicker({
     // default: mm/dd/yyyy

      format: 'dd-mm-yyyy'

    });----*/

    
    
    
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
        path="video/";
        var video = $(divId+' video')[0];
        video.src = path+src+".mp4";
        console.log(video.src);
        video.load();
        video.play();
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
    
     /* Funcion que cuenta la cantidad de idiomas selecionados, se utiliza al momento de validar la edicion de la movie */
    var countChecked = function() {
    langQ = $("input:checked" ).length;
        $('input[type=checkbox]').each(function(){
            if (this.checked) {
                langDesc.push($(this).attr("id"));
            }
        });

    };

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
        if(!$('#ThumbHor').val() && !$('#imgantlandscape').val()){
            errorMe("#ThumbHor");
            checkVal++;
        }else{
            okMe("#ThumbHor");
        }
        
        // chequea thumbnail vertical
        if(!$('#ThumbVer').val()&& !$('#imgantportrait').val()){
            errorMe("#ThumbVer");
            checkVal++;
        }else{
            okMe("#ThumbVer");
        }
        
        // chequea pornstar
        if ( $('#pornstarDrop li').length < 1 )
        {
            errorMe("#pornstarDrop");
            checkVal++;
        }else{
            okMe("#pornstarDrop");
            pornstars_selected = [];
            $('#pornstarDrop li').each(function(){
               pornstars_selected.push($(this).val());
            })
            //console.log("pornstars_selected:"+pornstars_selected)
        }
        
        // chequea categorías
        if ( $('#generoDrop li').length < 1 )
        {
            errorMe("#generoDrop");
            checkVal++;
        }else{
            okMe("#generoDrop");
            categories_selected = [];
            $('#generoDrop li').each(function(){
              categories_selected.push($(this).val());
            })
            console.log("generoDrop:"+categories_selected)
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
        
        // chequea director
        if(director_selected=="" || director_selected==" ")
        {
            errorMe("#director");
            checkVal++;
        }else{
            okMe("#director");
        }
        
        // chequea año de estreno
        if(year_selected=="" || year_selected==" ")
        {
            errorMe("#releaseYear");
            checkVal++;
        }else{
            okMe("#releaseYear");
        }
        
        
        
        // chequea elenco
        if(elenco_selected=="" || elenco_selected==" ")
        {
            errorMe("#elenco");
            checkVal++;
        }else{
            okMe("#elenco");
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
                for(i=0; i<lngth; i++){
                    var lang=arr[i];
                    /* check title */
                    var titCont = $("#tit_"+lang).val();
                    if(titCont==""){
                        errorMe("#tit_"+lang);
                        checkVal++;
                    }else{
                        okMe("#tit_"+lang);
                    }
                    /* check desc */
                    var descCont = $("#short_desc_"+lang).val().trim();
                    if(descCont.length < 1){
                        errorMe("#short_desc_"+lang);
                        checkVal++;
                    }else{
                        okMe("#short_desc_"+lang);
                    }
                    
                }
            }
        
            function addSerieMetadata(arr){
                var lngth = arr.length;
                var myLangs = "";
                
                for(i=0; i<lngth; i++){
                    var lang=arr[i];
                    
                    var tit = $("#tit_"+lang).val();
                    var short = $("#short_desc_"+lang).val().trim();
                    var long = $("#short_desc_"+lang).val().trim();
                    myLangs += '{"Seriemetadata":';
                    myLangs += '{"language": "'+lang+'",';
                    myLangs += '"title": "'+tit+'",';
                    myLangs += '"summary_short": "'+short+'",';
                    myLangs += '"summary_long":"'+long+'"';
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
                    myJSON+='{"Serie":{';
                    myJSON+='"asset_id":"'+asset_Id+'",';
                    myJSON+='"original_title":"'+original_Title+'",';
                    myJSON+='"channel_id":"'+canal_selected+'",';
                    myJSON+='"year":'+year_selected+',';
                    myJSON+='"cast":"'+elenco_selected+'",';
                    myJSON+='"directors":"'+director_selected+'",';
                    myJSON+='"girls":'+myGirls+',';                    
                    myJSON+='"categories":'+myCategories+',';
                    myJSON+='"publicar":"'+publicar+'",';
                    myJSON+='"Seriemetadatas": [';
                    myJSON+= addSerieMetadata(langDesc);
                    myJSON+=']}}';
                    console.log(myJSON);
                    $("#varsToJSON").val(myJSON);
                    $("#serieForm").submit();
                  }  
            }
        
    }
    
});