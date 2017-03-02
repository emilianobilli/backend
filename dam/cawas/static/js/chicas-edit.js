// La anteúltima línea es la que invoca a la función para llenar el formulario.
// la variable debajo de este texto (requestedData) es el JSON que sirve de datapool.
// Los datos se envían por POST a movies.html... chequear eso!!!!

var requestedData={"Girl":
	{	
		"asset_id":"G01245",
		"type":"playmate",
		"name":"nombre de la actriz 22",
		"birth_date": "02/03/1988",
		"height": "150",
		"weight": "70",
		"Girlmetadatas":[
							{"Girlmetadata":{
											"language": "pt",
											"description": "descripcion 2 portugues",
											"nationality": "nationality 1  "
											}
							},
                            {"Girlmetadata":{
											"language": "es",
											"description": "descripcion 2 espa",
											"nationality": "nationality 1  "
											}
							}
						]
	}
}


   



// helper para populateForm(), dependiendo del tipo de tag, llena un valor en un input, un string, select o agrega texto.
    function insertIt(id,valueSent,method){
        switch(method){
                case "html":
                    $(id).html(valueSent);
                break;
                case "val":
                    $(id).val(valueSent);
                break;
                case "append":
                    $(id).append(valueSent);
                break;
                case "select":
                    //id='"'+id+' option[value='+valueSent+']"';
                    //console.log("id"+id);
                    //$(id).attr('selected','selected');
                    $(id).val(valueSent).change();
                break;
                default:
                break;
        }
        
    }

    function insertIdiomas(cant){
        var checkIdvar;
        for(i=0; i<cant; i++){
            var lang=requestedData.Girl.Girlmetadatas[i].Girlmetadata.language;
                
            $("#"+lang).prop('checked', true);
            $("#"+lang).change();
            $("#Module_"+lang).show();
            $("#short_desc_"+lang).val(requestedData.Girl.Girlmetadatas[i].Girlmetadata.description);
            $("#nacionalidad_"+lang).val(requestedData.Girl.Girlmetadatas[i].Girlmetadata.nationality);
            //langQ++
            /*$("#date_"+lang).val(makeToday());*/
        }
        
        
    }

    function searchList(theList,val){
        //console.log("estoy buscando esto:"+val+" en:"+theList);
        var theAnswer;
        $(theList).find('li').each(function(){
         //console.log("ahora estoy en:"+$(this).val()+" y busco:"+val)  
            if($(this).val()==val){
                theAnswer=$(this).html();
                console.log("and the winner is:"+theAnswer);
                $(this).remove();//quita de la lista original el valor que viene el JSON
            }
        });
        return(theAnswer);
    }

    function makelist(iddrop,idpick,valuesOf,theObject){
        
        var myArrayOfValues = valuesOf;
        var ArrLngth = myArrayOfValues.length;        
        var htmlContent = "";
        for(i=0; i<ArrLngth; i++){
            if(theObject==".girl_id"){
             var theRealValue = myArrayOfValues[i].girl_id;
            }
            if(theObject==".category_id"){
             var theRealValue = myArrayOfValues[i].category_id;
            }
            console.log("theRealValue"+theRealValue);
            var listVal = searchList(idpick,theRealValue);
            console.log("listVal after function is"+listVal);
            htmlContent+= "<li value='"+theRealValue+"'>"+listVal+"</li>"
        }
        $(iddrop).html(htmlContent);
    }

    function makeToday(){
        var today = new Date();
        var dd = today.getDate();
        var mm = today.getMonth()+1; //January is 0!

        var yyyy = today.getFullYear();
        if(dd<10){
            dd='0'+dd;
        } 
        if(mm<10){
            mm='0'+mm;
        } 
        var today = dd+'/'+mm+'/'+yyyy;
        return(today);
    }
    
    // rellena el formulario con los datos recogidos en la variable requestedData
    function populateForm(){
        
        var qIdiomas = requestedData.Girl.Girlmetadatas.length;
        
        //id
        //insertIt("#idTit", requestedData.Movie.asset_id, "append");
        //name
        insertIt("#orginalName", requestedData.Girl.name, "val");
        //birthdate
        insertIt("#birthDate", requestedData.Girl.birth_date, "val");
        //Altura
        insertIt("#height", requestedData.Girl.height, "val");
        //Peso
        insertIt("#weight", requestedData.Girl.weight, "val");
        
        
        //categoría
        insertIt("#category", requestedData.Girl.type, "select");
                
        //idiomas
        insertIdiomas(qIdiomas)
        //console.log("qIdiomas:"+qIdiomas);
        
    }

$( document ).ready(function() {
    
    var checkedOnce = 0; //chequea si el formulario se ha intentado enviar alguna vez
    var checkVal=0; //chequea la cantidad de errores en el formulario
    var clickedToSubmit = 0; //chequea si el botón de submit se ha presionado
    var checkText="";
    var display_runtimeJSON; //necesaria para armar el valor final que debe ir en el JSON
    var langQ = 0; //Cuenta la cantidad de idiomas elegidos por el usuario
    var langDesc = [] // recoge qué idiomas son los que se seleccionaron
    var clickedVal; // recoge el valor del ID seleccionado en la lista de chcas;
    var clickedName; // recoge el valor del Nombre seleccionado en la lista de chcas;

    
    console.log( "ready!" );
    // inicializar tooltips para los íconos de HELP
    $('[data-toggle="tooltip"]').tooltip(); 
    
    
    
    
    // activar los selects con filtro
    $("#chica-select").select2({placeholder: "Despliega la lista"});
    
    // simular exit con el botón de salir
    $("#getOut").click(function(){
           window.location.href = "index.html?logstatus=OFF";
    })
    
    
    
    // interacción del usuario al hacer click en el botón debajo de la lista de selección
    $( "#IDBtn" ).click(function(){ 
        $( "#chica-pickerForm" ).submit();// Envía el formulario con el id de la chica
    })
    
    // interacción del usuario al hacer click en el botón de agregar chicas
    $( "#ADBtn" ).click(function(){ 
         $( "#hidden1" ).show();
    })  
    
    // interacción del usuario al hacer click en el botón cancelar
    $( "#CancelBtn" ).click(function(){ 
         window.location.href = "chicas.html";
    }) 
    
    
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
    $('#birthDate').dcalendarpicker({
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
        var original_name = $('#orginalName').val();
        var category_selected = $('#category option:selected');
        var birth_date = $('#birthDate').val().trim();
        var girl_height = $('#height').val();
        var girl_weight = $('#weight').val();
        
        
        // chequea original Name
        if(original_name=="" || original_name==" ")
        {
            errorMe("#orginalName");
            checkVal++;
        }else{
            okMe("#orginalName");
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
        
        // chequea birthDate
        if(birth_date=="" || birth_date==" ")
        {
            errorMe("#birthDate");
            checkVal++;
        }else{
            okMe("#birthDate");
        }
        
        // chequea girl_height
        if(girl_height=="" || girl_height==" ")
        {
            errorMe("#height");
            checkVal++;
        }else{
            okMe("#height");
        }
        
        // chequea girl_weight
        if(girl_weight=="" || girl_weight==" ")
        {
            errorMe("#weight");
            checkVal++;
        }else{
            okMe("#weight");
        }
        
        
        // chequea categoria
        console.log("#category"+$('#category').val());
        if ( $('#category').val()=="0" || $('#category').val()==0)
        {
            errorMe("#category");
            checkVal++;
        }else{
            okMe("#category");
            category_selected=$('#category').val();
        }
        
        
        
        // chequeo de idiomas (tit_; desc_; date_)
        console.log("langQ vale: "+langQ);
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
        
            function addGirlMetadata(arr){
                var lngth = arr.length;
                var myLangs = "";
                
                for(i=0; i<lngth; i++){
                    var lang=arr[i];
                    var nacion = $("#nacionalidad_"+lang).val().trim()
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
                    
                    var myJSON = '';
                    myJSON+='{"Girl":{';
                    myJSON+='"type_girl":"'+category_selected+'",';
                    myJSON+='"name":"'+original_name+'",';
                    myJSON+='"birth_date":'+birth_date+',';
                    myJSON+='"height":'+girl_height+',';
                    myJSON+='"weight":"'+girl_weight+'",';
                    myJSON+='"Girlmetadatas": [';
                    myJSON+= addGirlMetadata(langDesc);
                    myJSON+=']}}';
                    console.log(myJSON);
                    $("#varsToJSON").val(myJSON);
                    $("#girlForm").submit();
                  }  
            }
        
    }
    populateForm();
});