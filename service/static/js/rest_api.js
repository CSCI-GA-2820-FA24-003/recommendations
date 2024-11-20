$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#recommendation_id").val(res.id);
        $("#recommendation_product_id").val(res.product_id);
        $("#recommendation_recommended_id").val(res.recommended_id);
        $("#recommendation_recommendation_type").val(res.recommendation_type);
        $("#recommendation_status").val(res.status);
        $("#recommendation_like").val(res.like);
        $("#recommendation_dislike").val(res.dislike);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#recommendation_product_id").val("");
        $("#recommendation_recommended_id").val("");
        $("#recommendation_recommendation_type").val("");
        $("#recommendation_status").val("");
        $("#recommendation_like").val("");
        $("#recommendation_dislike").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Recommendation
    // ****************************************

    $("#create-btn").click(function () {

        let product_id = parseInt($("#recommendation_product_id").val()); 
        let recommended_id = parseInt($("#recommendation_recommended_id").val());
        let recommendation_type = $("#recommendation_recommendation_type").val();
        let status = $("#recommendation_status").val();
        // let like = $("#recommendation_like").val();

        let data = {
            "product_id": product_id,
            "recommended_id": recommended_id,
            "recommendation_type": recommendation_type,
            "status": status,
            // "like": like
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/recommendations",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Recommendation
    // ****************************************

    $("#update-btn").click(function () {

        let recommendation_id = $("#recommendation_id").val();
        let product_id = $("#recommendation_product_id").val();
        let recommended_id = $("#recommendation_recommended_id").val();
        let recommendation_type = $("#recommendation_recommendation_type").val();
        let status = $("#recommendation_status").val();
        // let like = $("#recommendation_like").val();

        let data = {
            "product_id": product_id,
            "recommended_id": recommended_id,
            "recommendation_type": recommendation_type,
            "status": status,
            // "like": like
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/recommendations/${recommendation_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Recommendation
    // ****************************************

    $("#retrieve-btn").click(function () {

        let recommendation_id = $("#recommendation_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/recommendations/${recommendation_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Recommendation
    // ****************************************

    $("#delete-btn").click(function () {

        let recommendation_id = $("#recommendation_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/recommendations/${recommendation_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Recommendation has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Like a Recommendation
    // ****************************************

    $("#like-btn").click(function () {

        let recommendation_id = $("#recommendation_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/recommendations/${recommendation_id}/like`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Recommendation has been Liked!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });

    });

    // ****************************************
    // Dislike a Recommendation
    // ****************************************

    $("#dislike-btn").click(function () {

        let recommendation_id = $("#recommendation_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/recommendations/${recommendation_id}/dislike`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Recommendation has been Disliked!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });

    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#recommendation_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for a Recommendation
    // ****************************************

    $("#search-btn").click(function () {

        let product_id = $("#recommendation_product_id").val();
        let recommended_id = $("#recommendation_recommended_id").val();
        let recommendation_type = $("#recommendation_recommendation_type").val();
        let status = $("#recommendation_status").val();

        let queryString = ""

        if (product_id) {
            queryString += 'product_id=' + product_id
        }
        if (recommended_id) {
            queryString += '&recommended_id=' + recommended_id
        }
        if (recommendation_type) {
            queryString += '&recommendation_type=' + recommendation_type
        }
        if (status) {
            queryString += '&status=' + status
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/recommendations?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Product ID</th>'
            table += '<th class="col-md-2">Recommended ID</th>'
            table += '<th class="col-md-2">Recommendation Type</th>'
            table += '<th class="col-md-2">Status</th>'
            table += '<th class="col-md-2">Like</th>'
            table += '<th class="col-md-2">Dislike</th>'
            table += '</tr></thead><tbody>'
            let firstRecommendation = "";
            for(let i = 0; i < res.length; i++) {
                let recommendation = res[i];
                table +=  `<tr id="row_${i}"><td>${recommendation.id}</td><td>${recommendation.product_id}</td><td>${recommendation.recommended_id}</td><td>${recommendation.recommendation_type}</td><td>${recommendation.status}</td><td>${recommendation.like}</td><td>${recommendation.dislike}</td></tr>`;
                if (i == 0) {
                    firstRecommendation = recommendation;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstRecommendation != "") {
                update_form_data(firstRecommendation)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})
