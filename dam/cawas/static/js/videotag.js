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
                    "file": "http://cdnlevel3.zolechamedia.net/" + src + "/mp4/1200/" + src +".mp4",
                });
        }
        p = changeVideo($("#asset_id").val(),"repro1");







        var toSecString = function(val)
        {
            strseg = "";
            strmin = "";
            strformat="";
            min = 0;
            seg = 0;
            if ( val > 60 ) {
                min = Math.round(val / 60);
                seg = Math.round(val % 60);
                console.log(min);
                console.log(seg);
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

        formatTimeList();

        function formatTimeList(){

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


        }



            //AGREGAR TAG
            $("#agregartag").click(function(){
                indexrow = indexrow +1;



                    //Cargar con ajax el contenido de tags y generar el row
                    var tags =listaTags;
                    if(tags.length > 0)
                    {
                        var tdselect = '<td class="tb-cell"><select data-id="'+indexrow+'" class="form-control select2" size="6">';
                        for(d in tags)
                        {
                            tdselect +='<option data="'+tags[d]['id']+'">'+tags[d]['descripcion']+'</option>';
                        }
                        tdselect +='</select></td>';
                    }
                    var rowtag='<tr class="tb-row" data="" data-id="'+indexrow+'">';

                    rowtag+= tdselect;
                    rowtag+= '<td class="tb-cell"><button class="btn-sm btn-default" data-id="'+indexrow+'" name="btnin"><span class="glyphicon glyphicon-play"> </span> In</button></td>';
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
                                alert("El Video no se esta reproduciendo, Esssstupido!");
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
                                alert("El Video no se esta reproduciendo, Esssstupido!");
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
                            alert("Guardado Correctamente");



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