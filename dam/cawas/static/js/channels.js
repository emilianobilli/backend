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


    $('.datePick').dcalendarpicker({
      format: 'dd-mm-yyyy'
    });


    //VALIDACION
    function validateForm(){
        validate = true;
        nombre          = $('#nombre').val();
        image_logo     = $('#image_logo').val();
        image_logo_hover        = $('#image_logo_hover').val();



        // chequea original Title
        if(!nombre)
        {
            errorMe("#nombre");
            validate = false;
        }else{
            okMe("#nombre");
        }

/*
        if(!$('#image_logo').val()){
            errorMe("#image_logo");
            checkVal++;
        }else{
            okMe("#image_logo");
        }

        if(!$('#image_logo_hover').val()){
            errorMe("#image_logo_hover");
            checkVal++;
        }else{
            okMe("#image_logo_hover");
        }
        */

        return validate;
     }


function submit(option){
    if (validateForm()){
        $("#channelform").submit();
    }
}

$("#btn_agregar").click(function(){
    submit();
});


$("#btn_agregar_publicar").click(function(){
    submit();
});

























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