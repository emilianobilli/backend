$( document ).ready(function() {


    $('#search').multiselect({
        search: {
            left: '<input type="text" name="q" class="form-control" placeholder="Buscar..." />',
            right: '<input type="text" name="q" class="form-control" placeholder="Buscar..." />',
        },
        fireSearch: function(value) {
            return value.length > 3;
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
    var $mySerieSelect = $("#serie-id").select2();

    // activar los selects con filtro
    $("#bloque-select").select2({placeholder: "Despliega la lista"});

    $("#btngrabarypublicar").click(function(){
        $("#publicar").val("1");
        clickedToSubmit=1;
        checkAll();
    });
    
    // simular exit con el botón de salir
    $("#getOut").click(function(){
           window.location.href = "/logout";
    });

    $("#btnsearch").click(function(){
           $("#searchForID").submit();
    });

     // simular exit con el botó de salir
    $("#IDBtn").click(function(){
        if (clickedVal != null){
               window.location.href = "/blocks/edit/"+clickedVal;
        }
    });



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

    
    // interacción del usuario al hacer click en el botón de agregar chicas
    $( "#ADBtn" ).click(function(){ 
         $( "#hidden1" ).show();
    })  
    
    // interacción del usuario al hacer click en el botón cancelar
    $( "#CancelBtn" ).click(function(){ 
         $( "#hidden1" ).hide();
    }) 
    
    // drag and drop controles para las listas
    var adjustment;

    $("ul.assetPick").sortable({
      group: 'assetPick',
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
    $('#date_blq').dcalendarpicker({
     // default: mm/dd/yyyy

      format: 'dd-mm-yyyy'

    });

    
    
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
        var block_id = $('#block_id').val();
        var asset_Id = $('#asset_id').val();
        var original_name = $('#orginalName').val();
        var idioma_selected = $('#idiomaSelect').val();
        var canal_selected = $('#canalSelect').val();
        var publish_date = $('#date_blq').val().trim();
        var device_selected = $('#deviceSelect').val();
        var asset_selected = [];
        var paises_selected = [];
        var publicar = $('#publicar').val();
        var order = $('#order').val();


        // Order
        if(order=="" || order==" ")
        {
            errorMe("#order");
            checkVal++;
        }else{
            okMe("#order");
        }

        // chequea original Name
        if(original_name=="" || original_name==" ")
        {
            errorMe("#orginalName");
            checkVal++;
        }else{
            okMe("#orginalName");
        }

        if ( $('#serie-id').val()=="0" || $('#serie-id').val()==0)
        {
            errorMe("#serie-id");
            checkVal++;
        }else{
            okMe("#serie-id");
            serie_selected=$('#serie-id').val();
        }

        
        // chequea idioma
        if (idioma_selected =="0" || idioma_selected ==""){
            errorMe("#idiomaSelect");
            checkVal++;
        }else{
            okMe("#idiomaSelect");
            idioma_selected=$('#idiomaSelect').val();
        }
        
        

        
        // chequea publish_date
        if(publish_date=="" || publish_date==" ")
        {
            errorMe("#date_blq");
            checkVal++;
        }else{
            okMe("#date_blq");
        }
        
        // chequea dispositivo
        if (device_selected =="0" || device_selected ==""){
            errorMe("#deviceSelect");
            checkVal++;
        }else{
            okMe("#deviceSelect");
            device_selected=$('#deviceSelect').val();
        }
        
         // chequea assets
        if ( $('#search_to option').length < 1 )
        {
            errorMe("#search_to");
            checkVal++;
        }else{
            okMe("#search_to");
            asset_selected = [];
            $('#search_to option').each(function(){
               var asset_id_aux = $(this).attr("value"); //val();
               if (asset_id_aux != null){
                   asset_selected.push(asset_id_aux);
               }
            })
            console.log("search_to_selected:"+asset_selected);
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
                    /* check nacionalidad */
                    var titCont = $("#nacionalidad_"+lang).val();
                    if(titCont==""){
                        errorMe("#nacionalidad_"+lang);
                        checkVal++;
                    }else{
                        okMe("#nacionalidad_"+lang);
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
        
            function addAssetMetadata(arr){
                var lngth = arr.length;
                var myLangs = "";
                
                for(i=0; i<lngth; i++){
                    var lang=arr[i];
                    var assetID = $("#asset_id").val().trim()
                    var short = $("#short_desc_"+lang).val().trim();
                    myLangs += '{"Girlmetadata":';
                    myLangs += '{"language": "'+lang+'",';
                    myLangs += '"description": "'+short+'",';
                    myLangs += '"nationality":"'+nacion+'"';
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
                    myJSON+='{"Block":{';
                    myJSON+='"block_id":"'+block_id+'",';
                    myJSON+='"name":"'+original_name+'",';
                    myJSON+='"language":"'+idioma_selected+'",';
                    if (canal_selected==''){
                        myJSON+='"channel_id":null,';
                       }else{
                        myJSON+='"channel_id":"'+canal_selected+'",';
                    }

                    if (myCountries=="[]"){myJSON+='"countries":null,'; }else{myJSON+='"countries":'+myCountries+',';}

                    myJSON+='"publish_date":"'+publish_date+'",';
                    myJSON+='"target_device_id":"'+device_selected+'",';
                    myJSON+='"publicar":"'+publicar+'",';
                    myJSON+='"order":'+order+', ';
                    myJSON+='"assets": ';
                    myJSON+= explodeArray(asset_selected, "asset_id");
                    myJSON+='}}';
                    console.log(myJSON);
                    $("#varsToJSON").val(myJSON);
                    $("#assetForm").submit();
                  }  
            }
        
    }
    
});