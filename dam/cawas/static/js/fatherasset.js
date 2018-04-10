

$( document ).ready(function() {

    var publicar = 0;
    var asset_Id = 0;
    var id            = "";
    var asset_id      = "";
    var contracts      = "";
    var arrival_date  = "";
    var duration      = "";
    var json          = {};
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


    $('#duration').mask('00:00:00',{placeholder: "HH:mm:ss"});

    $("#contracts").select2({placeholder: "Despliega la lista"});


    var $myVerifSelect = $("#canalSelect").select2();

    loadForm();
    listFormatDuration();






function loadForm(){
    var dur        = $("#duration");
    var segundos   = dur.attr("data") ;
    segundosFormat = toSecString(segundos);
    dur.val(segundosFormat);


}

function listFormatDuration(){
   $("td[name='cellduration']").each(function() {
        var tdin = $(this);
        timein = tdin.attr("data");
        tdin.html(toSecString(timein));
    });
}

function getSecToString(val){
    //El valor recibido esta formateado de la siguiente manera 00:00:00
    //separar el string por :
    //multiplicar string hora x 3600
    //multiplicar string minutos x 60
    //segundos x 1
    var stringHora = parseInt(val.substring(0,2));
    var stringMin = parseInt(val.substring(3,5));
    var stringSec = parseInt(val.substring(6,8));
    var segundosTotales = (stringHora * 3600) + (stringMin*60) + stringSec;
    return segundosTotales;

}


function toSecString(val)
    {
        mint = Math.floor(val/60);
        seg = Math.floor(val % 60);
        hora =  Math.floor(mint/60);
        min = Math.floor(mint % 60);

        strmin = min.toString();
        strseg = seg.toString();
        strhora = hora.toString();

        if (hora < 10 ){
            strhora = "0" + hora.toString();
        }
        if (min < 10 ){
            strmin = "0" + min.toString();
        }
        if (seg < 10){
            strseg = "0" + seg.toString();
        }
        strformat = strhora.toString() + ":" + strmin.toString() + ":" + strseg.toString();
        return strformat;

    }



    //VALIDACION========================================================================================================
    function validateForm(){
        validate = true;
        asset_id        = $('#asset_id').val();
        contracts       = $('#contracts').val();
        arrival_date    = $('#arrival_date').val();
        duration        = getSecToString($('#duration').val());
        id              = $('#codigo').val();

        // chequea original Title
        if(!asset_id)
        {
            errorMe("#asset_id");
            validate = false;
        }else{
            okMe("#asset_id");
        }


        if(!contracts)
        {
            errorMe("#contracts");
            validate = false;
        }else{
            okMe("#contracts");
        }


        if(!arrival_date)
        {
            errorMe("#arrival_date");
            validate = false;
        }else{
            okMe("#arrival_date");
        }

        if(!duration)
        {
            errorMe("#duration");
            validate = false;
        }else{
            okMe("#duration");
        }



        return validate;
     }


function submitJson(option){
    // Setear objeto JSON
    // opcion = 1
    // opcion = 2
    url = "/api/fatherassets/add/";
    cartel ="Guardado Correctamente";

    if (option == OPTION_EDIT){
        url="/api/fatherassets/edit/";
        cartel="Actualizado Correctamente";
    }


    json= {
        "item":{
                "id": id,
                "asset_id": asset_id,
                "contract": contracts,
                "arrival_date": arrival_date,
                "duration": duration
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
                window.location.href = "/fatherassets/";
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