

$( document ).ready(function() {
    var publicar = 0;
    var asset_Id = 0;
    var id            = "";
    var nombre        = "";
    var descripcion   = "";
    var provider      = "";
    var fecha_inicio  = "";
    var fecha_fin     = "";
    var json = {};
    var OPTION_ADD    = 1;
    var OPTION_EDIT   = 2;
    var OPTION_DELETE = 3;

    $("#btn_agregar").click(function(){
        if (validateForm()) submitJson(OPTION_ADD);

    });

    $("#btn_actualizar").click(function(){
        if (validateForm()) submitJson(OPTION_EDIT);

    });


   $("a[name='eliminar']").click(function(){
        var button = $(this);
        id = button.attr("data-id");
        submitJson(OPTION_DELETE);
    });




    /*---- DATE PICKER ----*/
    $('.datePick').dcalendarpicker({
      format: 'dd-mm-yyyy'
    });

    // activar los selects con filtro
    var $myVerifSelect = $("#canalSelect").select2();

    //VALIDACION
    function validateForm(){
        validate = true;
        nombre          = $('#nombre').val();
        descripcion     = $('#descripcion').val();
        provider        = $('#provider').val();
        fecha_inicio    = $('#fecha_inicio').val();
        fecha_fin       = $('#fecha_fin').val();
        id              = $('#codigo').val();


        // chequea original Title
        if(!nombre)
        {
            errorMe("#nombre");
            validate = false;
        }else{
            okMe("#nombre");
        }

        if(!descripcion)
        {
            errorMe("#descripcion");
            validate = false;
        }else{
            okMe("#descripcion");
        }

        if(!provider)
        {
            errorMe("#provider");
            validate = false;
        }else{
            okMe("#provider");
        }

        if(!fecha_inicio)
        {
            errorMe("#fecha_inicio");
            validate = false;
        }else{
            okMe("#fecha_inicio");
        }

        if(!fecha_fin)
        {
            errorMe("#fecha_fin");
            validate = false;
        }else{
            okMe("#fecha_fin");
        }

        return validate;
     }


function submitJson(option){
    // Setear objeto JSON
    // opcion = 1
    // opcion = 2
    url = "/api/contracts/add/";
    cartel ="Guardado Correctamente";

    if (option == OPTION_EDIT){
        url="/api/contracts/edit/";
        cartel="Actualizado Correctamente";
    }



    json= {
        "contract":{
                "id":id,
                "nombre" : nombre,
                "descripcion": descripcion,
                "provider": provider,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin
                }
     };

    $.ajax({
        url: url,
        dataType: "json",
        type: "POST",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify( json ),
        success: function(response){
                //alert(cartel);
                if (option==OPTION_DELETE){
                    $("tr[data-id='"+id+"']").fadeOut(1000);
                }
                window.location.href = "/contracts/";
            },
        error:function(request, status, error){
            alert(request.responseText);
        }
        });
    }







//Funciones Esteticas
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


});