$(document).ready(function() {


      $("#spinner").bind("ajaxSend", function() {
                $(this).show();
      }).bind("ajaxStop", function() {
                $(this).hide();
      }).bind("ajaxError", function() {
                $(this).hide();
      });

       $('#pdf_input').click(function() {
                $('#pdf_button').click();
            });
    
    $('#loading').hide()

    $('#pdf_button').click(function() {
        console.log('pdf button is clicked');
        var prompt = $('#article_input').val();
        //var connotation_inc = $('#connotation_inc').val(); //NEW
        console.log('text gen input value is');
        console.log(prompt);
        var url = 'science_post'

        $('#loading').show();

        $.post(
            url,
            {
                'prompt': prompt,
            },
            function(data) {
                console.log(data);
                var list_html = "";
                for (var t = 0; t < data['generated_ls'].length; t++) {
                    list_html += "<li style='list-style-type: none' id='generated_item_" + t + "'>" + data['generated_ls'][t] + "</li>";
                    $("#generated_ul").html(list_html);
                }

                $("#loading").hide();
            }

        ).fail(function() {
          alert( "There is something unexpected happened. Email hello@ai-camp.org to report your findings." );
        });

    });

    $()
});