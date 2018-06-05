$( document ).ready(function() {

    var json_data =[];
    var nombre;
    var nombre_es;
    var nombre_pt;
    var tag_id;
    var url = '';
    var urlredirect='';
    $("#getOut").click(function(){
           window.location.href = "/logout";
    });


    $("#btnguardarotro").click(function(){
        urlredirect="/tags/add";
        guardar();
    });

    /* triggers for checkALL function */
    $("#btngrabar").click(function(){
        urlredirect="/tags";
        guardar();

    });


        //CLICK BOTON ELIMINAR
    $("div[name='eliminar']").click(function(){
        var button = $(this);
        var id = button.attr("data-id");
         eliminar(id);
    });

    function eliminar(id){
        url = "/tags/delete";
        json_data = { 'id':id }

        $.ajax({
                url: url,
                dataType: 'json',
                type: 'POST',
                contentType: "application/json; charset=utf-8",
                data: JSON.stringify( json_data ),
                success: function(response){
                        //alert("Eliminado Correctamente");
                        $("tr[data-id='"+id+"']").fadeOut(1000);

                    },
                error:function(request, status, error){
                    alert(request.responseText);

                }
            });
    }



    function guardar(){
        tag_id = $("#tag_id").val();
        nombre = $("#nombre").val();
        nombre_es = $("#nombre_es").val();
        nombre_pt = $("#nombre_pt").val();
        if (validar()){

            url = '/tags/add/'
            if (tag_id.length > 0 ){
                url = '/tags/edit/'+ tag_id+'/'
            }

            json_data= {
                        "tag_id": tag_id,
                        "nombre": nombre,
                        "nombre_es": nombre_es,
                        "nombre_pt": nombre_pt

             };


            var respuesta = 0 ;
            $.ajax({
                url: url,
                dataType: 'json',
                type: 'POST',
                contentType: "application/json; charset=utf-8",
                data: JSON.stringify( json_data ),
                success: function(response){
                        alert("Guardado Correctamente");
                        window.location.href=urlredirect;
                    },
                error:function(request, status, error){
                    alert(request.responseText);

                }
            });
        }

    }

    
    function validar(){
        nombre = $("#nombre").val();

        if (nombre==""){
            alert("El Campo es Obligatorio");
            $("#nombre").focus();
            return false;
        }

        if (($("#nombre_es").val() =="") && ($("#nombre_pt").val()=="")){
            //Si no estan seleccionado algun idioma
            $("#nombre_es").focus();
            alert("Se debe Completar al menos un Idioma!");
            return false;
        }


        return true;

    }

                
        
        

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
        

        

        

    
});