

$( document ).ready(function() {

    var redirectionrule_id = 0;
    var country             = 0;
    var cableoperator       = 0;
    var rule                = "";

    var publicar            = false;
    var message             = "";
    var URL                 = "";


    function getForm(){
        redirectionrule_id = $('#redirectionrule_id').val();
        country             = $('#country').val();
        cableoperator       = $('#cableoperator').val();
        rule                = $('#rule').val();
        URL                 = '/redirectionrules/add/';

        if (redirectionrule_id > 0 ){
            URL                 = '/redirectionrules/edit/' + redirectionrule_id + '/';
        }
    }


    function validate(){
        check = true;
        if (country == 0 && cableoperator == 0){
            message = 'Debe Seleccionar Pais o Cable Operador ';
            check = false;
        }

        if (!check){
            alert(message);
        }
        return check;
    }


    function proccess(){
        getForm();
        if(validate()){

            //Setear objeto JSON
            json_data = {
                "redirectionrules":{
                        "redirectionrule_id": redirectionrule_id,
                        "cableoperator": cableoperator,
                        "country":       country,
                        "rule":          rule,
                        "publicar":      publicar
                        }
             };

            $.ajax({
                url: URL,
                dataType: 'json',
                type: 'POST',
                contentType: "application/json; charset=utf-8",
                data: JSON.stringify( json_data ),
                success: function(response){

                        console.log(response);
                        window.location="/redirectionrules/";
                    },
                error:function(request, status, error){
                    alert(request.responseText);
                }
            });

          }
    }

     //ELIMINAR VIDEOLOG POR ID, FUNCION AJAX
    function eliminar(id){
        url = "/redirectionrules/delete/";
        json_data= {
                "id": id
        };

        $.ajax({
            url: url,
            dataType: 'json',
            type: 'POST',
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify( json_data ),
            success: function(response){
                    $("tr[data='"+id+"']").fadeOut(1000);
                },
            error:function(request, status, error){
                alert(request.responseText);
            }
        });

    }






    //Handle Events
    $("#grabar").click(function(){
        publicar = false;
        proccess();

    });

    $("#grabarypublicar").click(function(){
        publicar = true;
        proccess();
    });

    $("button[name='btndelete']").click(function(){
        var data = $(this).attr("data");
        eliminar(data);
    });


});