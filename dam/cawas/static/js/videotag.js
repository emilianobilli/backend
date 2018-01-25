 jQuery(document).ready(function($)
        {

            //variables

            var indexrow = 0;
            var button;
            var dataid;
            var asset;
            var dataout;
            var datain;
            var json_data;
            var asset_id;
            var timein;
            var timeout;
            var tag_id;
            var url;
            var timeinteger_in;
            var timeinteger_out;
            var videolog_id;
            var p;

        $(".form-control.select2").select2({placeholder: "Despliega la lista"});

         function changeVideo(src, divId){// para cambiar lo que reproduce el player de acuerdo al ID de la lista.
               return jwplayer(divId).setup({
                    file: "http://cdnlevel3.zolechamedia.net/" + src + "/hls/" + src +".m3u8",
                    aspectratio: "16:9",
                    width: '100%',
                });
        }
        p = changeVideo($("#asset_id").val(),"pepito");







        var toSecString = function(val)
        {
            strseg = "";
            strmin = "";
            strformat="";
            min = 0;
            seg = 0;
            if ( val > 60 ) {
                min = Math.floor(val / 60);
                seg = Math.floor(val % 60);

            }else{
                min = 0;
                seg = val;
            }
            strmin = min.toString();
            strseg = seg.toString();

            if (min < 10 ){
                strmin = "0" + min.toString();
            }
            if (seg < 10){
                strseg = "0" + seg.toString();
            }
            strformat = strmin.toString() + ":" + strseg.toString();
            return strformat;

        }

        applyFunctionsList();



        function applyFunctionsList(){

            //Lee el valor de Data, lo formatea en minutos y segundos, luego lo asigna a la propiedad HTML
            $("td[name='inputin']").each(function() {
                var tdin = $(this);
                timeinteger_in = tdin.attr("data");
                tdin.html(toSecString(timeinteger_in));
            });

            $("td[name='inputout']").each(function() {
                var tdout =$(this);
                timeinteger_out = tdout.attr("data");
                tdout.html(toSecString(timeinteger_out));
            });

            //Asigna Efecto Hover en la primer columana
            $("td[name='tdselect']").hover(function(){
                $(this).addClass('hover'); // 500 is ms to animate class transition
                }, function()  //mouseout
                {
                  $(this).removeClass('hover');
            });

            //Lleva la reproduccion del video a la posicion del tag seleccionado
            $("td[name='tdselect']").click(function(){
                var td = $(this);
                var dataid = td.attr("data-id");
                //leer el tiempo
                var strselector = "td[name='inputin'][data-id="+dataid+"]";
                var timein = $(strselector).attr("data");
                p.seek(timein);
            });

        }



            //AGREGAR TAG
            $("#agregartag").click(function(){
                indexrow = indexrow +1;
                    //Cargar con ajax el contenido de tags y generar el row
                    var tags =listaTags;
                    if(tags.length > 0)
                    {
                        var tdselect = '<td class="tb-cell" name="tdselect" data-id="'+indexrow+'">';
                        tdselect += '<select data-id="'+indexrow+'" class="form-control select2" size="6">';
                        for(d in tags)
                        {
                            tdselect +='<option data="'+tags[d]['id']+'">'+tags[d]['descripcion']+'</option>';
                        }
                        tdselect +='</select></td>';
                    }
                    var rowtag='<tr class="tb-row" data="" data-id="'+indexrow+'">';

                    rowtag+= tdselect;
                    rowtag+= '<td class="tb-cell" ><button class="btn-sm btn-default" data-id="'+indexrow+'" name="btnin"><span class="glyphicon glyphicon-play"> </span> In</button></td>';
                    rowtag+='<td data-id="'+indexrow+'" name="inputin" class="tb-cell" data="">00:00</td>';
                    rowtag+='<td class="tb-cell"><button data-id="'+indexrow+'" class="btn-sm btn-default" name="btnout"><span class="glyphicon glyphicon-stop"> </span> Out</button></td>';
                    rowtag+='<td data-id="'+indexrow+'" name="inputout" class="tb-cell" data="">00:00</td>';
                    rowtag+='<td class="tb-cell"><button style="display:none" data="" data-id="'+indexrow+'" name="btndelete" class="btn-md btn-danger" ><span class="glyphicon glyphicon-trash"></span>Del  </button></td>';
                    rowtag+= '</tr>';

                    $("#tabletags tr:last").after(rowtag);
                    $(".form-control.select2").select2({placeholder: "Despliega la lista"});




                    //CLICK IN
                    $("button[name='btnin']").click(function(){
                            var buttonin = $(this);
                            var dataid= buttonin.attr("data-id");

                            var tdin = $("td[name='inputin'][data-id='"+dataid+"']");

                            var timeinteger_in = Math.round(p.getPosition());
                            if (timeinteger_in ==0){
                                alert("El Video no se esta reproduciendo!");
                                return false;
                            }
                            tdin.attr("data", timeinteger_in.toString());
                            tdin.html(toSecString(timeinteger_in));

                    });

                    //CLICK OUT
                    $("button[name='btnout']").click(function(){
                        var button = $(this);
                        var index = button.attr("data-id");
                        //Enviar Json por ajax para guardar el videotag

                        var timeinteger_out = Math.round(p.getPosition());
                        if (timeinteger_out ==0){
                                alert("El Video no se esta reproduciendo!");
                                return false;
                            }
                        var tdout = $("td[name='inputout'][data-id='"+index+"']");
                        tdout.attr("data",timeinteger_out.toString());
                        tdout.html(toSecString(timeinteger_out));

                        if(validar(index)){
                            guardar(index);

                        };
                    });





                     //CLICK BOTON DELETE
                    $("button[name='btndelete']").click(function(){
                        var data = $(this).attr("data");
                        deleteVideoLog(data);
                    });


                function validar(index){
                    //leer asset id
                    strasset = "select[data-id='"+index+"'] option:selected";
                    tag_id = $(strasset).attr("data");
                    if (tag_id==null){
                        alert("El Tag es obligatorio.");
                        $("select[data-id='"+index+"']").focus();
                        return false;
                    }

                    //leer time in
                    strin = "td[data-id='"+index+"'][name='inputin']";
                    timein = $(strin).attr("data");
                    if (timein==""){
                        alert("Se debe marcar el tiempo de inicio del Tag (In).");
                        $("button[name='btnin'][data-id='"+index+"']").focus();
                        return false;

                    }
                    //leer time out
                    strout = "td[data-id='"+index+"'][name='inputout']";
                    timeout = $(strout).attr("data");
                    if (timeout==""){
                        alert("Se debe marcar el tiempo de inicio del Tag (Out).");
                        $(timeout).focus();
                        return false;
                    }
                    if (parseInt(timeout) <= parseInt(timein)){
                        alert("Time In no puede ser mayor a Time Out.");
                        return false;
                    }

                    return true;

                }




    });

    //Fin de Click en Agrear Tag

        //AGREGAR BOTON DELETE
        function addButtonDelete(index, id ){
            var btndelete = $("button[name='btndelete'][data-id='"+index+"']");
            //id es el valor de la PK dentro de la tabla VideoLog
            btndelete.attr("data",id);
            btndelete.show();

            // se actualiza el campo de la fila para poder hacer el HIDE
            var tr = $("tr[data-id='"+index+"']");
            tr.attr("data",id);
        }

        function removeClassSelect2(index, id){
            //Quitar clase Select2 de la columna tag
            var strselector = "select[data-id='"+index+"'] option:selected";
            //var tag_id   = $(strselector).attr("data");
            var tag_name = $(strselector).html();
            //var strhtml = tag_id + " - " + tag_name;
            strselector = "td[name='tdselect'][data-id='"+index+"']";
            $(strselector).html(tag_name);

        }


        function guardar(index){

                asset_id = $("#asset_id").val();

                url = "/videologs/add/"+ asset_id +"/"
                json_data= {
                        "tag_id": tag_id,
                        "timein": timein,
                        "timeout": timeout,
                        "asset_id": asset_id
                };

                $.ajax({
                    url: url,
                    dataType: 'json',
                    type: 'POST',
                    contentType: "application/json; charset=utf-8",
                    data: JSON.stringify( json_data ),
                    success: function(response){
                            videolog_id = response.data;
                            //index es el numero de fila
                            //videolog_id es la PK de la tabla videolog
                            addButtonDelete(index, videolog_id)
                            removeClassSelect2(index, videolog_id);
                            applyFunctionsList();
                        },
                    error:function(request, status, error){
                        alert(request.responseText);

                }
                });
            }

            //ELIMINAR VIDEOLOG POR ID, FUNCION AJAX
            function deleteVideoLog(videolog_id){
                url = "/videologs/delete/";
                json_data= {
                        "id": videolog_id
                };

                $.ajax({
                    url: url,
                    dataType: 'json',
                    type: 'POST',
                    contentType: "application/json; charset=utf-8",
                    data: JSON.stringify( json_data ),
                    success: function(response){
                            //alert("Eliminado Correctamente");
                            $("tr[data='"+response.data+"']").fadeOut(1000);
                        },
                    error:function(request, status, error){
                        alert(request.responseText);

                    }
                });

            }





            //CLICK BOTON DELETE
            $("button[name='btndelete']").click(function(){
                var data = $(this).attr("data");
                deleteVideoLog(data);
            });



    });