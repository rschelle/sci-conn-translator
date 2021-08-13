function sleep(milliseconds) {
  const date = Date.now();
  let currentDate = null;
  do {
    currentDate = Date.now();
  } while (currentDate - date < milliseconds);
}

$(document).ready(function() {

    console.log('AI Camp is for the best of the best.')
    //sleep(3000)
    console.log('AI Camp is for the best of the best.')

    $('#text_gen_button').click(async function() {
        console.log('text gen button is clicked');
        var prompt = $('#article_input').val();
        //var connotation_inc = $('#connotation_inc').val(); //NEW
        console.log('text gen input value is');
        console.log(prompt);
        var url = 'science'
        var result_loaded = false

        $('#text_gen_button').prop("disabled",true)
        $('#text_gen_button').html("We are summarizing!...")
      
        console.log('about to call sci_post_thread');
        const data = await fetch(url, {
                                          method:"POST",
                                          headers: {"Content-Type": "application/json", "Accept" : "application/json"},
                                          body: JSON.stringify({prompt: prompt})
                                      })
        console.log("This is data")
        console.log(data)
        const data_json = await data.json();
        let waiting_for_result = true;
        let result_data = [""];
        var test_var = "uniquefjdsaklfdsa"
        console.log("waiting for result")
        while (result_data[0] == "") {
          //result_data = "BAD TEST"
          console.log(result_data)
          sleep(2000);
          const data_2 = await fetch("donttypeme", {
                                          method:"POST",
                                          headers: {"Content-Type": "application/json", "Accept" : "application/json"},
                                          body: JSON.stringify({something:test_var})
                                      })
          const data_2_json = await data_2.json();
          
          result_data = data_2_json["generated_ls"]
          if (result_data[0] != "") {
              console.log("done waiting")
              waiting_for_result = false;
              console.log(result_data)
              console.log('about to parse result');
              console.log(result_data)
              console.log(result_data[0])
              var list_html = "<li style='list-style-type: none' id='generated_item_0'>" + result_data[0] + "</li>";
              $("#generated_ul").html(list_html);
              console.log(list_html)
              console.log("parsed")
              $('#text_gen_button').prop("disabled",false)
              $('#text_gen_button').html("Submit")
          }
        }
          /* $.post(
            url,
            {
                'prompt': prompt,
            },
            function(data) {
                var waiting_for_result = true;
                var result_data = [""];
                var test_var = "unique"
                console.log("waiting for result")
                while (result_data[0] == "") {
                  console.log(result_data)
                  sleep(2000);
                  //waiting_for_result = false;
                  
                  $.post(
                        "donttypeme",
                        {
                          'something': test_var
                        },
                        function(data_2, status_string) {
                          console.log(data_2)
                          console.log(data_2['generated_ls'][0])
                          console.log(status_string)
                          test_var = data_2['generated_ls']
                          result_data = test_var
                        }
                    ).done(function() {
                      console.log("done")
                      if (result_data[0] != "") {
                            console.log("done waiting")
                            waiting_for_result = false;
                            console.log(result_data)
                            console.log('about to parse result');
                            console.log(result_data)
                            console.log(result_data[0])
                            var list_html = "<li style='list-style-type: none' id='generated_item_0'>" + result_data[0] + "</li>";
                            $("#generated_ul").html(list_html);
                            console.log(list_html)
                            console.log("parsed")
                        }
                    })
                }

                //Open the file
                /*
                console.log('about to parse result');
                console.log(result_data)
                console.log(result_data[0])
                var list_html = "<li style='list-style-type: none' id='generated_item_0'>" + result_data[0] + "</li>";
                $("#generated_ul").html(list_html);
                console.log(list_html)
                console.log("parsed") */
//            }
//         ).fail(function() {
//           alert( "There is something unexpected happened. Email hello@ai-camp.org to report your findings." );
//         }); 

    });

    
});