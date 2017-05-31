$( document ).ready(function() {

var targetUrl="";
function showmsg(){
        $("#msgconfirm").dialog({
          resizable: false,
          height: "auto",
          width: 400,
          modal: true,
          //position: "center",
          buttons : {
            "Ok" : function() {
              window.location.href = targetUrl;
            },
            "Cancelar" : function() {
              $(this).dialog("close");
            }
          }
        });
        $("#dialog").dialog("open");
}

//Desactivar chica, confirmacion
$(".btn-warning.btn.tb-btn.despublicar").click(function(e) {
        e.preventDefault();
        targetUrl = $(this).attr("href");
        $("#msgconfirm").text("Confirma Que Desea Despublicar el Contenido?");
        showmsg();
  });



//Desactivar chica, confirmacion
$(".btn-warning.btn.tb-btn.desactivar").click(function(e) {
        e.preventDefault();
        targetUrl = $(this).attr("href");
        $("#msgconfirm").text("Confirma Que Desea Desactivar el Contenido?");
        showmsg();
  });

//Publicar Chica
$(".btn-success.btn.tb-btn.publicar").click(function(e) {
        e.preventDefault();
        targetUrl = $(this).attr("href");
        $("#msgconfirm").text("Confirma Que Desea Publicar el Contenido?");
        showmsg();
  });

//Eliminar Contenido
$(".btn-danger.btn.tb-btn.eliminar").click(function(e) {
        e.preventDefault();
        $("#msgconfirm").text("Confirma Que Desea Eliminar el Contenido?");
        showmsg();
  });


});