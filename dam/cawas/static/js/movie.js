$( document ).ready(function() {
    
    console.log( "ready!" );
    var checkedOnce = 0; //chequea si el formulario se ha intentado enviar alguna vez
    var checkVal=0; //chequea la cantidad de errores en el formulario
    var clickedToSubmit = 0; //chequea si el botón de submit se ha presionado
    var checkText="";
    var clickedVal; // recoge el valor del ID seleccionado en la lista de movies;
    
    // simular exit con el botó de salir
    $("#getOut").click(function(){
           window.location.href = "index.html?logstatus=OFF";
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
    
    
    /*---- DATE PICKER ----*/
    $('.datePick').dcalendarpicker({
     // default: mm/dd/yyyy

      format: 'dd-mm-yyyy'

    });

    
    
    
    // checkbox idiomas detecta lo que se chequea y muestra el módulo de idioma
    $("input[type=checkbox]").on('change', function () {
        var self = $(this);
        var showDiv = "#Module_"+self.attr("id");
        if (self.is(":checked")) {
            console.log("checkbox  id =" + self.attr("id") + "is checked ");
            $(showDiv).show('slow');
        } else {
            console.log("Id = " + self.attr("id") + "is Unchecked ");
            $(showDiv).hide('fast');
        }
        
    });
    
//----------------> Helper functions
    
    function changeVideo(src, divId){// para cambiar lo que reproduce el player de acuerdo al ID de la lista.
        path="http://cdnlevel3.zolechamedia.net/" + src + "/mp4/350/" + src +".mp4";
        var video = $(divId+' video')[0];
        //http://cdnlevel3.zolechamedia.net/{asset_id}/mp4/350/{asset_id}.mp4
        video.src = path;
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
        var canal_selected;
        var director_selected = $('#director').val();
        var elenco_selected = $('#elenco').val();
        var year_selected = $('#releaseYear').val();
        
        // chequea original Title
        if(original_Title=="" || original_Title==" ")
        {
            errorMe("#orginalTitle");
            checkVal++;
        }else{
            okMe("#orginalTitle");
        }
        // chequea thumbnail horizaontal
        if(!$('#ThumbHor').val()){
            errorMe("#ThumbHor");
            checkVal++;
        }else{
            okMe("#ThumbHor");
        }
        
        // chequea thumbnail vertical
        if(!$('#ThumbVer').val()){
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
        }
        
        // chequea categorías
        if ( $('#generoDrop li').length < 1 )
        {
            errorMe("#generoDrop");
            checkVal++;
        }else{
            okMe("#generoDrop");
        }
        
        // chequea canal
        if ( $('#canalSelect').val()=="")
        {
            errorMe("#canalSelect");
            checkVal++;
        }else{
            okMe("#canalSelect");
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
        
        // checkboxes
        /*
        $('.chkbx').each(function () {
            var checkBox = $(this);
            if (checked) {
                checkBox.prop('checked', true);
            } else {
                checkBox.prop('checked', false);
                alert("chequeame una maestro")
            }
        });
        */
        
        
        
        
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
                    myJSON+='{"Movie":{';
                    myJSON+='"asset_id":"'+asset_Id+'",';
                    myJSON+='"original_title":"'+original_Title+'",';
                    myJSON+='"channel_id":"2",';
                    myJSON+='"year":'+year_selected+',';
                    myJSON+='"girls": [{"girl_id":"1"},{"girl_id":"2"}],';
                    myJSON+='"cast":"'+elenco_selected+'",';
                    myJSON+='"directors":"'+director_selected+'",';
                    myJSON+='"display_runtime": "20:30",';
                    myJSON+='"categories": [{"category_id":"1"},{"category_id":"2"}],';
                    myJSON+='"Moviesmetadata": [{"Moviemetadata":';
                    myJSON+='{"language": "es",';
                    myJSON+='"title": "title 1 español",';
                    myJSON+='"summary_short": "summary_short 1 ",';
                    myJSON+='"summary_long":"summary_long 1 "}},';
                    myJSON+='{"Moviemetadata":{"language": "pt",';
                    myJSON+='"title": "title 2 portugues",';
                    myJSON+='"summary_short": "summary_short 2 ",';
                    myJSON+='"summary_long":"summary_long 2 "}}'; 
                    myJSON+=']}}';
                    console.log(myJSON);
                    $("#varsToJSON").val(myJSON);
                    $("#movieForm").submit();
                  }  
            }
        
    }
    
});