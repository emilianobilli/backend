

// CAPTURAR VALOR EN VARIABLES
var asset_Id = $('#movieID').val();
var original_Title = $('#orginalTitle').val();
var canal_selected = $('#canalSelect option:selected');
var pornstars_selected = [];
var categories_selected = [];
var paises_selected = [];
var director_selected = $('#director').val();
var elenco_selected = $('#elenco').val();
var display_runtime = $('#runtime').val();
var year_selected = $('#releaseYear').val();
var publicar = $('#publicar').val();

 //search_to_girls
if ( $('#search_girls_to option').length > 0 )
{
    pornstars_selected = [];
    $('#search_girls_to option').each(function(){
       var asset_id_aux = $(this).attr("value"); //val();
       if (asset_id_aux != null){
           pornstars_selected.push(asset_id_aux);
       }
    })
}

//search_category_to
if ( $('#search_category_to option').length > 0 )
{
    categories_selected = [];
    $('#search_category_to option').each(function(){
       var asset_id_aux = $(this).attr("value"); //val();
       if (asset_id_aux != null){
           categories_selected.push(asset_id_aux);
       }
    })
}

//search_to_paises - No es obligatorio
if ( $('#search_paises_to option').length > 0 )
{
    paises_selected = [];
    $('#search_paises_to option').each(function(){
       var asset_id_aux = $(this).attr("value"); //val();
       if (asset_id_aux != null){
           paises_selected.push(asset_id_aux);
       }
    })

}