

$( document ).ready(function() {

    var packageprice_id     = 0;
    var country             = 0;
    var price               = 0;
    var currency            = "";
    var package_duration    = 0;
    var rule                = "";

    var publicar            = false;
    var message             = "";
    var URL                 = "";


    function getForm(){
        packageprice_id     = $('#packageprice_id').val();
        country             = $('#country').val();
        price               = $('#price').val();
        currency            = $('#currency').val();
        package_duration    = $('#package_duration').val();
        URL                 = '/packageprices/add/';

        if (packageprice_id > 0 ){
            URL                 = '/packageprices/edit/' + packageprice_id + '/';
        }
    }


    function validate(){
        check = true;
        if (country == 0 ){
            message = 'Debe Seleccionar Pais ';
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
                "data":{
                        "packageprice_id":  packageprice_id,
                        "price":            price,
                        "country":          country,
                        "currency":         currency,
                        "package_duration": package_duration,
                        "publicar":         publicar
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
                        window.location="/packageprices/";
                    },
                error:function(request, status, error){
                    alert(request.responseText);
                }
            });

          }
    }

     //ELIMINAR VIDEOLOG POR ID, FUNCION AJAX
    function eliminar(id){
        url = "/packageprices/delete/";
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

    //Publicar todos los packages price
    function publish(){
        url = "/publish/";

        $.ajax({
            url: url,
            dataType: 'json',
            type: 'POST',
            contentType: "application/json; charset=utf-8",

            success: function(response){
                    alert("Packages Price publicados correctamente");
                },
            error:function(request, status, error){
                alert(request.responseText);
            }
        });

    }





//--------- Handle Events -----------------------------------------------
    $("#grabar").click(function(){
        publicar = false;
        proccess();

    });

    $("#grabarypublicar").click(function(){
        publicar = true;
        proccess();
    });

    $("a[name='btndelete']").click(function(){
        var data = $(this).attr("data");
        eliminar(data);
    });

     $("#btn_publicar").click(function(){
        publish();
    });


});