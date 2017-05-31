
<script>

$(document).ready(function(){
    $('#TabAnswers').DataTable();
     $('#viewscope_country__row .w2p_fc').html('<select id="countryopt" name="countryopt" onchange="showcountryValue(this.value)"> <option value="{{=form.vars.country}}">{{=form.vars.country}}</option>   </select>');
   $('#viewscope_subdivision__row .w2p_fc').html('<select id="subdivopt" name="subdivopt" onchange="showsubdivValue(this.value)"> <option value="{{=form.vars.subdivision}}">{{=form.vars.subdivision}}</option> </select>');

    $('#viewscope_continent__row').hide();
    $('#viewscope_country__row .w2p_fw').hide();
    $('#viewscope_subdivision__row .w2p_fw').hide();

    if($("[id='scope1 Global']").prop('checked'))
            {$('#viewscope_continent__row').hide();
            $('#viewscope_country__row').hide();
            $('#viewscope_subdivision__row').hide()};
    if($("[id='scope2 Continental']").prop('checked'))
            {$('#viewscope_continent__row').show();
            $('#viewscope_country__row').hide();
            $('#viewscope_subdivision__row').hide()};
    if($("[id='scope3 National']").prop('checked'))
            {$('#viewscope_continent__row').show();
            $('#viewscope_country__row').show();
            $('#viewscope_country__row .w2p_fw').hide();
            $('#viewscope_subdivision__row').hide()};
     if($("[id='scope4 Local']").prop('checked'))
            {$('#viewscope_continent__row').show();
            $('#viewscope_country__row').show();
            $('#viewscope_country__row .w2p_fw').hide();
            $('#viewscope_subdivision__row').show();
            $('#viewscope_subdivision__row .w2p_fw').hide()};


    if ($('#viewscope_showscope').prop('checked')==false){
       $('#viewscope_view_scope__row').hide();
       $('#viewscope_continent__row').hide();
       $('#viewscope_country__row').hide();
       $('#viewscope_subdivision__row').hide();};
    if ($('#viewscope_showcat').prop('checked')==false){
        $('#viewscope_category__row').hide();};


   $('#viewscope_showcat').change(function(){
              $('#viewscope_category__row').toggle()});

   $('#viewscope_showscope').change(function(){
            if($('#viewscope_showscope').prop('checked')==false) {
                $('#viewscope_view_scope__row').hide();
                $('#viewscope_continent__row').hide();
                $('#viewscope_country__row').hide();
                $('#viewscope_subdivision__row').hide();}
            else
                {$('#viewscope_view_scope__row').show();
            if($("[id='scope3 National']").prop('checked'))
            {$('#viewscope_continent__row').show();
            $('#viewscope_country__row').show();
            $('#viewscope_subdivision__row').hide()};
            if($("[id='scope1 Global']").prop('checked'))
            {$('#viewscope_continent__row').hide();
            $('#viewscope_country__row').hide();
            $('#viewscope_subdivision__row').hide()};
            if($("[id='scope2 Continental']").prop('checked'))
            {$('#viewscope_continent__row').show();
            $('#viewscope_country__row').hide();
            $('#viewscope_subdivision__row').hide()};
            if($("[id='scope4 Local']").prop('checked'))
            {$('#viewscope_continent__row').show();
            $('#viewscope_country__row').show();
            $('#viewscope_subdivision__row').show()};}

            });

   $('input[name=scope]').change(function(){
            if($("[id='scope1 Global']").prop('checked'))
            {$('#viewscope_continent__row').hide();
            $('#viewscope_country__row').hide();
            $('#viewscope_subdivision__row').hide()};
            if($("[id='scope2 Continental']").prop('checked'))
            {$('#viewscope_continent__row').show();
            $('#viewscope_country__row').hide();
            $('#viewscope_subdivision__row').hide()};
            if($("[id='scope3 National']").prop('checked'))
            {$('#viewscope_continent__row').show();
            $('#viewscope_country__row').show();
            $('#viewscope_country__row .w2p_fw').hide();
            $('#viewscope_subdivision__row').hide()};
            if($("[id='scope4 Local']").prop('checked'))
            {$('#viewscope_continent__row').show();
            $('#viewscope_country__row').show();
            $('#viewscope_country__row .w2p_fw').hide();
            $('#viewscope_subdivision__row').show();
            $('#viewscope_subdivision__row .w2p_fw').hide()};
            });

            $('#viewscope_continent ').change(function(){
            $('#countryopt').empty();
            ajax('{{=URL('submit','country')}}', ['continent'], 'countryopt');});

            $('#viewscope_country').change(function(){
            $('#subdivopt').empty();
            ajax('{{=URL('submit','subdivn')}}', ['country'], 'subdivopt');});



});

</script>

