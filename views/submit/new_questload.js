function showsubdivValue(newValue)
{
	document.getElementById("activity_subdivision").value=newValue;
}

var qtext ='';

$(document).ready(function(){
   $(" body").tooltip({selector: '[data-toggle = popover]'});
   $('#activity_subdivision__row .help-block').html('<select id="subdivopt" name="subdivopt" onchange="showsubdivValue(this.value)"> <option value="Unspecified">Unspecified</option> </select>');
    /*$('#activity_country').hide();*/
    $('#activity_subdivision').hide();
    
            $('#activity_country').change(function(){
            $('#subdivopt').empty();
            ajax('{{=URL('submit','subdivn')}}', ['country'], 'subdivopt');
            document.getElementById("activity_subdivision").value="Unspecified";
            });

            $('#activity_questiontext').blur(function () {
                qtext = $('#activity_questiontext').val();
            });

            $('#myform').submit(function () {
                $('#itemload').hide();
                console.log('I ran on submit' + d32py.formaction);
                if (d32py.formaction=='New') {
                        addnode(qtext, d32py.xpos, d32py.ypos);
                    }
                    else {
                        amendnode(qtext);
                    }

                $("html, body").animate({scrollTop: 0}, "slow")
            });
            });