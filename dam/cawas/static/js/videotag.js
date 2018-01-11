 jQuery(document).ready(function($)
        {
            var indexrow = 0;
            $(".form-control.select2").select2({placeholder: "Despliega la lista"});
            $("#agregartag").click();




            //Funcion Agregar Row
            $("#agregartag").click(function(){
                indexrow = indexrow +1;
                    //Cargar con ajax el contenido de tags y generar el row
                    var tags =listaTags;
                    if(tags.length > 0)
                    {
                        var tdselect = '<td class="tb-cell"><select data-id="'+indexrow+'" class="form-control select2" size="6">';
                        for(d in tags)
                        {
                            tdselect +='<option data="'+tags[d]['descripcion']+'">'+tags[d]['descripcion']+'</option>';
                        }
                        tdselect +='</select></td>';
                    }
                    var rowtag='<tr class="tb-row" data-id="'+indexrow+'">';
                    rowtag+= '<td class="tb-cell" >AssetID</td>';
                    rowtag+= tdselect;
                    rowtag+= '<td class="tb-cell"><button class="btn-sm btn-default"><span class="glyphicon glyphicon-play"> </span> In</button></td>';
                    rowtag+='<td data-id="'+indexrow+'" name="inputin" class="tb-cell" data="00:01:01">00:00:00</td>';
                    rowtag+='<td class="tb-cell"><button data-id="'+indexrow+'" class="btn-sm btn-default" name="btnout"><span class="glyphicon glyphicon-stop"> </span> Out</button></td>';
                    rowtag+='<td data-id="'+indexrow+'" name="inputout" class="tb-cell" data="00:03:02" >00:00:00</td>';
                    rowtag+='<td class="tb-cell"></td>';
                    rowtag+= '</tr>';

                    $("#tabletags tr:last").after(rowtag);
                    $(".form-control.select2").select2({placeholder: "Despliega la lista"});

                    //Click en el Boton OUT
                    $("button[name='btnout']").click(function(){

                        var button = $(this);
                        //obtener el DATA-ID seleccionado
                        var dataid= button.attr("data-id");

                        //leer asset id
                        strasset = "select[data-id='"+dataid+"'] option:selected";
                        var asset = $(strasset).attr("data");

                        //leer time in
                        strin = "td[data-id='"+dataid+"'][name='inputin']";
                        var datain = $(strin).attr("data");

                        //leer time out
                        strout = "td[data-id='"+dataid+"'][name='inputout']";
                        var dataout = $(strout).attr("data");

                        if (asset==null){
                            alert("Debe seleccionar un asset");

                        }else{
                            alert("value"+ asset);
                        }

                        //Crear Json


                        //Enviar Json por ajax para guardar el videotag



                        alert("value"+ datain);
                        alert("value"+ dataout);



                    });


                    /*
                    $.ajax({
                            method: "GET",
                            url: "/ajax/tags/",
                            dataType: 'json',
                            contentType: "application/text; charset=utf-8",
                            success: function(data)
                            {
                                var tags =data;
                                if(tags.length > 0)
                                {
                                    var tdselect = '<td class="tb-cell"><select class="form-control select2" size="6">';
                                    for(d in tags)
                                    {

                                        tdselect +='<option data-id="'+d['id']+'" value="'+d['descripcion']+'">'+d['descripcion']+'</option>';
                                    }
                                    alert(d["id"]);
                                    tdselect +='</select></td>';
                                }
                                var rowtag='<tr class="tb-row" data-id="'+indexrow+'">';
                                rowtag+= '<td class="tb-cell">AssetID</td>';
                                rowtag+= tdselect;
                                rowtag+= '<td class="tb-cell"><button class="btn-sm btn-default"><span class="glyphicon glyphicon-play"> </span> In</button></td>';
                                rowtag+='<td class="tb-cell">00:00:00</td>';
                                rowtag+='<td class="tb-cell"><button class="btn-sm btn-default"><span class="glyphicon glyphicon-stop"> </span> Out</button></td>';
                                rowtag+='<td class="tb-cell">00:00:00</td>';
                                rowtag+='<td class="tb-cell"></td>';
                                rowtag+= '</tr>';

                                $("#tabletags tr:last").after(rowtag);
                                $(".form-control.select2").select2({placeholder: "Despliega la lista"});



                            },
                            error: function(jqXHR, exception)
                            {
                                if(jqXHR.status === 405)
                                {
                                    console.error("METHOD NOT ALLOWED!");
                                }
                            }
                    });
                    */




            });







            /*Detectar evento click */
            $(".btn.btn-xs.btn-default.actualizaritempedido").click(function(){
                    indexrow = indexrow +1;


                    //Armar json
                    var id = $(this).attr("data-id");
                    var select = "input[data-id=" + id + "][name='cantidad']";
                    var cantidad = $(select).val();
                    var json_item = {
                                    "id": id,
                                    "cantidad": cantidad
                                    };

                        $.ajax({
                            method: "POST",
                            url: "",
                            dataType: 'json',
                            data: JSON.stringify( json_item ),
                            success: function(data)
                            {
                                if(data.hasOwnProperty("response") && data.response === "success")
                                {
                                    if(data.hasOwnProperty("item"))
                                    {
                                            var posts = data.item;
                                            if(posts.length > 0)
                                            {
                                                var html = "";
                                                for(d in posts)
                                                {
                                                    html += "<p>" + JSON.stringify(posts[d]) + "</p>";
                                                }
                                                $("#containerPosts").append(html);
                                            }

                                    }
                                    else
                                    {
                                        console.log("POSTS NOT FOUND");
                                    }
                                }
                            },
                            error: function(jqXHR, exception)
                            {
                                if(jqXHR.status === 405)
                                {
                                    console.error("METHOD NOT ALLOWED!");
                                }
                            }
                    });



            });


        });